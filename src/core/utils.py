from graphql_jwt.settings import jwt_settings
from calendar import timegm
from datetime import datetime
from django.contrib.auth import get_user_model

def jwt_payload(user, context=None):
    """
    Create the JWT payload with user ID as the primary identifier
    """
    print("Custom JWT payload handler called!")
    
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA,
    }

    if jwt_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(datetime.utcnow().utctimetuple())

    if jwt_settings.JWT_AUDIENCE is not None:
        payload['aud'] = jwt_settings.JWT_AUDIENCE

    if jwt_settings.JWT_ISSUER is not None:
        payload['iss'] = jwt_settings.JWT_ISSUER

    return payload

def get_user_by_natural_key(user_id):
    """
    Get user by ID from the JWT payload
    This function name must match what's in GRAPHQL_JWT settings
    """
    UserModel = get_user_model()
    try:

        print("bang", user_id, UserModel.objects.get(id=user_id))
        return UserModel.objects.get(id=user_id)
    except (TypeError, ValueError, UserModel.DoesNotExist):
        print(f"Failed to find user with ID: {user_id}")
        return None