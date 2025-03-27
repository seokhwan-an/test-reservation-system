from core.models.reservation import Reservation, Status
from core.models.reservations import Reservations
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict

from .serializers import ReservationSerializer, ReservationUpdateSerializer


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


def update_reservation(reservation_id: int, data: ReturnDict, user: User):
    reservation = get_reservation_by_id(reservation_id)
    is_manipulate(reservation, user, '수정')

    serializer = ReservationUpdateSerializer(data=data, partial=True)
    serializer.is_valid(raise_exception=True)

    new_headcount = serializer.validated_data.get('headcount', reservation.headcount)

    reservations_in_time = Reservations(Reservation.objects.filter(
        test_reservation_date=reservation.test_reservation_date,
        test_start_time__lt=reservation.test_end_time,
        test_end_time__gt=reservation.test_start_time,
        status=Status.CONFIRM
    ).exclude(pk=reservation.pk))

    reservations_in_time.validate_exceed_limit(new_headcount)

    for attr, value in serializer.validated_data.items():
        setattr(reservation, attr, value)

    reservation.save()


def delete_reservation(reservation_id: int, user: User):
    reservation = get_reservation_by_id(reservation_id)
    is_manipulate(reservation, user, '삭제')

    reservation.delete()
