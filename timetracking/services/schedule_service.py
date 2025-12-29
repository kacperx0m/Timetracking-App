from timetracking.models import Schedule
from rest_framework.exceptions import ValidationError


class ScheduleService:
    @staticmethod
    def validate_no_schedule_duplicate(employee_id, date):
        if Schedule.objects.filter(employee_id=employee_id, date=date).exists():
            raise ValidationError(
                f"Schedule for {employee_id} on {date} already exists"
            )

    @staticmethod
    def create_schedule_day(employee_id, date, day_type, time_start, time_end):
        ScheduleService.validate_no_schedule_duplicate(employee_id, date)
        return Schedule.objects.create(
            employee_id=employee_id,
            date=date,
            day_type=day_type,
            time_start=time_start,
            time_end=time_end,
        )

    @staticmethod
    def create_schedule_days(
        employee_id,
        days,
        day_type,
        time_start,
        time_end,
    ):

        created_schedules = []
        for day in days:
            try:
                schedule = ScheduleService.create_schedule_day(
                    employee_id=employee_id,
                    date=day,
                    day_type=day_type,
                    time_start=time_start,
                    time_end=time_end,
                )
                created_schedules.append(schedule)
            except Exception as e:
                raise ValidationError(f"Error creating schedule for day {day}: {e}")

        return created_schedules

    @staticmethod
    def update_schedule_day(schedule_id, day_type, time_start, time_end):
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            raise ValidationError(f"Schedule {schedule_id} does not exist")

        schedule.day_type = day_type
        schedule.time_start = time_start
        schedule.time_end = time_end
        schedule.save()

        return schedule

    @staticmethod
    def update_schedule_days(schedule_ids, day_type, time_start, time_end):
        updated_schedules = []
        for schedule_id in schedule_ids:
            try:
                schedule = ScheduleService.update_schedule_day(
                    schedule_id, day_type, time_start, time_end
                )
                updated_schedules.append(schedule)
            except Exception as e:
                raise ValidationError(f"Error updating schedule {schedule_id}: {e}")

        return updated_schedules
