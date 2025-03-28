from django.utils.timezone import now
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time, timedelta
from core.auth.token_utils import generate_tokens_for_user


class TestUserReservationUpdate(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')

        self.reservation = Reservation.objects.create(
            user=self.user,
            test_reservation_date=date.today() + timedelta(days=5),
            test_start_time=time(10, 0),
            test_end_time=time(11, 0),
            headcount=1000,
            status=Status.AWAIT
        )

        self.confirmed_reservation = Reservation.objects.create(
            user=self.user,
            test_reservation_date=date.today() + timedelta(days=6),
            test_start_time=time(14, 0),
            test_end_time=time(15, 0),
            headcount=1000,
            status=Status.CONFIRM
        )

        self.other_reservation = Reservation.objects.create(
            user=self.other_user,
            test_reservation_date=date.today() + timedelta(days=5),
            test_start_time=time(12, 0),
            test_end_time=time(13, 0),
            headcount=500,
            status=Status.AWAIT
        )

        self.url = lambda pk: f'/api/reservations/{pk}/update/'

        token = generate_tokens_for_user(self.user)['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_success_update(self):
        new_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
        response = self.client.patch(self.url(self.reservation.id), {
            'test_reservation_date': new_date,
            'test_start_time': '12:00',
            'test_end_time': '13:00',
            'headcount': 1234
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '예약이 수정되었습니다.')

    def test_not_found_reservation(self):
        new_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
        response = self.client.patch(self.url(9999), {
            'test_reservation_date': new_date,
            'test_start_time': '12:00',
            'test_end_time': '13:00',
            'headcount': 100
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_others_reservation(self):
        new_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
        response = self.client.patch(self.url(self.other_reservation.id), {
            'test_reservation_date': new_date,
            'test_start_time': '12:00',
            'test_end_time': '13:00',
            'headcount': 100
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_confirmed_reservation(self):
        new_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
        response = self.client.patch(self.url(self.confirmed_reservation.id), {
            'test_reservation_date': new_date,
            'test_start_time': '12:00',
            'test_end_time': '13:00',
            'headcount': 100
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("확정된 예약", str(response.data))

    def test_invalid_time_range(self):
        new_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
        response = self.client.patch(self.url(self.reservation.id), {
            'test_reservation_date': new_date,
            'test_start_time': '15:00',
            'test_end_time': '14:00',
            'headcount': 100
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("종료 시간은 시작 시간보다 이후", str(response.data))

    def test_cannot_update_to_3_days_before(self):
        response = self.client.patch(self.url(self.reservation.id), {
            'test_reservation_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'test_start_time': '10:00',
            'test_end_time': '11:00',
            'headcount': 100
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("3일 이후로", str(response.data))

    def test_exceed_headcount_limit(self):
        # 기존에 확정 예약으로 49,000명 채우기
        new_date = (date.today() + timedelta(days=6)).strftime('%Y-%m-%d')
        Reservation.objects.create(
            user=self.other_user,
            test_reservation_date=new_date,
            test_start_time=time(9, 0),
            test_end_time=time(12, 0),
            headcount=49000,
            status=Status.CONFIRM
        )

        response = self.client.patch(self.url(self.reservation.id), {
            'test_reservation_date': new_date,
            'test_start_time': "9:00",
            'test_end_time': "12:00",
            'headcount': 2000
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("50,000명을 초과", str(response.data))
