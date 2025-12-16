from timetracking.models import TimeEvent
from django.utils import timezone
from django.core.exceptions import ValidationError


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

        last_event = (
            TimeEvent.objects.filter(employee_id=employee_id, timestamp__date=today)
            .order_by("-timestamp")
            .first()
        )
        first_event = (
            TimeEvent.objects.filter(employee_id=employee_id, timestamp__date=today)
            .order_by("-timestamp")
            .last()
        )
        if event_type == "CHECK_OUT":
            if not first_event or first_event.event_type != "CHECK_IN":
                raise ValidationError("Can't CHECK_OUT without active CHECK_IN")
            if last_event.event_type != "BREAK_END":
                raise ValidationError("Can't CHECK_OUT without BREAK_END")

        elif event_type == "BREAK_END":
            if not last_event or last_event.event_type != "BREAK_START":
                raise ValidationError("Can't BREAK_END without BREAK_START")

        elif event_type == "BREAK_START":
            if not first_event or first_event.event_type != "CHECK_IN":
                raise ValidationError("Can't BREAK_START without active CHECK_IN")

        elif event_type == "CHECK_IN":
            if first_event and first_event.event_type == "CHECK_IN":
                raise ValidationError("Can't CHECK_IN twice in one day")
