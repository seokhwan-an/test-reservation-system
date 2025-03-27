from rest_framework.exceptions import NotFound
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

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_reservation(self, request, pk=None):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            raise NotFound("해당 예약이 존재하지 않습니다.")

        reservation.delete()
        return Response({'message': '예약이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
