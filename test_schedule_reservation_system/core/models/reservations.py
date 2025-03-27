from rest_framework.exceptions import ValidationError

from .reservation import Reservation


class Reservations:
    MAX_AVAILABLE_LIMIT = 50_000

    def __init__(self, reservations: list[Reservation]):
        self.reservations = reservations

    def get_total_headcount(self):
        return sum(r.headcount for r in self.reservations)

    def validate_exceed_limit(self, headcount: int):
        if self.get_total_headcount() + headcount > self.MAX_AVAILABLE_LIMIT:
            raise ValidationError("해당 시간대의 예약 인원이 50,000명을 초과합니다.")
