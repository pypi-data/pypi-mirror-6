from document import Document
from copy import deepcopy
from bson import ObjectId
from middleware import MiddlewareRegistrar
import re
import types


OBJECTIDEXPR = re.compile(r"^[a-fA-F0-9]{24}$")

def deep_merge(source, dest):
    """Deep merges source dict into dest dict."""
    for key, value in source.iteritems():
        if key in dest:
            if isinstance(value, dict) and isinstance(dest[key], dict):
                deep_merge(value, dest[key])
                continue
            elif isinstance(value, list) and isinstance(dest[key], list):
                for item in value:
                    if item not in dest[key]:
                        dest[key].append(item)
                continue
        dest[key] = value


class ModelState:
    """Valid lifecycle states which a given Model instance may occupy."""
    NEW = 1
    PERSISTED = 2
    DELETED = 3


class NotFoundException(Exception):
    """Exception used to indicate that a requested record could not be
    found."""
    def __init__(self, collection, id):
        self._collection = collection
        self._id = id

    def __str__(self):
        return "{} {} not found".format(self._collection.name, self._id)


class ScopeBuilder(object):
    """A helper class used to build query scopes. This class is provided with a
    list of scope functions (all of which return query args) which can then
    be chained together using this builder to build up more complex queries."""

    @classmethod
    def unpack_scope(cls, scope):
        """Unpacks the response from a scope function. The function should return
        either a query, a query and a projection, or a query a projection and
        an query options hash."""
        query = {}
        projection = {}
        options = {}

        if isinstance(scope, tuple):
            if len(scope) > 3:
                raise ValueError("Invalid scope")
            if len(scope) >= 1:
                query = scope[0]
            if len(scope) >= 2:
                projection = scope[1]
            if len(scope) == 3:
                options = scope[2]
        elif isinstance(scope, dict):
            query = scope
        else:
            raise ValueError("Invalid scope")

        return query, projection, options


    @classmethod
    def register_fn(cls, f):
        """Registers a scope function on this builder."""
        def inner(self, *args, **kwargs):
            try:
                query, projection, options = cls.unpack_scope(f(*args, **kwargs))
                new_query = deepcopy(self.query)
                new_projection = deepcopy(self.projection)
                new_options = deepcopy(self.options)
                deep_merge(query, new_query)
                new_projection.update(projection)
                new_options.update(options)
                return ScopeBuilder(self.model, self.fns, new_query,
                    new_projection, new_options)
            except ValueError:
                raise ValueError("Scope function \"{}\ returns an invalid scope".format(f.__name__))

        setattr(cls, f.__name__, inner)


    def __init__(self, model, fns, query={}, projection={}, options={}):
        self.fns = fns
        self.model = model
        self.query = query
        self.projection = projection
        self.options = options
        for fn in fns:
            self.register_fn(fn)

    def __getitem__(self, index):
        """Implementation of the iterator __getitem__ method. This allows the
        builder query to be executed and iterated over without a separate call
        to `execute()` being needed."""
        if not hasattr(self, "in_progress_cursor"):
            self.in_progress_cursor = self.execute()
        return self.in_progress_cursor[index]


    def execute(self):
        """Executes the currently built up query."""
        return self.model.find(self.query, self.projection or None, **self.options)



