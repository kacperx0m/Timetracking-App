from timetracking.models import TimeEvent
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class TimeEventService:
    @staticmethod
    def register_time_event(employee_id, event_type, device_id):
        TimeEventService.validate_event_logic(employee_id, event_type)

        event = TimeEvent.objects.create(
            employee_id=employee_id, event_type=event_type, device_id=device_id
        )
        return event

    @staticmethod
    def validate_event_logic(employee_id, event_type):
        today = timezone.now().date()

        events_today = TimeEvent.objects.filter(
            employee_id=employee_id, timestamp__date=today
        ).order_by("-timestamp", "-id")
        newest_event = events_today.first()
        oldest_event = events_today.last()
        if newest_event is not None:
            active_check_in = newest_event.event_type != "CHECK_OUT"
        else:
            active_check_in = False

        if event_type == "CHECK_OUT":
            if not oldest_event or oldest_event.event_type != "CHECK_IN":
                raise ValidationError("Can't CHECK_OUT without active CHECK_IN")

        elif event_type == "BREAK_END":
            if not newest_event or newest_event.event_type != "BREAK_START":
                raise ValidationError("Can't BREAK_END without BREAK_START")

        elif event_type == "BREAK_START":
            if not active_check_in:
                raise ValidationError("Can't BREAK_START without active CHECK_IN")

        elif event_type == "CHECK_IN":
            if active_check_in:
                raise ValidationError("Can't CHECK_IN while CHECK_IN is active")
