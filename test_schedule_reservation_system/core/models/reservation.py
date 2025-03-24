from django.db import models


class Status(models.TextChoices):
    AWAIT = 'AWAIT', "대기"
    CONFIRM = 'CONFIRM', "확정"


class Reservation(models.Model):
    member_id = models.BigIntegerField(null=False)
    test_reservation_date = models.DateField(null=False)
    test_start_time = models.TimeField(null=False)
    test_end_time = models.TimeField(null=False)
    headcount = models.IntegerField(null=False, default=0)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.AWAIT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
