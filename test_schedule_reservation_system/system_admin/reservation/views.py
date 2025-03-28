from drf_spectacular.utils import extend_schema, OpenApiTypes
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
from .serializers import (
    ReservationSerializer,
    ReservationUpdateSerializer
)


class ReservationAdminViewSet(ViewSet):
    permission_classes = [IsStaffUser]

    @extend_schema(
        summary="전체 예약 목록 조회 (관리자)",
        description="관리자(staff)는 모든 예약 목록을 조회할 수 있습니다.",
        responses={200: ReservationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='reservations')
    def list_reservations(self, request):
        serializer = get_all_reservations()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="예약 정보 수정 (관리자)",
        description="예약의 날짜, 시간, 인원 등을 수정합니다. 확정된 예약은 수정할 수 없으며, 수정은 시간제한과 인원 제한을 고려해야 합니다.",
        request=ReservationUpdateSerializer,
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(detail=True, methods=['patch'], url_path='update')
    def update_reservation(self, request, pk=None):
        update_reservation(pk, request.data)
        return Response({'message': '예약이 수정되었습니다.'}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="예약 확정 (관리자)",
        description="관리자가 예약을 확정 상태로 변경합니다. 시간대별 최대 인원(50,000명)을 초과하면 예외가 발생합니다.",
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(detail=True, methods=['patch'], url_path='confirm')
    def confirm_reservation(self, request, pk=None):
        confirm_reservation_by_id(pk)
        return Response({'message': '예약이 확정되었습니다.'}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="예약 삭제 (관리자)",
        description="예약을 삭제합니다. 존재하지 않는 예약을 삭제할 경우 예외가 발생합니다.",
        responses={204: OpenApiTypes.NONE}
    )
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_reservation(self, request, pk=None):
        delete_reservation(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
