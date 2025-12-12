from django.db import models

# Create your models here.


class Employee(models.Model):
    employee_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)


class TimeEvent(models.Model):
    EVENT_TYPES = ("CHECK_IN", "CHECK_OUT", "BREAK_START", "BREAK_END")


class Schedule(models.Model):
    pass
