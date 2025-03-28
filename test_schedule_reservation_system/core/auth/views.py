from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSerializer
from .token_utils import generate_tokens_for_user
from drf_spectacular.utils import extend_schema
from .docs import signup_docs, login_docs


class AuthViewSet(ViewSet):

    @extend_schema(**signup_docs)
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '회원가입 성공'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(**login_docs)
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = generate_tokens_for_user(user)

        response = Response({
            "message": "로그인 성공",
            "access_token": tokens['access_token']
        })

        response.set_cookie("refresh_token", tokens['refresh_token'], httponly=True)
        return response
