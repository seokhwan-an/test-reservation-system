from django.utils.timezone import now
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time, timedelta
from core.auth.token_utils import generate_tokens_for_user


class TestMyReservations(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass2'
        )

        # user1의 예약 2개
        Reservation.objects.create(
            user=self.user1,
            test_reservation_date=date.today(),
            test_start_time=time(10, 0),
            test_end_time=time(11, 0),
            headcount=1
        )

        Reservation.objects.create(
            user=self.user1,
            test_reservation_date=date.today(),
            test_start_time=time(12, 0),
            test_end_time=time(13, 0),
            headcount=2
        )

        # user2의 예약 1개
        Reservation.objects.create(
            user=self.user2,
            test_reservation_date=date.today(),
            test_start_time=time(14, 0),
            test_end_time=time(15, 0),
            headcount=3
        )

        self.url = '/api/reservations/my/'

    def test_authenticated_user_gets_own_reservations(self):
        tokens = generate_tokens_for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for item in response.data:
            self.assertEqual(item['user']['id'], self.user1.id)

    def test_another_user_does_not_see_others_reservations(self):
        tokens = generate_tokens_for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['id'], self.user2.id)

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_cannot_access_my_reservations(self):
        admin = User.objects.create_user(username='admin', password='adminpass', is_staff=True)
        tokens = generate_tokens_for_user(admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
