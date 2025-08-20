from rest_framework import serializers
from .models import *

# class TeacherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Teachers
#         fields = ['teacher_id', 'first_name', 'last_name', 'subject', 'experience_years', 'credentials', 'bio', 'photo']


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

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adress
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

# # class CourseItemSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = CourseItem
# #         fields = '__all__'

# class CertificateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Certificate
#         fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    branch_name  = CourseSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Enrollment
        fields = '__all__'
