from dataclasses import dataclass
import datetime
from enum import Enum


class Anomalies(Enum):
    NO_CHECK_OUT = "no check-out"
    BREAK_WITHOUT_END = "break without end"
    CHECK_OUT_WITHOUT_CHECK_IN = "check-out without check-in"
    MULTIPLE_CHECK_IN = "multiple check-in"


@dataclass
class DailyWorklog:
    employee_id: int
    date: datetime.date
    planned_hours: float
    worked_hours: float
    break_minutes: float
    minutes_late: float
    absent: bool
    is_leave: bool
    anomalies: list[Anomalies]

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "date": str(self.date),
            "planned_hours": self.planned_hours,
            "worked_hours": self.worked_hours,
            "break_minutes": self.break_minutes,
            "minutes_late": self.minutes_late,
            "absent": self.absent,
            "is_leave": self.is_leave,
            "anomalies": [anomaly.value for anomaly in self.anomalies],
        }
