
__all__ = ["RequestError", "AccessError", "ObjectNotFound", ]

# 400
class RequestError(Exception):
    pass
    
# 401
class AccessError(Exception):
    pass
    
# 402-499
class ObjectNotFound(Exception):
    pass
    
