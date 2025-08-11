from rest_framework import serializers
from .models import Teachers, ExamEvents, ExamVenues, News, Activity

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teachers
        fields = ['teacher_id', 'first_name', 'last_name', 'subject', 'experience_years', 'credentials', 'bio', 'photo']


class ExamVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamVenues
        fields = ['name', 'adress', 'phone']

class ExamEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamEvents
        fields = ['name', 'date']

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'