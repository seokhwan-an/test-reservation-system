from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.models.reservation import Reservation, Status
from ..permissions import IsStaffUser
from .services import get_all_reservations, confirm_reservation_by_id, delete_reservation


class ReservationAdminViewSet(ViewSet):
    permission_classes = [IsStaffUser]

    @action(detail=False, methods=['get'], url_path='reservations')
    def list_reservations(self, request):
        serializer = get_all_reservations()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='confirm')
    def confirm_reservation(self, request, pk=None):
        confirm_reservation_by_id(pk)
        return Response({'message': '예약이 확정되었습니다.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_reservation(self, request, pk=None):
        delete_reservation(pk)
        return Response({'message': '예약이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
