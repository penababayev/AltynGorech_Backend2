from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import DateWidget, Widget
from import_export.admin import ImportExportModelAdmin
from django.db.models import Count, Q
from django.utils import timezone
from . import models


# Register your models here.


# Önemli diğerleri:
@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ("code", "name", "level", "is_active", "created_at")
    list_filter   = ("is_active", "level", "created_at")
    search_fields = ("code", "name")
    ordering      = ("name", "level")


class EnrollmentInline(admin.TabularInline):
    model = models.Enrollment
    extra = 0
    fields = ("student", "status", "enrolled_at")
    readonly_fields = ("enrolled_at",)
    autocomplete_fields = ("student",)


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "course_code", "subject", "branch", "teacher",
        "start_date", "time_start",
        "capacity", "active_enrollments", "is_full_flag",
        "status", "is_active",
    )
    list_filter   = ("status", "is_active", "branch", "teacher", "start_date")
    search_fields = ("course_code", "title", "subject__name", "branch__name", "teacher__first_name", "teacher__last_name")
    ordering      = ("-start_date", "subject__name")
    inlines       = [EnrollmentInline]
    autocomplete_fields = ("subject", "branch", "teacher")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Aktif kayıt sayısını tek sorguda anotasyonla getir
        return qs.select_related("subject", "branch", "teacher").annotate(
            _active_count=Count("enrollments", filter=Q(enrollments__status="ACTIVE"))
        )

    def active_enrollments(self, obj):
        return getattr(obj, "_active_count", 0)
    active_enrollments.short_description = "Aktif Kayıt"

    def is_full_flag(self, obj):
        if not obj.capacity:
            return False
        return getattr(obj, "_active_count", 0) >= obj.capacity
    is_full_flag.boolean = True
    is_full_flag.short_description = "Dolu mu?"


admin.site.register(models.Room)
admin.site.register(models.ClassSession)
admin.site.register(models.Enrollment)
admin.site.register(models.Attendance)

@admin.register(models.Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display  = (
        "title", "code", "organization", "branch", "course",
        "status", "start_at", "end_at", "is_online", "place_short", "capacity",
    )
    list_filter   = ("organization", "branch", "course", "status", "is_online")
    search_fields = ("title", "code", "description", "venue_name", "venue_address", "meeting_url", "venue_city")
    autocomplete_fields = ("organization", "branch", "course", "proctors")
    ordering      = ("-start_at", "-created_at")
    date_hierarchy = "start_at"
    filter_horizontal = ("proctors",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Temel", {
            "fields": ("organization", "branch", "course", "title", "code", "description", "status")
        }),
        ("Zaman/Limit", {
            "fields": ("start_at", "end_at", "duration_min", "capacity")
        }),
        ("Sınav Yeri", {
            "fields": (
                "is_online", "meeting_url",
                "venue_name", "venue_address", "venue_room", "venue_city",
                "venue_lat", "venue_lng", "map_embed_url",
            )
        }),
        ("Gözetmenler", {"fields": ("proctors",)}),
        ("Takip", {"fields": ("created_at", "updated_at")}),
    )

    actions = ("publish_now", "close_now", "archive")

    @admin.display(description="Yer")
    def place_short(self, obj):
        if obj.is_online:
            return "Online"
        return obj.venue_name or (obj.venue_city or "") or "—"

    @admin.action(description="Seçilenleri YAYINLA (hemen)")
    def publish_now(self, request, queryset):
        now = timezone.now()
        updated = 0
        for a in queryset:
            a.status = "PUBLISHED"
            if not a.start_at:
                a.start_at = now
            a.save(update_fields=["status", "start_at"])
            updated += 1
        self.message_user(request, f"{updated} sınav yayınlandı.")

    @admin.action(description="Seçilenleri KAPAT (hemen)")
    def close_now(self, request, queryset):
        now = timezone.now()
        updated = 0
        for a in queryset:
            a.status = "CLOSED"
            if not a.end_at or a.end_at > now:
                a.end_at = now
            a.save(update_fields=["status", "end_at"])
            updated += 1
        self.message_user(request, f"{updated} sınav kapatıldı.")

    @admin.action(description="Seçilenleri ARŞİVLE")
    def archive(self, request, queryset):
        updated = queryset.update(status="ARCHIVED")
        self.message_user(request, f"{updated} sınav arşivlendi.")






@admin.register(models.AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ("assessment", "student", "attempt", "status", "percent", "passed", "is_absent", "created_at")
    list_filter  = ("status", "passed", "is_absent", "assessment")
    search_fields = ("student__first_name", "student__last_name", "student__email", "assessment__title", "assessment__code")
    readonly_fields = ("percent", "created_at", "updated_at", "graded_at")

admin.site.register(models.Assignment)
admin.site.register(models.Submission)
admin.site.register(models.Material)