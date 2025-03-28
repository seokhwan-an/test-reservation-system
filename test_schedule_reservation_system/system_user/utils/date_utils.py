from rest_framework.exceptions import ValidationError
from datetime import datetime
from django.utils.timezone import now

def parse_and_validate_date(date_str: str) -> datetime.date:
    if not date_str:
        raise ValidationError("날짜를 입력해주세요. 예: ?date=2025-04-10")

    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요.")

    if input_date < now().date():
        raise ValidationError("현재 날짜보다 이전 날짜는 조회할 수 없습니다.")

    return input_date
