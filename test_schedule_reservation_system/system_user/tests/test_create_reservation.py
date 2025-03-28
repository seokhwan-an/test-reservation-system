from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time, timedelta
from core.auth.token_utils import generate_tokens_for_user


class TestUserReservationCreate(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.url = "/api/reservations/create/"
        token = generate_tokens_for_user(self.user)['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_create_reservation_success(self):
        test_date = (date.today() + timedelta(days=4)).strftime('%Y-%m-%d')
        data = {
            "test_reservation_date": test_date,
            "test_start_time": "10:00",
            "test_end_time": "11:00",
            "headcount": 1000
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], '예약이 신청되었습니다.')
        self.assertEqual(Reservation.objects.count(), 1)

    def test_create_reservation_within_3_days_fails(self):
        test_date = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        data = {
            "test_reservation_date": test_date,
            "test_start_time": "10:00",
            "test_end_time": "11:00",
            "headcount": 1000
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("3일 이후", str(response.data))

    def test_create_reservation_exceeds_headcount_limit(self):
        test_date = date.today() + timedelta(days=5)
        Reservation.objects.create(
            user=self.user,
            test_reservation_date=test_date,
            test_start_time=time(9, 0),
            test_end_time=time(12, 0),
            headcount=49000,
            status=Status.CONFIRM
        )

        data = {
            "test_reservation_date": test_date.strftime('%Y-%m-%d'),
            "test_start_time": "10:00",
            "test_end_time": "11:00",
            "headcount": 2000
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("50,000명을 초과", str(response.data))
