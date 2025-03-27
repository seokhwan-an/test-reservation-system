from rest_framework import serializers
from django.contrib.auth.models import User
from core.models.reservation import Reservation


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