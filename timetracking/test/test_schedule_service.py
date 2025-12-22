from django.test import TestCase
from timetracking.services.schedule_service import ScheduleService
from timetracking.models import Employee, Schedule
from datetime import time, date
from rest_framework.exceptions import ValidationError


class ScheduleServiceTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")
        self.date = date(2025, 12, 22)
        self.days = [
            date(2025, 12, 19),
            date(2025, 12, 20),
            date(2025, 12, 21),
        ]

    def test_create_workday_success(self):
        schedule = ScheduleService.create_schedule_day(
            employee_id=self.employee.id,
            date=self.date,
            day_type="WORK",
            time_start=time(9, 0),
            time_end=time(17, 0),
        )

        self.assertEqual(Schedule.objects.count(), 1)
        self.assertEqual(schedule.employee, self.employee)
        self.assertEqual(schedule.date, self.date)
        self.assertEqual(schedule.day_type, "WORK")
        self.assertEqual(schedule.time_start, time(9, 0))
        self.assertEqual(schedule.time_end, time(17, 0))

    def test_create_duplicate_raises_error(self):
        ScheduleService.create_schedule_day(
            employee_id=self.employee.id,
            date=self.date,
            day_type="WORK",
            time_start=time(9, 0),
            time_end=time(17, 0),
        )

        with self.assertRaises(ValidationError):
            ScheduleService.create_schedule_day(
                employee_id=self.employee.id,
                date=self.date,
                day_type="WORK",
                time_start=time(10, 0),
                time_end=time(18, 0),
            )

    def test_create_multiple_days_success(self):
        schedules = ScheduleService.create_schedule_days(
            employee_id=self.employee.id,
            days=self.days,
            day_type="WORK",
            time_start=time(9, 0),
            time_end=time(17, 0),
        )

        self.assertEqual(len(schedules), 3)
        self.assertEqual(Schedule.objects.count(), 3)
        dates_in_db = set(Schedule.objects.values_list("date", flat=True))
        self.assertEqual(dates_in_db, set(self.days))

    def test_create_multiple_days_rollback_on_duplicate(self):
        existing_date = self.days[1]
        ScheduleService.create_schedule_day(
            employee_id=self.employee.id,
            date=existing_date,
            day_type="WORK",
            time_start=time(9, 0),
            time_end=time(17, 0),
        )

        with self.assertRaises(ValidationError):
            ScheduleService.create_schedule_days(
                employee_id=self.employee.id,
                days=self.days,
                day_type="WORK",
                time_start=time(9, 0),
                time_end=time(17, 0),
            )

        self.assertEqual(Schedule.objects.count(), 2)

    def test_update_schedule_day_raises_validation_error(self):
        non_existing_id = 99999

        with self.assertRaises(ValidationError):
            ScheduleService.update_schedule_day(
                schedule_id=non_existing_id,
                day_type="WORK",
                time_start=time(9, 0),
                time_end=time(17, 0),
            )

    def test_update_schedule_days_raises_validation_error(self):
        non_existing_id = 99999

        schedule = ScheduleService.create_schedule_day(
            employee_id=self.employee.id,
            date=self.date,
            day_type="WORK",
            time_start=time(9, 0),
            time_end=time(17, 0),
        )
        with self.assertRaises(ValidationError):
            ScheduleService.update_schedule_days(
                schedule_ids=[1, non_existing_id],
                day_type="WORK",
                time_start=time(8, 0),
                time_end=time(16, 0),
            )

        schedule = Schedule.objects.get(id=schedule.id)
        self.assertEqual(schedule.time_start, time(8, 0))
