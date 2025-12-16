from timetracking.models import Schedule
from django.core.exceptions import ValidationError


class ScheduleService:
    @staticmethod
    def create_schedule_day(employee_id, date, day_type, start_time, end_time):
        if Schedule.objects.filter(employee_id=employee_id, date=date).exists():
            raise ValidationError(
                f"Schedule for {employee_id} on {date} already exists"
            )

        if day_type == "WORK":
            if not start_time or end_time:
                raise ValidationError("Work day requires start and end time")
            if start_time >= end_time:
                raise ValidationError("Start time must be before end time")

        return Schedule.objects.create(
            employee_id, date, day_type, start_time=start_time, end_time=end_time
        )

    @staticmethod
    def create_schedule_days(
        employee_id,
        days,
        day_type,
        start_time,
        end_time,
    ):

        created_schedules = []
        for day in days:
            try:
                schedule = ScheduleService.create_schedule_day(
                    employee_id=employee_id,
                    date=day,
                    day_type=day_type,
                    start_time=start_time,
                    end_time=end_time,
                )
                created_schedules.append(schedule)
            except ValidationError as e:
                raise (f"Error {e}")

        return created_schedules

    @staticmethod
    def update_schedule_day():
        pass

    def update_schedule_days():
        pass
