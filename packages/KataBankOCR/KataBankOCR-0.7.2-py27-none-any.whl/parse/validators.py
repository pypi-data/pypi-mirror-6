class Validate():
    "methods that raise errors on invalid input"

    @classmethod
    def type(cls, expected_type, value, name):
        "confirm value of expected type or raise TypeError"
        if not isinstance(value, expected_type):
            message = _build_message(name, value, 'type', expected_type, type(value))
            raise(TypeError(message))

    @classmethod
    def length(cls, expected_length, value, name):
        "confirm value has expected length or raise ValueError"
        length = len(value)
        if len(value) != expected_length:
            message = _build_message(name, value, 'length', expected_length, len(value))
            raise(ValueError(message))

    @classmethod
    def composition(cls, allowed_components, value, name):
        "validate value composed only of allowed components"
        for index, element in enumerate(value):
            if element not in allowed_components:
                message = '%s "%s" contains unexpected element "%s" at index %d'
                message = message % (name, value, element, index)
                raise(TypeError(message))

def _build_message(name, value, error, expected, found):
    message = '%s "%s" of unexpected %s. Expected:%s. Found:%s.'
    return message % (name, value, error, str(expected), str(found))
