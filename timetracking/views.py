from timetracking.models import Schedule, Employee, TimeEvent
from timetracking.serializers import (
    ScheduleSerializer,
    EmployeeSerializer,
    TimeEventSerializer,
)
from rest_framework import generics, viewsets, views, status
from rest_framework.response import Response
from services.time_event_service import TimeEventService


# Create your views here.
class TimeEventRegister(views.APIView):
    def post(self, request, format=None):  # format ????
        # parser, serializer, is_valid, response(seralizer)
        serializer = TimeEventSerializer(data=request.data)
        employee_id = TimeEvent.employee
        event_type = TimeEvent.event_type
        device_id = TimeEvent.device_id
        TimeEventService.register_time_event(employee_id, event_type, device_id)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class ScheduleDetail(generics.RetrieveUpdateDestroyAPIView):
    schedule = Schedule.objects.get()
    serializer_class = ScheduleSerializer


class EmployeeReport(viewsets.ModelViewSet):
    def get(self, request, pk, format=None):
        employee = Employee.objects.get(pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    pass
