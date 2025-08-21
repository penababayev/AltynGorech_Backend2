from django.contrib import admin
from django.apps import apps
from django.db.models import Count, Q
# from courses.models import Course
from . import models


Course = apps.get_model("courses", "Course")  # app_label, ModelName

#Ogretmenler için
class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    show_change_link = True
    fields = ("course_code", "subject", "branch", "status", "start_date", "end_date", "capacity")
    readonly_fields = ("course_code",)
    autocomplete_fields = ("subject", "branch")

@admin.register(models.Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display  = (
        "full_name", "branch", "status", "employment_type",
        "phone", "email", "active_course_count", "subjects_list", "hire_date"
    )
    list_filter   = ("status", "employment_type", "branch", "subjects")
    search_fields = ("first_name", "last_name", "email", "phone", "subjects__name")
    ordering      = ("last_name", "first_name")
    autocomplete_fields = ("branch", "subjects")
    inlines       = [CourseInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Kimlik", {"fields": ("first_name", "last_name", "title")}),
        ("İletişim", {"fields": ("email", "phone", "address")}),
        ("İlişkiler", {"fields": ("branch", "subjects")}),
        ("İş Bilgileri", {"fields": ("employment_type", "status", "hire_date", "leave_date", "hourly_rate")}),
        ("Diğer", {"fields": ("bio", "created_at", "updated_at")}),
    )

    actions = ["mark_active", "mark_inactive"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Aktif kurs sayısını tek sorguda getir
        return qs.select_related("branch").prefetch_related("subjects").annotate(
            _active_course_count=Count("courses", filter=Q(courses__is_active=True))
        )

    def active_course_count(self, obj):
        return getattr(obj, "_active_course_count", 0)
    active_course_count.short_description = "Aktif Kurs"

    def subjects_list(self, obj):
        names = [s.name for s in obj.subjects.all()[:3]]
        if obj.subjects.count() > 3:
            names.append("…")
        return ", ".join(names)
    subjects_list.short_description = "Konular"

    def mark_active(self, request, queryset):
        updated = queryset.update(status="ACTIVE")
        self.message_user(request, f"{updated} eğitmen AKTİF yapıldı.")
    mark_active.short_description = "Seçilenleri AKTİF yap"

    def mark_inactive(self, request, queryset):
        updated = queryset.update(status="INACTIVE")
        self.message_user(request, f"{updated} eğitmen PASİF yapıldı.")
    mark_inactive.short_description = "Seçilenleri PASİF yap"