class Model(Document):
    """
    Model base class on which all specific user model classes subclass.

    ** Do not attempt to subclass Model directly. **

    Instead use mongothon.create_model which will ensure the model
    subclass is correctly constructed with the appropriate collection
    and schema dependencies.
    """

    middleware_registrar = MiddlewareRegistrar()

    def __init__(self, inital_doc=None, initial_state=ModelState.NEW):
        self._state = initial_state
        super(Model, self).__init__(inital_doc)

    def _create_working(self):
        working = deepcopy(self)
        self.schema.apply_defaults(working)
        return working

    @classmethod
    def _ensure_object_id(cls, id):
        """Checks whether the given id is an ObjectId instance, and if not wraps it."""
        if isinstance(id, ObjectId):
            return id

        if isinstance(id, basestring) and OBJECTIDEXPR.match(id):
            return ObjectId(id)

        return id

    @classmethod
    def _id_spec(cls, id):
        return {'_id': cls._ensure_object_id(id)}

    def is_new(self):
        """Returns true if the current model instance is new and has yet to be
        persisted to the underlying Mongo collection."""
        return self._state == ModelState.NEW

    def is_persisted(self):
        """Returns true if the model instance exists in the database."""
        return self._state == ModelState.PERSISTED

    def is_deleted(self):
        """Returns true if the model instance was deleted from the database."""
        return self._state == ModelState.DELETED

    def validate(self):
        """Validates this model against the schema with which is was constructed.
        Throws a ValidationException if the document is found to be invalid."""
        self._do_validate(self._create_working())

    def _do_validate(self, document):
        self.middleware_registrar.apply('before_validate', document)
        self.schema.validate(document)
        self.middleware_registrar.apply('after_validate', document)

    def apply_defaults(self):
        """Apply schema defaults to this document."""
        self.schema.apply_defaults(self)

    def save(self, *args, **kwargs):
        # Create a working copy of ourselves and validate it
        working = self._create_working()
        self._do_validate(working)

        # Apply before save middleware
        self.middleware_registrar.apply('before_save', working)

        # Attempt to save
        self.collection.save(working, *args, **kwargs)
        self._state = ModelState.PERSISTED

        # Apply after save middleware
        self.middleware_registrar.apply('after_save', working)

        # On successful completion, update from the working copy
        self.populate(working)

    @classmethod
    def insert(cls, *args, **kwargs):
        cls.collection.insert(*args, **kwargs)

    def update_instance(self, *args, **kwargs):
        return self.__class__.update({'_id': self['_id']}, *args, **kwargs)

    @classmethod
    def update(cls, *args, **kwargs):
        return cls.collection.update(*args, **kwargs)

    def __getattribute__(self, name):
        if name == 'update':
            return lambda *args, **kwargs: dict.update(self, *args, **kwargs)
        return super(Model, self).__getattribute__(name)

    def remove(self, *args, **kwargs):
        self.collection.remove(self['_id'], *args, **kwargs)
        self._state = ModelState.DELETED

    @classmethod
    def count(cls):
        return cls.collection.count()

    @classmethod
    def find_one(cls, *args, **kwargs):
        return cls(cls.collection.find_one(*args, **kwargs),
                   initial_state=ModelState.PERSISTED)

    @classmethod
    def find(cls, *args, **kwargs):
        return CursorWrapper(cls.collection.find(*args, **kwargs), cls)

    @classmethod
    def find_by_id(cls, id):
        """
        Finds a single document by it's ID. Throws a
        NotFoundException if the document does not exist (the
        assumption being if you're got an id you should be
        pretty certain the thing exists)
        """
        obj = cls.find_one(cls._id_spec(id))
        if not obj:
            raise NotFoundException(cls.collection, id)
        return obj

    def reload(self):
        """Reloads the current model's data from the underlying
        database record, updating it in-place."""
        self.populate(self.collection.find_one(self.__class__._id_spec(self['_id'])))

    @classmethod
    def before_save(cls, middleware_func):
        """Registers a middleware function to be run before every instance
        of the given model is saved, after any before_validate middleware.
        """
        cls.middleware_registrar.register('before_save', middleware_func)

    @classmethod
    def after_save(cls, middleware_func):
        """Registers a middleware function to be run after every instance
        of the given model is saved.
        """
        cls.middleware_registrar.register('after_save', middleware_func)

    @classmethod
    def before_validate(cls, middleware_func):
        """Registers a middleware function to be run before every instance
        of the given model is validated.
        """
        cls.middleware_registrar.register('before_validate', middleware_func)

    @classmethod
    def after_validate(cls, middleware_func):
        """Registers a middleware function to be run after every instance
        of the given model is validated.
        """
        cls.middleware_registrar.register('after_validate', middleware_func)

    @classmethod
    def class_method(cls, f):
        """Decorator which dynamically binds class methods to the model for later use."""
        setattr(cls, f.__name__, types.MethodType(f, cls))

    @classmethod
    def instance_method(cls, f):
        """Decorator which dynamically binds instance methods to the model."""
        setattr(cls, f.__name__, f)

    @classmethod
    def scope(cls, f):
        """Decorator which can dynamically attach a query scope to the model."""
        if not hasattr(cls, "scopes"):
            cls.scopes = []

        cls.scopes.append(f)

        def create_builder(self, *args, **kwargs):
            bldr = ScopeBuilder(cls, cls.scopes)
            return getattr(bldr, f.__name__)(*args, **kwargs)

        setattr(cls, f.__name__, types.MethodType(create_builder, cls))


class CursorWrapper(object):
    """
    A wrapper for the standard pymongo Cursor object which ensures all
    objects returned by the cursor's query are wrapped in an instance
    of the given Model class.
    """
    RETURNS_CURSOR = ['rewind', 'clone', 'add_option', 'remove_option',
                      'limit', 'batch_size', 'skip', 'max_scan', 'sort',
                      'hint', 'where']

    def __init__(self, wrapped_cursor, model_class):
        self._wrapped = wrapped_cursor
        self._model_class = model_class

    def __getitem__(self, index):
        return self._model_class(self._wrapped[index], initial_state=ModelState.PERSISTED)

    def __iter__(self):
        return IteratorWrapper(self._wrapped.__iter__(), self._model_class)

    def __getattr__(self, name):
        attr = getattr(self._wrapped, name)
        if name in self.RETURNS_CURSOR:
            def attr_wrapper(*args, **kwargs):
                return CursorWrapper(attr(*args, **kwargs), self._model_class)

            return attr_wrapper
        return attr


class IteratorWrapper(object):
    """
    Wrapper for the iterator object returned by the pymongo cursor. Allows
    CursorWrapper to implement the iterator protocol while still returning
    models.
    """

    def __init__(self, wrapped_iterator, model_class):
        self._wrapped = wrapped_iterator
        self._model_class = model_class

    def next(self):
        return self._model_class(self._wrapped.next(), initial_state=ModelState.PERSISTED)
