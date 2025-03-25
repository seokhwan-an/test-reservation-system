import jwt
from django.conf import settings
from jwt import InvalidTokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def generate_tokens_for_user(user):
    token = TokenObtainPairSerializer.get_token(user)
    return {
        "access_token": str(token.access_token),
        "refresh_token": str(token)
    }

def extract_user_id_from_token(token):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,        # simplejwt 기본은 SECRET_KEY로 서명
            algorithms=["HS256"]
        )
        return payload.get("user_id")
    except InvalidTokenError:
        return None