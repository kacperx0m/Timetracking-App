from django.db import models

# Create your models here.


class Employee(models.Model):
    # employee_id = models.IntegerField(unique=True, auto_created=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} {self.surname}"


class EventTypes(models.TextChoices):
    CHECK_IN = ("CHECK_IN",)
    CHECK_OUT = "CHECK_OUT"
    BRAEK_START = "BREAK_START"
    BREAK_END = "BREAK_END"


class TimeEvent(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EventTypes)
    timestamp = models.DateTimeField(
        auto_now_add=True
    )  # set field to now when object is created
    device_id = models.IntegerField()

    def __str__(self):
        return (
            f"{self.employee} - {self.event_type}: {self.timestamp}, {self.device_id}"
        )


class DayTypes(models.TextChoices):
    WORK = "WORK"
    OFF = "OFF"
    LEAVE = "LEAVE"


class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    day_type = models.CharField(max_length=10, choices=DayTypes)
    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self):
        if self.day_type in ["OFF", "LEAVE"]:
            return f"{self.date}: {self.employee} {self.day_type}"
        return f"{self.date}: {self.employee} {self.time_start} {self.time_end}"
