from datetime import time

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

    def get_hourly_available_headcount(self) -> list:
        available_headcount = []
        for hour in range(0, 24):
            start = time(hour, 0)
            end = time(hour + 1, 0) if hour < 23 else time(23, 59)

            reserved_headcount = sum(
                r.headcount for r in self.reservations
                if r.test_start_time < end and r.test_end_time > start
            )

            available_headcount.append((start, end, max(0, self.MAX_AVAILABLE_LIMIT - reserved_headcount)))
        return available_headcount
