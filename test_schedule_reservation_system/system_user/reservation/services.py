from core.models.reservation import Reservation, Status
from core.models.reservations import Reservations
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict

from .serializers import ReservationSerializer, ReservationUpdateSerializer, ReservationCreateSerializer
from ..utils import date_utils


def create_reservation(data: ReturnDict, user: User) -> Reservation:
    serializer = ReservationCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    test_date = serializer.validated_data['test_reservation_date']
    test_start = serializer.validated_data['test_start_time']
    test_end = serializer.validated_data['test_end_time']
    headcount = serializer.validated_data['headcount']

    reservations_in_time = Reservations(Reservation.objects.filter(
        test_reservation_date=test_date,
        test_start_time__lt=test_end,
        test_end_time__gt=test_start,
        status=Status.CONFIRM
    ))

    reservations_in_time.validate_exceed_limit(headcount)

    reservation = Reservation.objects.create(
        user=user,
        test_reservation_date=test_date,
        test_start_time=test_start,
        test_end_time=test_end,
        headcount=headcount,
        status=Status.AWAIT
    )
    return reservation


def get_my_reservations(user: User) -> ReservationSerializer:
    reservations = Reservation.objects.filter(user=user).order_by('-test_reservation_date')
    return ReservationSerializer(reservations, many=True)


def get_reservation_by_id(reservation_id: int) -> Reservation:
    try:
        return Reservation.objects.get(pk=reservation_id)
    except Reservation.DoesNotExist:
        raise NotFound("해당 예약이 존재하지 않습니다.")


def is_manipulate(reservation: Reservation, user: User, message: str):
    if not reservation.is_writer(user):
        raise PermissionDenied(f"본인의 예약만 {message}할 수 있습니다.")

    if reservation.is_confirmed():
        raise ValidationError(f"확정된 예약은 {message}할 수 없습니다.")


def update_reservation(reservation_id: int, data: ReturnDict, user: User) -> Reservation:
    reservation = get_reservation_by_id(reservation_id)
    is_manipulate(reservation, user, '수정')

    serializer = ReservationUpdateSerializer(data=data, partial=True)
    serializer.is_valid(raise_exception=True)

    new_test_reservation_date = serializer.validated_data['test_reservation_date']
    new_test_start_time = serializer.validated_data['test_start_time']
    new_test_end_time = serializer.validated_data['test_end_time']
    new_headcount = serializer.validated_data['headcount']

    reservations_in_time = Reservations(list(Reservation.objects.filter(
        test_reservation_date=new_test_reservation_date,
        test_start_time__lt=new_test_end_time,
        test_end_time__gt=new_test_start_time,
        status=Status.CONFIRM
    ).exclude(pk=reservation.pk)))

    reservations_in_time.validate_exceed_limit(new_headcount)

    for attr, value in serializer.validated_data.items():
        setattr(reservation, attr, value)

    reservation.save()
    return reservation


def delete_reservation(reservation_id: int, user: User):
    reservation = get_reservation_by_id(reservation_id)
    is_manipulate(reservation, user, '삭제')

    reservation.delete()


def get_available_slots(date: str) -> dict:
    date = date_utils.parse_and_validate_date(date)

    reservations_on_date = Reservations(list(Reservation.objects.filter(
        test_reservation_date=date,
        status=Status.CONFIRM
    )))

    available_slots = reservations_on_date.get_hourly_available_headcount()
    return {
        "date": date,
        "available_slots": available_slots
    }
