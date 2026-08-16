from rest_framework import serializers
from schedule.models import Schedule

class ScheduleSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source='assistant.name', read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id', 
            'title', 
            'room', 
            'target_class', 
            'start_time', 
            'end_time', 
            'assistant', 
            'assistant_name'
        ]
