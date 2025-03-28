from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.models.reservation import Reservation, Status
from ..permissions import IsCorporateUser
from .services import create_reservation, get_my_reservations, delete_reservation, update_reservation, \
    get_available_slots

from .serializers import ReservationAvailabilityResponseSerializer


class ReservationAdminViewSet(ViewSet):
    permission_classes = [IsCorporateUser]

    @action(detail=False, methods=['post'], url_path='create')
    def create_reservation(self, request):
        create_reservation(request.data, request.user)
        return Response({'message': '예약이 신청되었습니다.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my')
    def my_reservations(self, request):
        serializer = get_my_reservations(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='update')
    def update_reservation(self, request, pk=None):
        update_reservation(pk, request.data, request.user)
        return Response({'message': '예약이 수정되었습니다.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_reservation(self, request, pk=None):
        delete_reservation(pk, request.user)
        return Response({'message': '예약이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path = 'available')
    def get_available_slots(self, request):
        available_slots = get_available_slots(request.query_params.get('date'))
        serializer = ReservationAvailabilityResponseSerializer(available_slots)
        return Response(serializer.data)
