from inflection import camelize
from document import Document
from model import Model, NotFoundException
from schema import Schema, Mixed, ValidationException

def create_model(schema, collection, class_name=None):
    """
    Main entry point to creating a new mongothon model. Both
    schema and Pymongo collection objects must be provided.

    Returns a new class which can be used as a model class.

    The class name of the model class by default is inferred
    from the provided collection (converted to camel case).
    Optionally, a class_name argument can be provided to
    override this.
    """

    if not class_name:
        class_name = camelize(str(collection.name))
    return type(
        class_name,
        (Model,),
        dict(schema=schema, collection=collection))
