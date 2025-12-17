from timetracking.models import Schedule, Employee, TimeEvent, EventTypes
from timetracking.serializers import (
    ScheduleSerializer,
    EmployeeSerializer,
    TimeEventSerializer,
)
from rest_framework import generics, viewsets, views, status
from rest_framework.response import Response
from timetracking.services.time_event_service import TimeEventService
from timetracking.services.schedule_service import ScheduleService
from timetracking.services.report_service import ReportService
from rest_framework.decorators import action


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
            return Response(f"Error {e}", status=status.HTTP_400_BAD_REQUEST)


# class TimeEventViewSet(viewsets.ModelViewSet):
#     queryset = TimeEvent.objects.all()
#     serializer_class = TimeEventSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

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
        employee_id, start_date, end_date, day_type = self.get_query_params(request)
        schedule = Schedule.objects.all()

        # if not employee_id:
        #     return Response(
        #         {"error": f"No employee {employee_id}"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # if not start_date or not end_date:
        #     return Response(
        #         {"error": f"No date range {start_date}-{end_date}"},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        if employee_id:
            schedules = Schedule.objects.filter(employee_id=employee_id)

        if start_date and end_date:
            schedules = Schedule.objects.filter(date__range=[start_date, end_date])

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
            response_serializer = ScheduleSerializer(schedule)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:  # logic error
            return Response(f"Error {e}", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def create_multiple(self, request, *args, **kwargs):
        try:
            employee_id, days, day_type, time_start, time_end = self.get_request_data(
                request
            )
            schedules = ScheduleService.create_schedule_days(
                employee_id, days, day_type, time_start, time_end
            )
            serializer = ScheduleSerializer(schedules, many=True)
            return Response(
                {"created ": len(schedules), "schedules": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            schedule_id = instance.id
            # TODO: don't update employee?
            # TODO: don't update date?
            _, _, day_type, time_start, time_end = self.get_validated_data(
                validated_data
            )
            schedule = ScheduleService.update_schedule_day(
                schedule_id, day_type, time_start, time_end
            )
            response_serializer = ScheduleSerializer(schedule)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error {e}", status=status.HTTP_400_BAD_REQUEST)

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
            return Response(f"Error {e}", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"])
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


class EmployeeReport(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(detail=False, methods=["get"])
    def report(self, request, pk, format=None):
        employee = Employee.objects.get(pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        schedules = Schedule.objects.filter(employee=employee).filter(
            date__range=[start_date, end_date]
        )
        time_events = TimeEvent.objects.filter(employee=employee).filter(
            timestamp__range=[start_date, end_date]
        )

        report = ReportService.generate_employee_raport(
            employee, schedules, time_events
        )

        return Response({"report": report})


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    pass
