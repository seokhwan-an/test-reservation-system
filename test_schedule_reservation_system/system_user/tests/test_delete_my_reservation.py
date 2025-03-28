from django.utils.timezone import now
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time, timedelta
from core.auth.token_utils import generate_tokens_for_user


class TestDeleteOwnReservation(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')

        self.own_reservation = Reservation.objects.create(
            user=self.user,
            test_reservation_date=date.today(),
            test_start_time=time(10, 0),
            test_end_time=time(11, 0),
            headcount=1,
            status=Status.AWAIT
        )

        self.other_reservation = Reservation.objects.create(
            user=self.other_user,
            test_reservation_date=date.today(),
            test_start_time=time(12, 0),
            test_end_time=time(13, 0),
            headcount=1,
            status=Status.AWAIT
        )

        self.confirmed_reservation = Reservation.objects.create(
            user=self.user,
            test_reservation_date=date.today(),
            test_start_time=time(14, 0),
            test_end_time=time(15, 0),
            headcount=1,
            status=Status.CONFIRM
        )

        self.base_url = '/api/reservations/'

    def _auth(self, user):
        token = generate_tokens_for_user(user)['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_user_can_delete_own_reservation(self):
        self._auth(self.user)
        url = f"{self.base_url}{self.own_reservation.id}/delete/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(id=self.own_reservation.id).exists())

    def test_user_cannot_delete_others_reservation(self):
        self._auth(self.user)

        url = f"{self.base_url}{self.other_reservation.id}/delete/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Reservation.objects.filter(id=self.other_reservation.id).exists())

    def test_delete_nonexistent_reservation(self):
        self._auth(self.user)
        url = f"{self.base_url}99999/delete/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_confirmed_reservation(self):
        self._auth(self.user)
        url = f"{self.base_url}{self.confirmed_reservation.id}/delete/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Reservation.objects.filter(id=self.confirmed_reservation.id).exists())
