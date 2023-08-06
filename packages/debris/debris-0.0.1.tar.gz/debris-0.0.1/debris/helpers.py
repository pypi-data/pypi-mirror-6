def call(_callable, *args, **kwargs):
    return _callable(*args, **kwargs) if hasattr(_callable, "__call__") else _callable

def callattr(cls, _call, *args, **kwargs):
    if not _call:
        return _call
    elif hasattr(_call, "__call__"):
        return _call(*args, **kwargs)
    else:
        return getattr(cls, _call)(*args, **kwargs)
