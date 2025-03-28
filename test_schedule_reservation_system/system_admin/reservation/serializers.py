from datetime import datetime

from django.utils.timezone import now, make_aware
from rest_framework import serializers
from django.contrib.auth.models import User
from core.models.reservation import Reservation
from rest_framework.exceptions import ValidationError


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff']


class ReservationSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id',
            'user',
            'test_reservation_date',
            'test_start_time',
            'test_end_time',
            'headcount',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]


class ReservationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'test_reservation_date',
            'test_start_time',
            'test_end_time',
            'headcount',
        ]

    def validate(self, data):
        test_date = data.get('test_reservation_date')
        test_start = data.get('test_start_time')
        test_end = data.get('test_end_time')

        if test_date and test_start:
            if make_aware(datetime.combine(test_date, test_start)) < now():
                raise ValidationError("예약 시작시간은 현재보다 이전일 수 없습니다.")

        if test_start and test_end:
            if test_end <= test_start:
                raise ValidationError("종료 시간은 시작 시간보다 이후여야 합니다.")

        return data

class ReservationDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Reservation
        fields = [
            'id',
            'user',
            'test_reservation_date',
            'test_start_time',
            'test_end_time',
            'headcount',
            'status',
            'created_at',
            'updated_at',
        ]
