from rest_framework import serializers
from .models import *

class TeacherProfileSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    branch_name  = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model  = TeacherProfile
        fields = [
            "id", "teacher", "teacher_name",
            "organization", "branch", "branch_name",
            "title_override", "bio_public",
            "photo", "photo_alt",
            "slug", "is_visible", "sort_order",
            "created_at", "updated_at",
        ]
        read_only_fields = ("slug", "created_at", "updated_at")

    def get_teacher_name(self, obj):
        t = obj.teacher
        return getattr(t, "full_name", f"{getattr(t, 'first_name', '')} {getattr(t, 'last_name', '')}".strip())







class BranchWebSerializer(serializers.ModelSerializer):
    branch_name    = serializers.CharField(source="branch.name", read_only=True)
    organization_id = serializers.IntegerField(source="branch.organization_id", read_only=True)

    # Web'de göstereceğimiz alanları tek yerde toparlayalım
    title    = serializers.CharField(source="display_title", read_only=True)
    address  = serializers.CharField(source="display_address", read_only=True)
    phone    = serializers.CharField(source="display_phone", read_only=True)
    email    = serializers.CharField(source="display_email", read_only=True)

    class Meta:
        model = BranchWeb
        fields = [
            "id", "slug",
            "branch", "branch_name", "organization_id",
            "title", "description",
            "address", "phone", "email",
            "photo", "photo_alt",
            "map_lat", "map_lng", "map_embed_url",
            "is_visible", "sort_order",
            "created_at", "updated_at",
        ]
        read_only_fields = ("slug", "created_at", "updated_at")
