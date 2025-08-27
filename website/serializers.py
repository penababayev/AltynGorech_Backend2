from rest_framework import serializers
from .models import *
from courses.models import Subject


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



class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Subject
        fields = "__all__"
        



class CourseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CourseItem
        fields = [
            "id", "subject", "name",
            "description", 
        ]




# announcements/serializers.py

class AnnouncementImageOut(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = AnnouncementImage
        fields = ("id","url","caption","alt","order")

    def get_url(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url

class AnnouncementAttachmentOut(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = AnnouncementAttachment
        fields = ("id","name","url")

    def get_url(self, obj):
        request = self.context.get("request")
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url

class AnnouncementOut(serializers.ModelSerializer):
    images = AnnouncementImageOut(many=True, read_only=True)
    attachments = AnnouncementAttachmentOut(many=True, read_only=True)
    is_published_now = serializers.SerializerMethodField()

    class Meta:
        model  = Announcement
        fields = (
            "id","title","body","link_url",
            "audience","priority","pinned",
            "publish_start_at","publish_end_at",
            "branch","course",
            "is_published_now",
            "images","attachments",
        )

    def get_is_published_now(self, obj):
        return obj.is_published_now



# events/serializers.py

class EventImageOut(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = EventImage
        fields = ("id","url","caption","alt","order")
    def get_url(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url

class EventAttachmentOut(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = EventAttachment
        fields = ("id","name","url")
    def get_url(self, obj):
        request = self.context.get("request")
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url

class EventOut(serializers.ModelSerializer):
    images = EventImageOut(many=True, read_only=True)
    attachments = EventAttachmentOut(many=True, read_only=True)
    is_published_now = serializers.SerializerMethodField()
    is_live_now = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id","title","description","link_url",
            "audience","priority","pinned","status","is_active",
            "start_at","end_at",
            "publish_start_at","publish_end_at",
            "is_published_now","is_live_now","is_upcoming",
            "is_online","meeting_url",
            "venue_name","venue_address","venue_city","venue_room",
            "capacity",
            "branch","course",
            "images","attachments",
        )

    def get_is_published_now(self, obj): return obj.is_published_now
    def get_is_live_now(self, obj): return obj.is_live_now
    def get_is_upcoming(self, obj): return obj.is_upcoming
