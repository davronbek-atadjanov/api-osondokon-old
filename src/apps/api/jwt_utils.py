from graphql_jwt.utils import jwt_payload as default_payload

def jwt_payload(user, context=None):
    payload = default_payload(user, context)
    del payload['email']
    
    payload['user_id'] = str(user.id)
    return payload