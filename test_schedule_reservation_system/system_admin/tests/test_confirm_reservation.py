from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time
from core.auth.token_utils import generate_tokens_for_user


class TestConfirmReservation(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )

        self.normal_user = User.objects.create_user(
            username='user',
            password='userpass',
            is_staff=False
        )

        self.reservation = Reservation.objects.create(
            user=self.admin,
            test_reservation_date=date.today(),
            test_start_time=time(10, 0),
            test_end_time=time(11, 0),
            headcount=10000,
            status=Status.AWAIT
        )

        self.url = f'/api/admin-reservation/{self.reservation.id}/confirm/'

    def test_admin_can_confirm_reservation(self):
        tokens = generate_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '예약이 확정되었습니다.')

        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, Status.CONFIRM)

    def test_already_confirmed_reservation(self):
        self.reservation.status = Status.CONFIRM
        self.reservation.save()

        tokens = generate_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), '이미 확정된 예약입니다.')

    def test_reservation_not_found(self):
        tokens = generate_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        invalid_url = '/api/admin-reservation/99999/confirm/'
        response = self.client.patch(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_exceed_headcount_limit(self):
        Reservation.objects.create(
            user=self.admin,
            test_reservation_date=self.reservation.test_reservation_date,
            test_start_time=time(9, 0),
            test_end_time=time(12, 0),
            headcount=49000,
            status=Status.CONFIRM
        )

        self.reservation.headcount = 1001
        self.reservation.save()

        tokens = generate_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("해당 시간대의 예약 인원이 50,000명을 초과합니다.", str(response.data[0]))

    def test_normal_user_cannot_confirm_reservation(self):
        tokens = generate_tokens_for_user(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
