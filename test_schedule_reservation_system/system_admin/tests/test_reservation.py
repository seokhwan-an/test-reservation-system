from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation
from datetime import date, time
from core.auth.token_utils import generate_tokens_for_user


class TestReservationAdminList(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )

        self.user = User.objects.create_user(
            username='normal',
            password='userpass',
            is_staff=False
        )

        Reservation.objects.create(
            user=self.user,
            test_reservation_date=date.today(),
            test_start_time=time(9, 0),
            test_end_time=time(10, 0),
            headcount=1
        )

        Reservation.objects.create(
            user=self.user,
            test_reservation_date=date.today(),
            test_start_time=time(11, 0),
            test_end_time=time(12, 0),
            headcount=2
        )

        self.url = '/api/admin-reservation/reservations/'

    def test_admin_can_see_all_reservations(self):
        tokens = generate_tokens_for_user(self.admin)
        access_token = tokens['access_token']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_normal_user_cannot_see_reservations(self):
        tokens = generate_tokens_for_user(self.user)
        access_token = tokens['access_token']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestDeleteReservation(APITestCase):
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
            headcount=2
        )

        self.url = f'/api/admin-reservation/{self.reservation.id}/delete/'

    def test_admin_can_delete_reservation(self):
        tokens = generate_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_normal_user_cannot_delete_reservation(self):
        tokens = generate_tokens_for_user(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_delete_nonexistent_reservation(self):
        tokens = generate_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        invalid_url = '/api/admin/reservations/reservations/9999/delete/'

        response = self.client.delete(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
