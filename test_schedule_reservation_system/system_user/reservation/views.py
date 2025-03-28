from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.models.reservation import Reservation, Status

from ..permissions import IsCorporateUser
from .docs import (
    create_reservation_docs,
    my_reservations_docs,
    update_reservation_docs,
    delete_reservation_docs,
    available_slots_docs
)
from .services import (
    create_reservation,
    get_my_reservations,
    delete_reservation,
    update_reservation,
    get_available_slots
)
from .serializers import (
    ReservationAvailabilityResponseSerializer,
    ReservationDetailSerializer
)


class ReservationAdminViewSet(ViewSet):
    permission_classes = [IsCorporateUser]

    @extend_schema(**create_reservation_docs)
    @action(detail=False, methods=['post'], url_path='create')
    def create_reservation(self, request):
        new_reservation = create_reservation(request.data, request.user)
        serializer = ReservationDetailSerializer(new_reservation)

        return Response({
            'message': '예약이 신청되었습니다.',
            'reservation': serializer.data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(**my_reservations_docs)
    @action(detail=False, methods=['get'], url_path='my')
    def my_reservations(self, request):
        serializer = get_my_reservations(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(**update_reservation_docs)
    @action(detail=True, methods=['patch'], url_path='update')
    def update_reservation(self, request, pk=None):
        updated_reservation = update_reservation(pk, request.data, request.user)
        serializer = ReservationDetailSerializer(updated_reservation)

        return Response({
            'message': '예약이 수정되었습니다.',
            'reservation': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(**delete_reservation_docs)
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_reservation(self, request, pk=None):
        delete_reservation(pk, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(**available_slots_docs)
    @action(detail=False, methods=['get'], url_path='available')
    def get_available_slots(self, request):
        available_slots = get_available_slots(request.query_params.get('date'))
        serializer = ReservationAvailabilityResponseSerializer(available_slots)
        return Response(serializer.data)
