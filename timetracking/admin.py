from django.contrib import admin
from timetracking.models import Employee, Schedule, TimeEvent


# Register your models here.
# class EmployeeAdmin(admin.ModelAdmin):
#     fields = ["name", "surname"]


admin.site.register(Employee)
admin.site.register(Schedule)
admin.site.register(TimeEvent)
