import re

def one_of(*args):
    if len(args) == 1 and isinstance(args[0], list):
        items = tuple(args[0])
    else:
        items = args

    """Validates that the field value is in the given list."""
    def validate(value):
        if not value in items:
            return "'{0}' is not in the list {1}".format(value, items)
    return validate


def gte(min_value):
    def validate(value):
        if value < min_value:
            return "{0} is less than the minimum value of {1}".format(value, min_value)
    return validate


def lte(max_value):
    def validate(value):
        if value > max_value:
            return "{0} is greater than the maximum value of {1}".format(value, max_value)
    return validate


def gt(gt_value):
    def validate(value):
        if value <= gt_value:
            return "Value must be greater than {0}".format(gt_value)
    return validate


def lt(lt_value):
    def validate(value):
        if value >= lt_value:
            return "Value must be less than {0}".format(lt_value)
    return validate


def between(min_value, max_value):
    def validate(value):
        if value < min_value:
            return "{0} is less than the minimum value of {1}".format(
                value, min_value)
        if value > max_value:
            return "{0} is greater than the maximum value of {1}".format(
                value, max_value)
    return validate


def length(min=None, max=None):
    def validate(value):
        if min and len(value) < min:
            return "String must be at least {0} characters in length".format(min)
        if max and len(value) > max:
            return "String must be at most {0} characters in length".format(max)
    return validate


def match(pattern):
    regex = re.compile(pattern)

    def validate(value):
        if not regex.match(value):
            return "String must match regex"
    return validate

def is_email():
    # Stolen from Django
    regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
        r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$)'  # domain
        r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)
    
    def validate(value):
        if not regex.match(value):
            return "{0} is not a valid email address".format(value)
    return validate

def is_url():
    # Stolen from Django
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def validate(value):
        if not regex.match(value):
            return "{0} is not a valid URL".format(value)
    return validate
