from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from ..auth.token_utils import extract_user_id_from_token


class TestSignup(APITestCase):
    def setUp(self):
        self.url = '/api/auth/signup/'

    def test_signup_success(self):
        req = {
            'username': 'newuser',
            'password': 'securepass123',
            'is_staff': 'True'
        }
        res = self.client.post(self.url, req, format='json')

        saved_user = User.objects.filter(username=req['username']).get()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['message'], '회원가입 성공')
        self.assertEqual(saved_user.username, req['username'])
        self.assertTrue(saved_user.check_password(req['password']))
        self.assertEqual(saved_user.is_staff, True)

    def test_signup_missing_fields(self):
        req = {'username': 'noinfo'}
        res = self.client.post(self.url, req, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TestLogin(APITestCase):
    def setUp(self):
        self.url = '/api/auth/login/'
        self.username = "testUser"
        self.password = "1234"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

    def test_login_success(self):
        req = {
            "username": self.username,
            "password": self.password
        }

        res = self.client.post(self.url, req, format='json')
        access_token = res.data['access_token']
        refresh_token = res.cookies.get('refresh_token').value
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(extract_user_id_from_token(access_token), self.user.id)
        self.assertEqual(extract_user_id_from_token(refresh_token), self.user.id)


    def test_login_wrong_password(self):
        req = {
            "username": self.username,
            "password": "wrongpassword"
        }

        response = self.client.post(self.url, req, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        req = {
            "username": "nouser",
            "password": "any"
        }

        response = self.client.post(self.url, req, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
