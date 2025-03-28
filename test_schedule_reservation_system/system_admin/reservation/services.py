from core.models.reservation import Reservation, Status
from core.models.reservations import Reservations
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict

from .serializers import ReservationSerializer, ReservationUpdateSerializer


def get_reservation_by_id(reservation_id: int) -> Reservation:
    try:
        return Reservation.objects.get(pk=reservation_id)
    except Reservation.DoesNotExist:
        raise NotFound("해당 예약이 존재하지 않습니다.")


def get_all_reservations() -> ReservationSerializer:
    reservations = Reservation.objects.select_related('user').all()
    return ReservationSerializer(reservations, many=True)


def update_reservation(reservation_id: int, data: ReturnDict) -> Reservation:
    reservation = get_reservation_by_id(reservation_id)

    serializer = ReservationUpdateSerializer(data=data)
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


def confirm_reservation_by_id(reservation_id: int) -> Reservation:
    reservation = get_reservation_by_id(reservation_id)

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
    reservation = get_reservation_by_id(reservation_id)
    reservation.delete()
