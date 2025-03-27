from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models.reservation import Reservation, Status
from datetime import date, time, timedelta
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
        self.assertIn("이전일 수 없습니다", str(response.data))

    def test_end_time_before_start_time(self):
        three_days_later = date.today() + timedelta(days=3)
        response = self.client.patch(self.url, {
            "test_reservation_date": three_days_later,
            "test_start_time": "14:00",
            "test_end_time": "13:00",
            "headcount": 2000
        }, format='json')


        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("종료 시간은 시작 시간보다 이후", str(response.data))

    def test_exceed_headcount_limit(self):
        # 이미 존재하는 확정 예약으로 49000 채움
        Reservation.objects.create(
            user=self.admin,
            test_reservation_date=self.reservation.test_reservation_date,
            test_start_time=time(10, 0),
            test_end_time=time(12, 0),
            headcount=49000,
            status=Status.CONFIRM
        )

        three_days_later = date.today() + timedelta(days=3)
        response = self.client.patch(self.url, {
            "test_reservation_date": three_days_later,
            "test_start_time": "11:00",
            "test_end_time": "12:00",
            "headcount": 2000
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('50,000명을 초과', str(response.data))


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
        self.assertIn('50,000명을 초과', str(response.data[0]))

    def test_normal_user_cannot_confirm_reservation(self):
        tokens = generate_tokens_for_user(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + tokens['access_token'])

        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
