from django.contrib import admin
from .models import *
from django.utils.html import format_html


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display  = ("teacher", "organization", "branch", "is_visible", "sort_order", "slug", "updated_at")
    list_filter   = ("organization", "branch", "is_visible")
    search_fields = ("teacher__first_name", "teacher__last_name", "title_override", "slug")
    autocomplete_fields = ("organization", "branch", "teacher")
    ordering      = ("sort_order", "teacher__last_name")






@admin.register(BranchWeb)
class BranchWebAdmin(admin.ModelAdmin):
    list_display  = ("display_title", "branch", "is_visible", "sort_order", "slug", "updated_at")
    list_filter   = ("is_visible",)
    search_fields = ("title_override", "slug", "branch__name", "branch__address")
    autocomplete_fields = ("branch",)
    ordering      = ("sort_order", "branch__name")

    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Bağlantı", {"fields": ("branch",)}),
        ("Görünüm", {"fields": ("title_override", "description", "photo", "photo_alt")}),
        ("İletişim", {"fields": ("address_override", "phone_override", "email_override")}),
        ("Harita", {"fields": ("map_lat", "map_lng", "map_embed_url")}),
        ("Yayın", {"fields": ("is_visible", "sort_order", "slug", "created_at", "updated_at")}),
    )



@admin.register(CourseItem)
class CourseItemAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "description")







# announcements/admin.py


class AnnouncementImageInline(admin.TabularInline):
    model = AnnouncementImage
    extra = 1
    fields = ("preview", "image", "caption", "alt", "order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if not obj or not obj.image:
            return "-"
        return format_html('<img src="{}" style="max-height:80px; border:1px solid #ddd;"/>', obj.image.url)

class AnnouncementAttachmentInline(admin.TabularInline):
    model = AnnouncementAttachment
    extra = 0

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ("title","audience","status","priority","pinned","is_active","publish_start_at","publish_end_at","branch","course")
    list_filter   = ("audience","status","priority","pinned","is_active","branch","course")
    search_fields = ("title","body")
    date_hierarchy = "publish_start_at"
    readonly_fields = ("view_count","created_at","updated_at")
    inlines = [AnnouncementImageInline, AnnouncementAttachmentInline]



# events/admin.py

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    fields = ("preview", "image", "caption", "alt", "order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if not obj or not obj.image:
            return "-"
        return format_html('<img src="{}" style="max-height:80px;border:1px solid #ddd;"/>', obj.image.url)

class EventAttachmentInline(admin.TabularInline):
    model = EventAttachment
    extra = 0

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ("title","start_at","end_at","audience","status","priority","pinned","is_active","branch","course")
    list_filter   = ("status","audience","priority","pinned","is_active","branch","course","start_at")
    search_fields = ("title","description","venue_name","venue_city","meeting_url")
    date_hierarchy = "start_at"
    readonly_fields = ("view_count","created_at","updated_at")
    inlines = [EventImageInline, EventAttachmentInline]
    fieldsets = (
        ("İçerik", {"fields": ("title","description","link_url","status","audience","priority","pinned","is_active")}),
        ("Zaman",  {"fields": ("start_at","end_at","publish_start_at","publish_end_at")}),
        ("Tür & Mekân", {"fields": ("is_online","meeting_url","venue_name","venue_address","venue_city","venue_room","capacity")}),
        ("İlişkiler", {"fields": ("organization","branch","course","created_by")}),
        ("İzleme", {"fields": ("view_count","created_at","updated_at")}),
    )
    actions = ["act_publish","act_cancel","act_archive"]

    @admin.action(description="Seçilenleri YAYINLA (PUBLISHED)")
    def act_publish(self, request, queryset):
        queryset.update(status="PUBLISHED")

    @admin.action(description="Seçilenleri İPTAL (CANCELLED)")
    def act_cancel(self, request, queryset):
        queryset.update(status="CANCELLED")

    @admin.action(description="Seçilenleri ARŞİVLE (ARCHIVED)")
    def act_archive(self, request, queryset):
        queryset.update(status="ARCHIVED")

