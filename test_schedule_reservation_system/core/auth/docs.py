# core/docs/auth_docs.py

from drf_spectacular.utils import OpenApiTypes, OpenApiExample
from .serializers import (
    SignupSerializer,
    LoginSerializer
)

signup_docs = {
    "summary": "회원가입",
    "description": "사용자 회원가입을 진행합니다.",
    "request": SignupSerializer,
    "examples": [
        OpenApiExample(
            name="회원가입 요청 예시",
            value={
                "username": "newuser",
                "password": "securepass123",
                "is_staff": False
            }
        )
    ],
    "responses": {
        201: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
}

login_docs = {
    "summary": "로그인",
    "description": "사용자 로그인을 통해 액세스 토큰과 리프레시 토큰을 발급받습니다.",
    "request": LoginSerializer,
    "examples": [
        OpenApiExample(
            name="로그인 요청 예시",
            value={
                "username": "newuser",
                "password": "securepass123"
            }
        ),
        OpenApiExample(
            name="로그인 응답 예시",
            value={
                "message": "로그인 성공",
                "access_token": "<access_token>"
            },
            response_only=True
        )
    ],
    "responses": {
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
}
