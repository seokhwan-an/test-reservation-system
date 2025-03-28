from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, OpenApiExample

from .serializers import (
    ReservationSerializer,
    ReservationUpdateSerializer,
    ReservationDetailSerializer
)

list_reservations_docs = {
    "summary": "전체 예약 목록 조회 (관리자)",
    "description": "관리자(staff)는 모든 예약 목록을 조회할 수 있습니다.",
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 인증 헤더 (예: Bearer <token>)"
        )
    ],
    "responses": {200: ReservationSerializer(many=True)}
}

update_reservation_docs = {
    "summary": "예약 정보 수정 (관리자)",
    "description": "예약의 날짜, 시간, 인원 등을 수정합니다. 확정된 예약은 수정할 수 없으며, 수정은 시간제한과 인원 제한을 고려해야 합니다.",
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 인증 헤더 (예: Bearer <token>)"
        )
    ],
    "request": ReservationUpdateSerializer,
    "examples": [
        OpenApiExample(
            name="예약 수정 성공 응답",
            value={
                "message": "예약이 수정되었습니다.",
                "reservation": {
                    "id": 1,
                    "user": "user1",
                    "test_reservation_date": "2025-04-20",
                    "test_start_time": "10:00",
                    "test_end_time": "11:00",
                    "headcount": 100,
                    "status": "AWAIT",
                    "created_at": "2025-04-10T00:00:00Z",
                    "updated_at": "2025-04-11T00:00:00Z"
                }
            },
            response_only=True
        )
    ],
    "responses": {200: ReservationDetailSerializer}
}

confirm_reservation_docs = {
    "summary": "예약 확정 (관리자)",
    "description": "관리자가 예약을 확정 상태로 변경합니다. 시간대별 최대 인원(50,000명)을 초과하면 예외가 발생합니다.",
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 액세스 토큰 (어드민 권한 필요). 예: Bearer <your_token>"
        )
    ],
    "examples": [
        OpenApiExample(
            name="예약 확정 성공 응답",
            value={
                "message": "예약이 확정되었습니다.",
                "reservation": {
                    "id": 1,
                    "user": "user1",
                    "test_reservation_date": "2025-04-20",
                    "test_start_time": "10:00",
                    "test_end_time": "11:00",
                    "headcount": 100,
                    "status": "CONFIRM",
                    "created_at": "2025-04-10T00:00:00Z",
                    "updated_at": "2025-04-11T00:00:00Z"
                }
            },
            response_only=True
        )
    ],
    "responses": {200: ReservationDetailSerializer}
}

delete_reservation_docs = {
    "summary": "예약 삭제 (관리자)",
    "description": "예약을 삭제합니다. 존재하지 않는 예약을 삭제할 경우 예외가 발생합니다.",
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 액세스 토큰 (어드민 권한 필요). 예: Bearer <your_token>"
        )
    ],
    "responses": {204: OpenApiTypes.NONE}
}
