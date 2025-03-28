from django.utils.timezone import now
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time, timedelta
from core.auth.token_utils import generate_tokens_for_user


class TestReservationAvailabilityAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass')
        tokens = generate_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        self.base_url = '/api/reservations/available/'
        self.target_date = (now().date() + timedelta(days=5)).strftime('%Y-%m-%d')

    def test_no_reservations_returns_full_capacity(self):
        res = self.client.get(self.base_url + f'?date={self.target_date}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["date"], self.target_date)
        self.assertEqual(len(res.data["available_slots"]), 24)
        for slot in res.data["available_slots"]:
            self.assertEqual(slot["available_headcount"], 50000)

    def test_existing_reservation_reduces_available_headcount(self):
        Reservation.objects.create(
            user=self.user,
            test_reservation_date=date.fromisoformat(self.target_date),
            test_start_time=time(10, 0),
            test_end_time=time(12, 0),
            headcount=2000,
            status=Status.CONFIRM
        )

        res = self.client.get(self.base_url + f'?date={self.target_date}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        reduced_hours = ["10:00", "11:00"]
        for slot in res.data["available_slots"]:
            if slot["start_time"] in reduced_hours:
                self.assertEqual(slot["available_headcount"], 48000)
            else:
                self.assertEqual(slot["available_headcount"], 50000)

    def test_invalid_date_returns_error(self):
        res = self.client.get(self.base_url + '?date=invalid-date')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("날짜 형식이 잘못되었습니다", str(res.data))

    def test_past_date_returns_error(self):
        past_date = (now().date() - timedelta(days=1)).strftime('%Y-%m-%d')
        res = self.client.get(self.base_url + f'?date={past_date}')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("현재 날짜보다 이전 날짜는 조회할 수 없습니다.", str(res.data))
