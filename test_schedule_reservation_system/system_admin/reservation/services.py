from core.models.reservation import Reservation, Status
from core.models.reservations import Reservations
from rest_framework.exceptions import NotFound, ValidationError

from .serializers import ReservationSerializer


def is_exist(reservation_id: int) -> Reservation:
    try:
        return Reservation.objects.get(pk=reservation_id)
    except Reservation.DoesNotExist:
        raise NotFound("해당 예약이 존재하지 않습니다.")


def get_all_reservations() -> ReservationSerializer:
    reservations = Reservation.objects.select_related('user').all()
    return ReservationSerializer(reservations, many=True)


def confirm_reservation_by_id(reservation_id: int) -> Reservation:
    reservation = is_exist(reservation_id)

    if reservation.is_confirmed():
        raise ValidationError("이미 확정된 예약입니다.")

    reservations_in_time = Reservations(Reservation.objects.filter(
        test_reservation_date=reservation.test_reservation_date,
        test_start_time__lt=reservation.test_end_time,
        test_end_time__gt=reservation.test_start_time,
        status=Status.CONFIRM
    ))

    reservations_in_time.validate_exceed_limit(reservation.headcount)

    reservation.status = Status.CONFIRM
    reservation.save()
    return reservation

def delete_reservation(reservation_id: int):
    reservation = is_exist(reservation_id)
    reservation.delete()
