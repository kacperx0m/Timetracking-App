from rest_framework.test import APITestCase
from timetracking.models import Employee, Schedule
from rest_framework import status


class TimeEventAPITest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")

    def test_register_check_in(self):
        url = "/time-events/register/"
        data = {"employee": self.employee.id, "event_type": "CHECK_IN", "device_id": 1}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event_type"], "CHECK_IN")

    def test_register_invalid_event_order(self):
        url = "/time-events/register/"
        data = {"employee": self.employee.id, "event_type": "CHECK_OUT", "device_id": 1}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ScheduleAPITest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")

    def test_create_schedule(self):
        url = "/schedule/"
        data = {
            "employee": self.employee.id,
            "date": "2025-12-20",
            "day_type": "WORK",
            "time_start": "09:00",
            "time_end": "17:00",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)
