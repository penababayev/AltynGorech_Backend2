from rest_framework import serializers
from .models import *



class TimetableEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableEntry
        fields = (
            "id","title","course","branch","teacher",
            "day_of_week","start_time","end_time","repeat_every",
            "valid_from","valid_to",
            "room","is_online","meeting_url","capacity","notes","is_active"
        )