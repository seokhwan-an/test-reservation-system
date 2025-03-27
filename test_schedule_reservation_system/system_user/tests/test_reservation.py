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
