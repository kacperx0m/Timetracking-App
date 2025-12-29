from django.test import TestCase
from timetracking.models import Employee, TimeEvent, Device
from django.utils import timezone
from datetime import datetime
from timetracking.services.anomaly_service import AnomalyService, Anomalies
from django.contrib.auth.models import User


class AnomalyServiceTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")
        self.date = timezone.now().date()
        self.tablet_user = User.objects.create(
            username="test_tablet1", password="tablet1"
        )
        self.device = Device.objects.create(name="TEST_TABLET1", user=self.tablet_user)

    def test_no_anomalies_day(self):
        self.create_event_at_time(self.employee, "CHECK_IN", "08:00")
        self.create_event_at_time(self.employee, "CHECK_OUT", "16:00")

        events = TimeEvent.objects.filter(employee=self.employee)
        anomalies = AnomalyService.check_for_daily_anomalies(events)

        self.assertEqual(len(anomalies), 0)

    def test_anomaly_no_checkout(self):
        self.create_event_at_time(self.employee, "CHECK_IN", "08:00")

        events = TimeEvent.objects.filter(employee=self.employee)
        anomalies = AnomalyService.check_for_daily_anomalies(events)

        self.assertIn(Anomalies.NO_CHECK_OUT, anomalies)

    def test_anomaly_break_without_end(self):
        self.create_event_at_time(self.employee, "CHECK_IN", "08:00")
        self.create_event_at_time(self.employee, "BREAK_START", "12:00")
        self.create_event_at_time(self.employee, "CHECK_OUT", "16:00")

        events = TimeEvent.objects.filter(employee=self.employee)
        anomalies = AnomalyService.check_for_daily_anomalies(events)

        self.assertIn(Anomalies.BREAK_WITHOUT_END, anomalies)

    def test_anomaly_multiple_check_in(self):
        self.create_event_at_time(self.employee, "CHECK_IN", "08:00")
        self.create_event_at_time(self.employee, "CHECK_IN", "08:05")

        events = TimeEvent.objects.filter(employee=self.employee)
        anomalies = AnomalyService.check_for_daily_anomalies(events)

        self.assertIn(Anomalies.MULTIPLE_CHECK_IN, anomalies)

    def create_event_at_time(self, employee, event_type, time_str):
        event = TimeEvent.objects.create(
            employee=employee,
            event_type=event_type,
            device_id=self.device.id,
        )
        event.timestamp = str(
            timezone.make_aware(
                datetime.combine(self.date, datetime.strptime(time_str, "%H:%M").time())
            ),
        )
        event.save(update_fields=["timestamp"])
