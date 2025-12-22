from django.test import TestCase
from timetracking.models import Employee
from timetracking.serializers import ScheduleBaseSerializer


class ScheduleSerializerTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")

    def test_work_day_requires_times(self):
        data = {
            "employee": self.employee.id,
            "date": "2025-12-19",
            "day_type": "WORK",
        }
        serializer = ScheduleBaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("time_start", str(serializer.errors))

    def test_time_end_after_time_start(self):
        data = {
            "employee": self.employee.id,
            "date": "2025-12-19",
            "day_type": "WORK",
            "time_start": "17:00",
            "time_end": "09:00",
        }
        serializer = ScheduleBaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_not_work_day_valid_without_times(self):
        data = {
            "employee": self.employee.id,
            "date": "2025-12-19",
            "day_type": "OFF",
        }
        serializer = ScheduleBaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
