from rest_framework import serializers
from .models import Teachers

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teachers
        fields = ['teacher_id', 'first_name', 'last_name', 'subject', 'experience_years', 'credentials', 'bio', 'photo']