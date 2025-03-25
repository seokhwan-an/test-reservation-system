from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User


class TestSignup(APITestCase):
    def setUp(self):
        self.url = '/api/auth/signup/'

    def test_signup_success(self):
        data = {
            'username': 'newuser',
            'password': 'securepass123',
            'is_staff': 'True'
        }
        res = self.client.post(self.url, data, format='json')

        saved_user = User.objects.filter(username=data['username']).get()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['message'], '회원가입 성공')
        self.assertEqual(saved_user.username, data['username'])
        self.assertTrue(saved_user.check_password(data['password']))
        self.assertEqual(saved_user.is_staff, True)

    def test_signup_missing_fields(self):
        data = {'username': 'noinfo'}
        res = self.client.post(self.url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
