from core.models.reservation import Reservation
from django.contrib.auth.models import User

from .serializers import ReservationSerializer


def get_my_reservations(user: User) -> ReservationSerializer:
    reservations = Reservation.objects.filter(user=user).order_by('-test_reservation_date')
    return ReservationSerializer(reservations, many=True)
