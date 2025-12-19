from rest_framework import serializers
from timetracking.models import Employee, TimeEvent, Schedule


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "name", "surname"]
        read_only_fields = ["timestamp"]


class TimeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEvent
        fields = ["id", "employee", "event_type", "timestamp", "device_id"]
        read_only_fields = ["id", "timestamp"]


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["id", "employee", "date", "day_type", "time_start", "time_end"]
        read_only_fields = ["id"]  # TODO: employee as well?


class DailyWorklogSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    date = serializers.DateField()
    planned_hours = serializers.IntegerField()
    worked_hours = serializers.FloatField()
    break_minutes = serializers.FloatField()
    minutes_late = serializers.FloatField()
    absent = serializers.BooleanField()
    is_leave = serializers.BooleanField()
    anomalies = serializers.ListField(child=serializers.CharField(), allow_empty=True)
