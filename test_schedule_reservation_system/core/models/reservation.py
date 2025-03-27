from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Status(models.TextChoices):
    AWAIT = 'AWAIT', "대기"
    CONFIRM = 'CONFIRM', "확정"


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        null=False
    )
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

    def is_confirmed(self) -> bool:
        return self.status == Status.CONFIRM

    def is_writer(self, user: User):
        return self.user == user