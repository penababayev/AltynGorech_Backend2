from rest_framework import serializers
from .models import *
from courses.serializers import CourseSerializer

class StudentSerializer(serializers.ModelSerializer):
    branch_name  = CourseSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'
