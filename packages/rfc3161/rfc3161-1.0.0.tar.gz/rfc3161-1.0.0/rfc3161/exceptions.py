

class RFC3161Exception(Exception):
    pass

class BaseUnknownValue(RFC3161Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.value)

class UnknownPKIStatusValue(BaseUnknownValue):
    pass

class UnknownPKIFailureInfo(BaseUnknownValue):
    pass

class 
