from rest_framework import serializers
from timetracking.models import Employee, TimeEvent, Schedule


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "name", "surname"]


class TimeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEvent
        fields = ["id", "employee", "event_type", "timestamp", "device_id"]
        read_only_fields = ["id", "timestamp"]


class ScheduleBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["id", "employee", "date", "day_type", "time_start", "time_end"]
        read_only_fields = ["id"]

    def validate(self, data):
        day_type = data.get("day_type")
        time_start = data.get("time_start")
        time_end = data.get("time_end")

        if day_type == "WORK":
            if not time_start or not time_end:
                raise serializers.ValidationError(
                    "Work days must have time_start and time_end"
                )
            if time_start >= time_end:
                raise serializers.ValidationError("time_end has to be after time_start")

        if day_type in ["OFF", "LEAVE"]:
            if time_start or time_end:
                raise serializers.ValidationError(
                    "OFF or LEAVE days should not have time_start or time_end"
                )

        return data


class ScheduleCreateSerializer(ScheduleBaseSerializer):
    class Meta(ScheduleBaseSerializer.Meta):
        read_only_fields = ["id"]


# Serializer for list / detail / update
class ScheduleSerializer(ScheduleBaseSerializer):
    class Meta(ScheduleBaseSerializer.Meta):
        read_only_fields = ["id", "employee", "date"]


class DailyWorklogSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    date = serializers.DateField()
    planned_hours = serializers.FloatField()
    worked_hours = serializers.FloatField()
    break_minutes = serializers.FloatField()
    minutes_late = serializers.FloatField()
    absent = serializers.BooleanField()
    is_leave = serializers.BooleanField()
    anomalies = serializers.ListField(child=serializers.CharField(), allow_empty=True)

    def validate_worked_hours(self, value):
        if value < 0:
            raise serializers.ValidationError("Worked hours can't be negative number")

    def validate_break_minutes(self, value):
        if value < 0:
            raise serializers.ValidationError("Break time can't be negative number")

    def validate_minutes_late(self, value):
        if value < 0:
            raise serializers.ValidationError("Minutes late can't be negative number")
