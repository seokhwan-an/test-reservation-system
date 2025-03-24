from django.db import models


class MemberRole(models.TextChoices):
    ADMIN = 'ADMIN', '관리자'
    USER = 'USER', '기업 고객'


class Member(models.Model):
    name = models.CharField(max_length=20, null = False)
    role = models.CharField(
        max_length=20,
        choices=MemberRole.choices
    )
