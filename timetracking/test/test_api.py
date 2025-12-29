from rest_framework.test import APITestCase
from timetracking.models import Employee, Schedule, Device
from rest_framework import status
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token


class TimeEventAPITest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")
        self.tablet_user = User.objects.create_user(
            username="test_tablet1", password="test_tablet1"
        )
        self.token = Token.objects.create(user=self.tablet_user)
        tablets_group = Group.objects.create(name="tablets")
        self.tablet_user.groups.add(tablets_group)
        self.device = Device.objects.create(name="TEST_TABLET1", user=self.tablet_user)

    def test_register_check_in(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        url = "/time-events/register/"
        data = {
            "employee": self.employee.id,
            "event_type": "CHECK_IN",
            "device": self.device.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event_type"], "CHECK_IN")

    def test_register_invalid_event_order(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        url = "/time-events/register/"
        data = {
            "employee": self.employee.id,
            "event_type": "CHECK_OUT",
            "device": self.device.id,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ScheduleAPITest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(name="Jane", surname="Nowak")
        self.admin = User.objects.create_superuser(
            username="test_admin", password="admin"
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.tablet_user = User.objects.create_user(
            username="test_tablet1", password="test_tablet1"
        )
        self.tablet_token = Token.objects.create(user=self.tablet_user)

    def test_admin_create_schedule(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
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

    def test_user_create_schedule(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.tablet_token.key}")
        url = "/schedule/"
        data = {
            "employee": self.employee.id,
            "date": "2025-12-20",
            "day_type": "WORK",
            "time_start": "09:00",
            "time_end": "17:00",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Schedule.objects.count(), 0)
