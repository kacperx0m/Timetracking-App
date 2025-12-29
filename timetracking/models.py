from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Employee(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} {self.surname}"


class Device(models.Model):
    name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="device")

    def __str__(self):
        return f"{self.name} {self.user}"


class EventTypes(models.TextChoices):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"


class TimeEvent(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    event_type = models.CharField(max_length=20, choices=EventTypes.choices)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    device = models.ForeignKey(Device, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.employee} - {self.event_type}: {self.timestamp}, {self.device}"


class DayTypes(models.TextChoices):
    WORK = "WORK"
    OFF = "OFF"
    LEAVE = "LEAVE"


class Schedule(models.Model):
    # Restrict deleting worklog with employee related
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    day_type = models.CharField(max_length=10, choices=DayTypes.choices)
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        if self.day_type in ["OFF", "LEAVE"]:
            return f"{self.date}: {self.employee} {self.day_type}"
        return f"{self.date}: {self.employee} {self.day_type} {self.time_start} {self.time_end}"
