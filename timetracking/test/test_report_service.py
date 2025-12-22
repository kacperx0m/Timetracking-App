from django.test import TestCase
from timetracking.models import Employee, Schedule, TimeEvent
from datetime import datetime, time, date
from django.utils import timezone
from timetracking.services.report_service import ReportService


class ReportServiceTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")
        self.date = date(2025, 12, 19)

        self.schedule = Schedule.objects.create(
            employee=self.employee,
            date=self.date,
            day_type="WORK",
            time_start=time(9, 0),
            time_end=time(17, 0),
        )

        self._create_event("CHECK_IN", "09:00")
        self._create_event("CHECK_OUT", "17:00")

    def _create_event(self, event_type, time_str):
        event = TimeEvent.objects.create(
            employee=self.employee,
            event_type=event_type,
            device_id=1,
        )
        naive_dt = datetime.combine(
            self.date, datetime.strptime(time_str, "%H:%M").time()
        )
        ts = timezone.make_aware(naive_dt)
        TimeEvent.objects.filter(pk=event.pk).update(timestamp=ts)
        event.refresh_from_db()
        return event

    def test_generate_employee_report_single_day(self):
        schedules = Schedule.objects.filter(employee=self.employee)
        time_events = TimeEvent.objects.filter(employee=self.employee)

        reports = ReportService.generate_employee_report(
            self.employee, schedules, time_events
        )

        self.assertEqual(len(reports), 1)
        report = reports[0]
        report_dict = report.to_dict()

        self.assertEqual(report_dict["employee_id"], self.employee.id)
        self.assertEqual(report_dict["date"], str(self.date))
        self.assertIn("planned_hours", report_dict)
        self.assertIn("worked_hours", report_dict)
        self.assertIn("break_minutes", report_dict)
        self.assertIn("minutes_late", report_dict)
        self.assertIn("absent", report_dict)
        self.assertIn("is_leave", report_dict)
        self.assertIn("anomalies", report_dict)
