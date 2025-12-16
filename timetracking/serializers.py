from rest_framework import serializers
from timetracking.models import Employee, TimeEvent, Schedule


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        # fields = ["name", "surname"]
        fields = "__all__"


class TimeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEvent
        fields = ["employee", "event_type", "timestamp", "device_id"]
        read_only_fields = ["timestamp"]


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["employee", "date", "day_type", "time_start", "time_end"]
