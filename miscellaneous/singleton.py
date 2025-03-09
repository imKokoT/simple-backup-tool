
class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
            if hasattr(cls, 'onInstanceCreated') and callable(getattr(cls, 'onInstanceCreated')):
                cls.onInstanceCreated()
        return cls.__instances[cls]
