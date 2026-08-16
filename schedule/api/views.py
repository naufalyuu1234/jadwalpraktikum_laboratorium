from rest_framework.decorators import api_view
from rest_framework.response import Response
from schedule.models import Schedule
from .serializers import ScheduleSerializer

@api_view(['GET'])
def api_schedule_list(request):
    schedules = Schedule.objects.all()
    serializer = ScheduleSerializer(schedules, many=True)
    return Response({
        'status': 'success',
        'total': schedules.count(),
        'data': serializer.data
    })