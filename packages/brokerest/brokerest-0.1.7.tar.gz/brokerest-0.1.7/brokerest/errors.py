
__all__ = ["RequestError", "IntegrityError", "AccessError", "MethodError", "ObjectNotFound", ]

# 4xx
class RequestError(Exception):
    pass
    
# 400
class IntegrityError(RequestError):
    pass
    
# 401
class AccessError(RequestError):
    pass

# 405
class MethodError(RequestError):
    pass

# 402-499
class ObjectNotFound(RequestError):
    pass
    
