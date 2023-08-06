ResultsDict


class combined(contextmethod):
    def __init__(self, *handlers, **options):
        self.handlers = handlers

    def __call__(self, func):
        handlers = self.handlers
        _method = contextmethod.__call__(self, func)
        results = {}

        def method(self, *args, **kwargs):
            for cls in handlers:
                cls.contextmethods.add(method)
            results[context.name] = _method(self, *args, **kwargs)
            return results

        for handler in handlers:
            for context in handler.contexts:
                name = context.name
                setattr(method, name, getattr(_method, name))
        method.__name__ = _method.__name__
        return method


contextmethod.combined = combined
