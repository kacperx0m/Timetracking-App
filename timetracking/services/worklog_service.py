from datetime import timedelta, datetime
from timetracking.services.worklog import DailyWorklog
from timetracking.services.anomaly_service import AnomalyService
from django.utils import timezone


class WorklogService:

    @staticmethod
    def calculate_real_worktime(daily_events):
        """
        Assumptions: register only finished events
        """
        real_worktime = timedelta()
        break_time = timedelta()
        check_in = None
        break_start = None
        work_periods = []
        break_periods = []

        for event in daily_events.order_by("timestamp"):
            if event.event_type == "CHECK_IN":
                check_in = event.timestamp

            elif event.event_type == "CHECK_OUT":
                if check_in:
                    check_out = event.timestamp
                    work_periods.append((check_in, check_out))
                    check_in = None

            elif event.event_type == "BREAK_START":
                break_start = event.timestamp

            elif event.event_type == "BREAK_END":
                if break_start:
                    break_end = event.timestamp
                    break_periods.append((break_start, break_end))
                    break_start = None

        work_time = sum((end - start for start, end in work_periods), timedelta())
        break_time = sum((end - start for start, end in break_periods), timedelta())
        real_worktime = work_time - break_time

        return real_worktime / timedelta(hours=1), break_time / timedelta(minutes=1)

    @staticmethod
    def calculate_planned_worktime(single_schedule, break_minutes=30):
        if single_schedule.day_type != "WORK":
            return 0.0
        planned_worktime = timedelta()
        time_end = datetime.combine(single_schedule.date, single_schedule.time_end)
        time_start = datetime.combine(single_schedule.date, single_schedule.time_start)
        time_end = timezone.make_aware(time_end)
        time_start = timezone.make_aware(time_start)
        planned_worktime = time_end - time_start - timedelta(minutes=break_minutes)
        return planned_worktime / timedelta(hours=1)

    @staticmethod
    def check_if_late(single_schedule, daily_events, late_threshold_minutes=5):
        check_in_event = daily_events.filter(
            event_type="CHECK_IN"
        ).last()  # ordering is -timestamp
        if not check_in_event:
            return 0.0
        planned_start = datetime.combine(
            single_schedule.date, single_schedule.time_start
        )
        planned_start = timezone.make_aware(planned_start)
        minutes_late = check_in_event.timestamp - planned_start
        minutes_late /= timedelta(minutes=1)
        return minutes_late if minutes_late >= late_threshold_minutes else 0.0

    @staticmethod
    def check_if_absent(single_schedule, daily_events):
        """
        Assumptions: no time event means no anomalies -> means absence
        """
        if single_schedule.day_type == "WORK" and not daily_events:
            return True
        return False

    @staticmethod
    def create_daily_worklog(
        employee,
        single_schedule,
        daily_events,
        break_minutes=30,
        late_threshold_minutes=5,
    ):
        anomalies = []
        absent = WorklogService.check_if_absent(single_schedule, daily_events)
        planned_hours = round(
            WorklogService.calculate_planned_worktime(single_schedule, break_minutes), 2
        )
        worked_hours = 0.0
        break_minutes = 0.0
        minutes_late = 0.0
        is_leave = False
        if single_schedule.day_type == "OFF":
            pass
        elif single_schedule.day_type == "LEAVE":
            is_leave = True
        else:
            if not absent:
                worked_hours, break_minutes = WorklogService.calculate_real_worktime(
                    daily_events
                )
                minutes_late = WorklogService.check_if_late(
                    single_schedule, daily_events, late_threshold_minutes
                )
                anomalies = AnomalyService.check_for_daily_anomalies(daily_events)
        daily_worklog = DailyWorklog(
            employee.id,
            single_schedule.date,
            planned_hours,
            worked_hours,
            break_minutes,
            minutes_late,
            absent,
            is_leave,
            anomalies,
        )
        return daily_worklog
