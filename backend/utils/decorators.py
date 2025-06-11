from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models.user import User

def token_required(fn):
    """A decorator to protect routes with JWT and pass the user object."""
    @wraps(fn)
    def decorator(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(msg="User not found"), 404
        # Pass the user object to the decorated route function
        return fn(user, *args, **kwargs)
    return decorator

def login_required(fn):
    """A decorator to protect routes with JWT without passing the user object."""
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                 return jsonify(msg="Token is valid, but user not found."), 404
        except Exception as e:
            return jsonify(msg=f"JWT verification failed: {str(e)}"), 401
        
        return fn(*args, **kwargs)
    return decorator

def admin_required():
    """A decorator factory that requires admin role."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            # This decorator does not pass the user object,
            # but checks for admin role.
            if user and user.role == 'admin':
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins access required"), 403
        return decorator
    return wrapper 