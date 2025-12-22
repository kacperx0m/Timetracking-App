from timetracking.models import Schedule, Employee, TimeEvent
from timetracking.serializers import (
    ScheduleBaseSerializer,
    ScheduleCreateSerializer,
    ScheduleSerializer,
    EmployeeSerializer,
    TimeEventSerializer,
    DailyWorklogSerializer,
)
from rest_framework import generics, viewsets, views, status
from rest_framework.response import Response
from timetracking.services.time_event_service import TimeEventService
from timetracking.services.schedule_service import ScheduleService
from timetracking.services.report_service import ReportService
from rest_framework.decorators import action
from django.utils import timezone
import calendar


# Create your views here.
class TimeEventRegister(generics.CreateAPIView):
    queryset = TimeEvent.objects.all()
    serializer_class = TimeEventSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            employee_id = validated_data["employee"].id
            event_type = validated_data["event_type"]
            device_id = validated_data["device_id"]
            time_event = TimeEventService.register_time_event(
                employee_id, event_type, device_id
            )
            response_serializer = TimeEventSerializer(time_event)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:  # logic error
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TimeEventViewSet(viewsets.ModelViewSet):
    queryset = TimeEvent.objects.all()
    serializer_class = TimeEventSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return ScheduleCreateSerializer
        return ScheduleSerializer

    def get_query_params(self, request):
        employee_id = request.query_params.get("employee_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        day_type = request.query_params.get("day_type")
        return employee_id, start_date, end_date, day_type

    def get_request_data(self, request):
        employee_id = request.data.get("employee_id")
        days = request.data.get("days")
        day_type = request.data.get("day_type")
        time_start = request.data.get("time_start")
        time_end = request.data.get("time_end")
        return employee_id, days, day_type, time_start, time_end

    def get_validated_data(self, validated_data):
        employee_id = validated_data["employee"].id
        date = validated_data["date"]
        day_type = validated_data["day_type"]
        time_start = validated_data["time_start"]
        time_end = validated_data["time_end"]
        return employee_id, date, day_type, time_start, time_end

    @action(detail=False, methods=["get"])
    def get_employee_schedule_range(self, request):
        employee_id, start_date, end_date, _ = self.get_query_params(request)
        schedules = Schedule.objects.all()

        if employee_id:
            schedules = schedules.filter(employee_id=employee_id)

        if start_date and end_date:
            schedules = schedules.filter(date__range=[start_date, end_date])

        schedules = schedules.order_by("date", "employee")
        serializer = self.get_serializer(schedules, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            employee_id, date, day_type, time_start, time_end = self.get_validated_data(
                validated_data
            )
            schedule = ScheduleService.create_schedule_day(
                employee_id, date, day_type, time_start, time_end
            )
            response_serializer = ScheduleCreateSerializer(schedule)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:  # logic error
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def create_multiple(self, request, *args, **kwargs):
        try:
            employee_id, days, day_type, time_start, time_end = self.get_request_data(
                request
            )
            schedules = ScheduleService.create_schedule_days(
                employee_id, days, day_type, time_start, time_end
            )
            serializer = ScheduleCreateSerializer(schedules, many=True)
            return Response(
                {"created ": len(schedules), "schedules": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        This method is only for updating day_type, time_start and time_end.
        To change employee or date assigned to schedule - delete existing object and create new one.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            schedule_id = instance.id
            _, _, day_type, time_start, time_end = self.get_validated_data(
                validated_data
            )
            schedule = ScheduleService.update_schedule_day(
                schedule_id, day_type, time_start, time_end
            )
            response_serializer = ScheduleSerializer(schedule)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def update_multiple(self, request, *args, **kwargs):
        schedule_ids = request.data.get("schedule_ids", [])
        _, _, day_type, time_start, time_end = self.get_request_data(request)

        if not schedule_ids:
            return Response(
                {"Error": "Field schedule_ids required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            schedules = ScheduleService.update_schedule_days(
                schedule_ids, day_type, time_start, time_end
            )
            response_serializer = self.get_serializer(
                schedules, many=True, partial=True
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def delete_multiple(self, request, *args, **kwargs):
        schedule_ids = request.data.get("schedule_ids", [])

        if not schedule_ids:
            return Response(
                {"Error": "Field schedule_ids required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = Schedule.objects.filter(id__in=schedule_ids).delete()
        return Response(
            {"message": f"Deleted {deleted_count} elements"}, status=status.HTTP_200_OK
        )


class EmployeeReport(views.APIView):
    def get(self, request, pk):
        employee = Employee.objects.get(pk=pk)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        export_csv = request.query_params.get("export_csv")
        now = timezone.localdate()
        if not start_date:
            start_date = now.replace(day=1)
        if not end_date:
            last_day = calendar.monthrange(now.year, now.month)[1]
            end_date = now.replace(day=last_day, hour=23, minute=59, seconds=59)
        schedules = Schedule.objects.filter(employee=employee).filter(
            date__range=[start_date, end_date]
        )
        time_events = TimeEvent.objects.filter(employee=employee).filter(
            timestamp__date__range=[start_date, end_date]
        )

        reports = ReportService.generate_employee_report(
            employee, schedules, time_events
        )

        if export_csv:
            return ReportService.export_to_csv(reports)

        serializer = DailyWorklogSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
