from django.test import TestCase
from timetracking.models import Employee, TimeEvent, Device
from timetracking.services.time_event_service import TimeEventService
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User


# Create your tests here.
class TimeEventServiceTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")
        self.tablet_user = User.objects.create(
            username="test_tablet1", password="tablet1"
        )
        self.device = Device.objects.create(name="TEST_TABLET1", user=self.tablet_user)

    def test_cannot_check_out_without_check_in(self):
        with self.assertRaises(ValidationError):
            TimeEventService.register_time_event(
                self.employee.id, "CHECK_OUT", device_id=self.device.id
            )

    def test_cannot_end_break_without_start_break(self):
        with self.assertRaises(ValidationError):
            TimeEventService.register_time_event(
                self.employee.id, "BREAK_END", device_id=self.device.id
            )

    def test_cannot_start_break_without_check_in(self):
        with self.assertRaises(ValidationError):
            TimeEventService.register_time_event(
                self.employee.id, "BREAK_START", device_id=self.device.id
            )

    def test_cannot_check_in_during_check_in(self):
        TimeEventService.register_time_event(
            self.employee.id, "CHECK_IN", device_id=self.device.id
        )
        self.assertEqual(TimeEvent.objects.get(pk=self.employee.pk).id, 1)
        with self.assertRaises(ValidationError):
            TimeEventService.register_time_event(
                self.employee.id, "CHECK_IN", device_id=self.device.id
            )

    def test_normal_work_day_sequence(self):
        check_in = TimeEventService.register_time_event(
            self.employee.id, "CHECK_IN", device_id=self.device.id
        )
        break_start = TimeEventService.register_time_event(
            self.employee.id, "BREAK_START", device_id=self.device.id
        )
        break_end = TimeEventService.register_time_event(
            self.employee.id, "BREAK_END", device_id=self.device.id
        )
        check_out = TimeEventService.register_time_event(
            self.employee.id, "CHECK_OUT", device_id=self.device.id
        )

        events = TimeEvent.objects.filter(employee=self.employee)
        self.assertEqual(events.count(), 4)
