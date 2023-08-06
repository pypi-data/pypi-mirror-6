class Asset:
    __cacheable__ = True
    def __init__(self, value, expires=None):
        self.value = value
