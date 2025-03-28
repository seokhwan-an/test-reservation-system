from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.models.reservation import Reservation, Status
from ..permissions import IsCorporateUser
from .services import (
    create_reservation,
    get_my_reservations,
    delete_reservation,
    update_reservation,
    get_available_slots
)

from .serializers import (
    ReservationAvailabilityResponseSerializer,
    ReservationCreateSerializer,
    ReservationUpdateSerializer,
    ReservationSerializer
)


class ReservationAdminViewSet(ViewSet):
    permission_classes = [IsCorporateUser]

    @extend_schema(
        summary="예약 생성",
        description="예약을 새로 생성합니다. 최소 3일 이후의 날짜여야 하며, 시간대별 예약 가능 인원을 초과할 수 없습니다.",
        request=ReservationCreateSerializer,
        responses={201: OpenApiTypes.OBJECT}
    )
    @action(detail=False, methods=['post'], url_path='create')
    def create_reservation(self, request):
        create_reservation(request.data, request.user)
        return Response({'message': '예약이 신청되었습니다.'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="내 예약 목록 조회",
        description="자신이 등록한 예약을 조회합니다.",
        responses={200: ReservationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my')
    def my_reservations(self, request):
        serializer = get_my_reservations(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="예약 수정",
        description="예약을 수정합니다. 최소 3일 이후 시간대로만 수정 가능하며, 확정된 예약은 수정할 수 없습니다.",
        request=ReservationUpdateSerializer,
        responses={200: OpenApiTypes.NONE}
    )
    @action(detail=True, methods=['patch'], url_path='update')
    def update_reservation(self, request, pk=None):
        update_reservation(pk, request.data, request.user)
        return Response({'message': '예약이 수정되었습니다.'}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="예약 삭제",
        description="예약을 삭제합니다. 확정된 예약이나 타인의 예약은 삭제할 수 없습니다.",
        responses={204: OpenApiTypes.NONE}
    )
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_reservation(self, request, pk=None):
        delete_reservation(pk, request.user)
        return Response({'message': '예약이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="시간대별 예약 가능 인원 조회",
        description="입력한 날짜에 대해 00:00부터 23:59까지 각 시간대별로 예약 가능 인원을 조회합니다.",
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="조회할 날짜 (예: 2025-04-10)"
            )
        ],
        responses={200: ReservationAvailabilityResponseSerializer}
    )
    @action(detail=False, methods=['get'], url_path='available')
    def get_available_slots(self, request):
        available_slots = get_available_slots(request.query_params.get('date'))
        serializer = ReservationAvailabilityResponseSerializer(available_slots)
        return Response(serializer.data)
