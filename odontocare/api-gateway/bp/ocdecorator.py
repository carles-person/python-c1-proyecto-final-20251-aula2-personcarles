"""
Docstring for odontocare.api-gateway.bp.ocdecorator
"""


from functools import wraps
def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        pass

def require_role(role_name,f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        pass
    
