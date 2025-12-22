from timetracking.services.worklog import Anomalies


class AnomalyService:
    @staticmethod
    def check_for_daily_anomalies(time_events):
        anomalies = []
        check_in_active = False
        break_active = False
        for event in time_events.order_by("timestamp"):
            if event.event_type == "CHECK_IN":
                if check_in_active:
                    anomalies.append(Anomalies.MULTIPLE_CHECK_IN)
                check_in_active = True

            elif event.event_type == "CHECK_OUT":
                if not check_in_active:
                    anomalies.append(Anomalies.CHECK_OUT_WITHOUT_CHECK_IN)
                check_in_active = False

            elif event.event_type == "BREAK_START":
                break_active = True

            elif event.event_type == "BREAK_END":
                break_active = False

        if break_active:
            anomalies.append(Anomalies.BREAK_WITHOUT_END)
        if check_in_active:
            anomalies.append(Anomalies.NO_CHECK_OUT)

        return anomalies
