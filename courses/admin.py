from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import DateWidget, Widget
from import_export.admin import ImportExportModelAdmin
from django.db.models import Count, Q
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
admin.site.register(models.Assessment)
admin.site.register(models.AssessmentResult)
admin.site.register(models.Assignment)
admin.site.register(models.Submission)
admin.site.register(models.Material)