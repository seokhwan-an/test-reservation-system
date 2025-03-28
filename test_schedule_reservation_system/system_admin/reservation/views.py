from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.models.reservation import Reservation, Status
from ..permissions import IsStaffUser
from .services import (
    get_all_reservations,
    update_reservation,
    confirm_reservation_by_id,
    delete_reservation
)
from .docs import (
    list_reservations_docs,
    update_reservation_docs,
    confirm_reservation_docs,
    delete_reservation_docs
)
from .serializers import ReservationDetailSerializer

class ReservationAdminViewSet(ViewSet):
    permission_classes = [IsStaffUser]

    @extend_schema(**list_reservations_docs)
    @action(detail=False, methods=['get'], url_path='reservations')
    def list_reservations(self, request):
        serializer = get_all_reservations()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(**update_reservation_docs)
    @action(detail=True, methods=['patch'], url_path='update')
    def update_reservation(self, request, pk=None):
        updated_reservation = update_reservation(pk, request.data)
        serializer = ReservationDetailSerializer(updated_reservation)
        return Response({
            'message': '예약이 수정되었습니다.',
            'reservation': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(**confirm_reservation_docs)
    @action(detail=True, methods=['patch'], url_path='confirm')
    def confirm_reservation(self, request, pk=None):
        confirmed_reservation = confirm_reservation_by_id(pk)
        serializer = ReservationDetailSerializer(confirmed_reservation)
        return Response({
            'message': '예약이 확정되었습니다.',
            'reservation': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(**delete_reservation_docs)
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_reservation(self, request, pk=None):
        delete_reservation(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
