from rest_framework import serializers
from .models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'




class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Enrollment
        fields = '__all__'




class AssessmentResultSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AssessmentResult
        fields = [
            "id", "assessment", "student", "graded_by",
            "attempt", "status",
            "registered_at", "started_at", "submitted_at", "graded_at",
            "raw_score", "max_score", "percent", "pass_mark", "passed",
            "is_absent", "notes",
            "duration_minutes",
            "created_at", "updated_at",
        ]
        read_only_fields = ("percent", "passed", "registered_at", "graded_at", "created_at", "updated_at")

    def get_duration_minutes(self, obj):
        return obj.duration_minutes








