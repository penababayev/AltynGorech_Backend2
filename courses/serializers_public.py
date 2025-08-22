# courses/serializers_public.py
from rest_framework import serializers
from .models import *

class PublicAssessmentSerializer(serializers.ModelSerializer):
    is_open_now = serializers.ReadOnlyField()
    course_title = serializers.CharField(source="course.title", read_only=True)
    branch_name  = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Assessment  # ← kendi Assessment modeline işaret et
        fields = [
            "id", "title", "code", "description", "status",
            "start_at", "end_at", "duration_min", "capacity",
            "is_online", "meeting_url",
            "venue_name", "venue_address", "venue_room", "venue_city",
            "venue_lat", "venue_lng", "map_embed_url",
            "course", "course_title", "branch", "branch_name",
            "is_open_now",
        ]



class PublicAssessmentRegisterSerializer(serializers.Serializer):
    assessment_id = serializers.IntegerField()
    student_id    = serializers.IntegerField(required=True)  # veya email ile yakalayacaksan CharField

    def validate(self, attrs):
        from .models import Assessment, AssessmentResult
        aid = attrs["assessment_id"]
        sid = attrs["student_id"]
        try:
            assessment = Assessment.objects.get(id=aid, status="PUBLISHED")
        except Assessment.DoesNotExist:
            raise serializers.ValidationError("Sınav bulunamadı veya yayında değil.")

        # Kapasite kontrol (isteğe bağlı)
        if assessment.capacity:
            current = AssessmentResult.objects.filter(
                assessment_id=aid
            ).exclude(status="CANCELLED").count()
            if current >= assessment.capacity:
                raise serializers.ValidationError("Kontenjan dolu.")

        # Aynı öğrenci daha önce kayıt oldu mu?
        exists = AssessmentResult.objects.filter(
            assessment_id=aid, student_id=sid
        ).exclude(status="CANCELLED").exists()
        if exists:
            raise serializers.ValidationError("Bu öğrenci zaten kayıtlı.")

        attrs["assessment"] = assessment
        return attrs

    def create(self, validated_data):
        from .models import AssessmentResult
        return AssessmentResult.objects.create(
            assessment=validated_data["assessment"],
            student_id=validated_data["student_id"],
            status="REGISTERED",
        )
