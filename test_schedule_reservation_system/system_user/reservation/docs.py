from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, OpenApiExample

from .serializers import (
    ReservationCreateSerializer,
    ReservationSerializer,
    ReservationUpdateSerializer,
    ReservationAvailabilityResponseSerializer,
    ReservationDetailSerializer
)

create_reservation_docs = {
    "summary": "예약 생성",
    "description": "예약을 새로 생성합니다. 최소 3일 이후의 날짜여야 하며, 시간대별 예약 가능 인원을 초과할 수 없습니다.",
    "request": ReservationCreateSerializer,
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 액세스 토큰 (기업 사용자 권한 필요). 예: Bearer <your_token>"
        )
    ],
    "examples": [
        OpenApiExample(
            name="예약 생성 성공 응답 예시",
            value={
                "message": "예약이 신청되었습니다.",
                "reservation": {
                    "id": 17,
                    "user": "company_user1",
                    "test_reservation_date": "2025-04-25",
                    "test_start_time": "10:00:00",
                    "test_end_time": "11:00:00",
                    "headcount": 200,
                    "status": "AWAIT",
                    "created_at": "2025-04-20T10:00:00Z",
                    "updated_at": "2025-04-20T10:00:00Z"
                }
            },
            response_only=True
        )
    ],
    "responses": {
        201: ReservationDetailSerializer
    }
}

my_reservations_docs = {
    "summary": "내 예약 목록 조회",
    "description": "자신이 등록한 예약을 조회합니다.",
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 액세스 토큰 (기업 사용자 권한 필요). 예: Bearer <your_token>"
        )
    ],
    "responses": {
        200: ReservationSerializer(many=True)
    }
}

update_reservation_docs = {
    "summary": "예약 수정",
    "description": "예약을 수정합니다. 최소 3일 이후 시간대로만 수정 가능하며, 확정된 예약은 수정할 수 없습니다.",
    "request": ReservationUpdateSerializer,
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 액세스 토큰 (기업 사용자 권한 필요). 예: Bearer <your_token>"
        )
    ],
    "examples": [
        OpenApiExample(
            name="예약 수정 성공 응답 예시",
            value={
                "message": "예약이 신청되었습니다.",
                "reservation": {
                    "id": 17,
                    "user": "company_user1",
                    "test_reservation_date": "2025-04-25",
                    "test_start_time": "10:00:00",
                    "test_end_time": "11:00:00",
                    "headcount": 200,
                    "status": "AWAIT",
                    "created_at": "2025-04-20T10:00:00Z",
                    "updated_at": "2025-04-20T10:00:00Z"
                }
            },
            response_only=True
        )
    ],
    "responses": {
        200: ReservationDetailSerializer
    }
}

delete_reservation_docs = {
    "summary": "예약 삭제",
    "description": "예약을 삭제합니다. 확정된 예약이나 타인의 예약은 삭제할 수 없습니다.",
    "parameters": [
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 액세스 토큰 (기업 사용자 권한 필요). 예: Bearer <your_token>"
        )
    ],
    "responses": {
        204: OpenApiTypes.NONE
    },
}

available_slots_docs = {
    "summary": "시간대별 예약 가능 인원 조회",
    "description": "입력한 날짜에 대해 00:00부터 23:59까지 각 시간대별로 예약 가능 인원을 조회합니다.",
    "parameters": [
        OpenApiParameter(
            name="date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description="조회할 날짜 (예: 2025-04-10)"
        ),
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="JWT 액세스 토큰 (기업 사용자 권한 필요). 예: Bearer <your_token>"
        )
    ],
    "responses": {
        200: ReservationAvailabilityResponseSerializer
    }
}
