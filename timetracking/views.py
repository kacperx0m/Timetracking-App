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
from rest_framework.decorators import action


# Create your views here.
class TimeEventRegister(generics.CreateAPIView):  # views.APIView):
    # def get(self, request, format=None):
    #     return Response({"event_types": [{"choice": choice} for choice in EventTypes]})

    queryset = TimeEvent.objects.all()
    serializer_class = TimeEventSerializer

    def create(self, request, *args, **kwargs):  # format ????
        # parser, serializer, is_valid, response(seralizer)
        # serializer = TimeEventSerializer(data=request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("serializer is not valid")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        try:
            employee_id = validated_data["employee"].id
            event_type = validated_data["event_type"]
            device_id = validated_data["device_id"]
            event = TimeEventService.register_time_event(
                employee_id, event_type, device_id
            )
            response_serializer = TimeEventSerializer(event)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:  # logic error
            return Response(f"Error {e}", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def create_multiple(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get("employee_id")
            days = request.data.get("days")
            day_type = request.data.get("day_type")
            start_time = request.data.get("start_time")
            end_time = request.data.get("end_time")
            schedules = ScheduleService.create_schedule_days(
                employee_id, days, day_type, start_time, end_time
            )
            serializer = ScheduleSerializer(many=True)
            return Response(
                {"created ": len(schedules), "schedules": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)


class TimeEventViewSet(viewsets.ModelViewSet):
    queryset = TimeEvent.objects.all()
    serializer_class = TimeEventSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()


class ScheduleDetail(generics.RetrieveUpdateDestroyAPIView):
    schedule = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class EmployeeReport(viewsets.ModelViewSet):
    def get(self, request, pk, format=None):
        employee = Employee.objects.get(pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data)
        if not serializer.is_valid():
            print("serializer is not valid")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        try:
            employee_id = validated_data["employee_id"].id
            date = validated_data["date"]
            day_type = validated_data["day_type"]
            start_time = validated_data["start_time"]
            end_time = validated_data["end_time"]
            event = ScheduleService.create_schedule_day(
                employee_id, date, day_type, start_time, end_time
            )
            response_serializer = ScheduleSerializer(event)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:  # logic error
            return Response(f"Error {e}", status=status.HTTP_400_BAD_REQUEST)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    pass
