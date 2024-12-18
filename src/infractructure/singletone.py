class SingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            instance = super().__call__(*args, **kwargs)
            cls._instance = instance
        return cls._instance
