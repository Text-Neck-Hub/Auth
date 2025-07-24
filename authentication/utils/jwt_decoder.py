import jwt
import os


def extract_uid_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token,  os.environ.get(
            'SECRET_KEY'), algorithms=[os.environ.get('JWT_ALGORITHM', 'HS256')])

        return decoded.get("uid")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.DecodeError:
        return None
