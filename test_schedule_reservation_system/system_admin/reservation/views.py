from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.models.reservation import Reservation
from .serializers import ReservationSerializer
from ..permissions import IsStaffUser


class ReservationAdminViewSet(ViewSet):
    permission_classes = [IsStaffUser]

    @action(detail=False, methods=['get'], url_path='reservations')
    def list_reservations(self, request):
        reservations = Reservation.objects.select_related('user').all()
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
