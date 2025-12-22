from timetracking.services.worklog_service import WorklogService
from django.http import HttpResponse
import csv
from rest_framework.exceptions import ValidationError


class ReportService:
    @staticmethod
    def generate_employee_report(employee, schedules, time_events):
        reports = []
        for single_schedule in schedules:
            daily_events = time_events.filter(timestamp__date=single_schedule.date)
            daily_worklog = WorklogService.create_daily_worklog(
                employee, single_schedule, daily_events
            )

            reports.append(daily_worklog)
        return reports

    @staticmethod
    def export_to_csv(employee_report):
        if not employee_report:
            raise ValidationError("Cannot export empty report")
        filename = f"Report_employee{employee_report[0].employee_id}_{employee_report[0].date}_{employee_report[-1].date}.csv"
        response = HttpResponse(
            content_type="text/csv",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Employee ID",
                "Date",
                "Planned Hours",
                "Worked Hours",
                "Break Minutes",
                "Minutes Late",
                "Absent",
                "Leave",
                "Anomalies",
            ]
        )

        for report in employee_report:
            writer.writerow(
                [
                    report.employee_id,
                    report.date,
                    report.planned_hours,
                    round(report.worked_hours, 2),
                    round(report.break_minutes, 2),
                    round(report.minutes_late, 2),
                    "Yes" if report.absent else "No",
                    "Yes" if report.is_leave else "No",
                    ", ".join(report.anomalies) if report.anomalies else "None",
                ]
            )

        return response
