from django.test import TestCase
from timetracking.models import Employee, TimeEvent, Schedule, Device
from timetracking.services.worklog_service import WorklogService
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User


class WorklogServiceTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")
        self.date = timezone.now().date()
        self.tablet_user = User.objects.create_user(
            username="test_tablet1", password="test_tablet1"
        )
        self.device = Device.objects.create(name="TEST_TABLET1", user=self.tablet_user)

    def update_timestamp(self, time_str):
        return timezone.make_aware(
            datetime.combine(self.date, datetime.strptime(time_str, "%H:%M").time())
        )

    def test_calculate_worktime_with_break(self):
        check_in = TimeEvent.objects.create(
            employee=self.employee,
            event_type="CHECK_IN",
            device_id=self.device.id,
        )
        check_in.timestamp = self.update_timestamp("08:00")
        check_in.save(update_fields=["timestamp"])
        break_start = TimeEvent.objects.create(
            employee=self.employee,
            event_type="BREAK_START",
            device_id=self.device.id,
        )
        break_start.timestamp = self.update_timestamp("12:00")
        break_start.save(update_fields=["timestamp"])
        break_end = TimeEvent.objects.create(
            employee=self.employee,
            event_type="BREAK_END",
            device_id=self.device.id,
        )
        break_end.timestamp = self.update_timestamp("12:30")
        break_end.save(update_fields=["timestamp"])
        check_out = TimeEvent.objects.create(
            employee=self.employee,
            event_type="CHECK_OUT",
            device_id=self.device.id,
        )
        check_out.timestamp = self.update_timestamp("16:00")
        check_out.save(update_fields=["timestamp"])
        events = TimeEvent.objects.filter(
            employee=self.employee, timestamp__date=self.date
        )
        worked_hours, break_minutes = WorklogService.calculate_real_worktime(events)
        self.assertEqual(worked_hours, 7.5)
        self.assertEqual(break_minutes, 30.0)

    def test_check_late(self):
        employee = Employee.objects.create(name="John", surname="Nowak")
        check_in = TimeEvent.objects.create(
            employee=employee,
            event_type="CHECK_IN",
            device_id=self.device.id,
        )
        check_in.timestamp = self.update_timestamp("08:10")
        check_in.save(update_fields=["timestamp"])
        schedule = Schedule.objects.create(
            employee=employee,
            date=self.date,
            day_type="WORK",
            time_start=datetime.strptime("08:00", "%H:%M").time(),
            time_end=datetime.strptime("16:00", "%H:%M").time(),
        )
        events = TimeEvent.objects.filter(employee=employee)
        minutes_late = WorklogService.check_if_late(schedule, events)
        self.assertEqual(minutes_late, 10.0)

    def test_check_absent(self):
        employee = Employee.objects.create(name="Barry", surname="Haul")
        schedule = Schedule.objects.create(
            employee=employee,
            date=self.date,
            day_type="WORK",
            time_start=datetime.strptime("08:00", "%H:%M").time(),
            time_end=datetime.strptime("16:00", "%H:%M").time(),
        )
        events = TimeEvent.objects.none()
        absent = WorklogService.check_if_absent(schedule, events)
        self.assertTrue(absent)

    def test_calculate_planned_worktime(self):
        schedule = Schedule.objects.create(
            employee=self.employee,
            date=self.date,
            day_type="WORK",
            time_start=datetime.strptime("08:00", "%H:%M").time(),
            time_end=datetime.strptime("16:00", "%H:%M").time(),
        )
        planned_worktime = WorklogService.calculate_planned_worktime(schedule)
        self.assertEqual(planned_worktime, 7.5)

    def test_off_day_worklog(self):
        schedule = Schedule.objects.create(
            employee=self.employee,
            date=self.date,
            day_type="OFF",
        )
        events = TimeEvent.objects.none()
        worklog = WorklogService.create_daily_worklog(self.employee, schedule, events)
        self.assertEqual(worklog.employee_id, self.employee.id)
        self.assertEqual(worklog.date, schedule.date)
        self.assertEqual(worklog.planned_hours, 0.0)
        self.assertEqual(worklog.worked_hours, 0.0)
        self.assertEqual(worklog.break_minutes, 0.0)
        self.assertFalse(worklog.absent)
        self.assertFalse(worklog.is_leave)
        self.assertEqual(len(worklog.anomalies), 0)
