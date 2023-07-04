class Singleton(type):
    _instances = {}

    # Each of the following functions use cls instead of self
    # to emphasize that although they are instance methods of
    # Singleton, they are also *class* methods of a class defined
    # with Singleton
    def __call__(cls, *args, **kwargs):
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        return Singleton._instances[cls]

    def clear(cls):
        try:
            del Singleton._instances[cls]
        except KeyError:
            pass

    def __deepcopy__(cls, instance):
        return instance
