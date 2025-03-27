from core.models.reservation import Reservation
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .serializers import ReservationSerializer


def get_my_reservations(user: User) -> ReservationSerializer:
    reservations = Reservation.objects.filter(user=user).order_by('-test_reservation_date')
    return ReservationSerializer(reservations, many=True)


def get_reservation_by_id(reservation_id: int) -> Reservation:
    try:
        return Reservation.objects.get(pk=reservation_id)
    except Reservation.DoesNotExist:
        raise NotFound("해당 예약이 존재하지 않습니다.")


def delete_reservation(reservation_id: int, user: User):
    reservation = get_reservation_by_id(reservation_id)

    if not reservation.is_writer(user):
        raise PermissionDenied("본인의 예약만 삭제할 수 있습니다.")

    if reservation.is_confirmed():
        raise ValidationError("확정된 예약은 삭제할 수 없습니다.")

    reservation.delete()
