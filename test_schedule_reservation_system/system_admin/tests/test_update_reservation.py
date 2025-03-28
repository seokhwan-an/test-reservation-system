from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time, timedelta
from core.auth.token_utils import generate_tokens_for_user


class TestAdminUpdateReservation(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.other_user = User.objects.create_user(username="user", password="pass", is_staff=False)

        self.reservation = Reservation.objects.create(
            user=self.admin,
            test_reservation_date=date.today() + timedelta(days=1),
            test_start_time=time(10, 0),
            test_end_time=time(11, 0),
            headcount=1000,
            status=Status.AWAIT
        )

        self.url = f"/api/admin-reservation/{self.reservation.id}/update/"
        self.token = generate_tokens_for_user(self.admin)['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_success_update_reservation(self):
        three_days_later = date.today() + timedelta(days=3)
        res = self.client.patch(self.url, {
            "test_reservation_date": three_days_later,
            "test_start_time": "12:00",
            "test_end_time": "13:00",
            "headcount": 2000
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['message'], "예약이 수정되었습니다.")

    def test_reservation_does_not_exist(self):
        invalid_url = "/api/admin-reservation/9999/update/"
        three_days_later = date.today() + timedelta(days=3)
        res = self.client.patch(invalid_url, {
            "test_reservation_date": three_days_later,
            "test_start_time": "12:00",
            "test_end_time": "13:00",
            "headcount": 2000
        }, format='json')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_start_time_before_now(self):
        yesterday = date.today() - timedelta(days=1)
        response = self.client.patch(self.url, {
            "test_reservation_date": yesterday.strftime('%Y-%m-%d'),
            "test_start_time": "09:00",
            "test_end_time": "10:00",
            "headcount": 2000
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("예약 시작시간은 현재보다 이전일 수 없습니다.", str(response.data))

    def test_end_time_before_start_time(self):
        three_days_later = date.today() + timedelta(days=3)
        response = self.client.patch(self.url, {
            "test_reservation_date": three_days_later,
            "test_start_time": "14:00",
            "test_end_time": "13:00",
            "headcount": 2000
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("종료 시간은 시작 시간보다 이후여야 합니다.", str(response.data))

    def test_exceed_headcount_limit(self):
        # 이미 존재하는 확정 예약으로 49000 채움
        three_days_later = date.today() + timedelta(days=3)
        Reservation.objects.create(
            user=self.admin,
            test_reservation_date=three_days_later,
            test_start_time=time(10, 0),
            test_end_time=time(12, 0),
            headcount=49000,
            status=Status.CONFIRM
        )

        response = self.client.patch(self.url, {
            "test_reservation_date": three_days_later,
            "test_start_time": "11:00",
            "test_end_time": "12:00",
            "headcount": 2000
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("해당 시간대의 예약 인원이 50,000명을 초과합니다.", str(response.data))
