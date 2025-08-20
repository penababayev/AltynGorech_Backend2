from django.contrib import admin


from import_export import resources, fields
from import_export.widgets import DateWidget, Widget
from import_export.admin import ImportExportModelAdmin
from django.db.models import Count, Q
from . import models

# Register your models here.

# admin.site.register(Teachers)
# admin.site.register(ExamEvents)
# admin.site.register(News)
# admin.site.register(Activity)
# admin.site.register(Video)
# admin.site.register(Adress)
# admin.site.register(Course)
# admin.site.register(CourseItem)
# admin.site.register(Certificate)


#--- Student Area -----

class BranchFromDisplayWidget(Widget):
    """
    'Organization - Branch' formatındaki tek kolondan gerçek Branch nesnesi üretir.
    Örn: 'Altyn Göreç Okuw Merkezi - Ýolöten şahamçasy'
    Boşsa None döner.
    """
    def clean(self, value, row=None, *args, **kwargs):
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None

        # ' - ' ile sadece ilkinden böl (kurum adında tire olabilir diye)
        parts = [p.strip() for p in text.split(' - ', 1)]
        if len(parts) == 2:
            org_name, branch_name = parts
        else:
            # Yedek: CSV'de ayrı 'Kurum' kolonu varsa onu kullan
            org_name = (row.get("Kurum") or row.get("Organization") or "").strip()
            branch_name = text

        qs = models.Branch.objects.all()
        if org_name:
            qs = qs.filter(organization__name__iexact=org_name)

        try:
            return qs.get(name__iexact=branch_name)
        except models.Branch.DoesNotExist:
            raise ValueError(f"Şube bulunamadı: org='{org_name}', şube='{branch_name}'")
        except models.Branch.MultipleObjectsReturned:
            raise ValueError(f"Birden fazla şube bulundu: org='{org_name}', şube='{branch_name}'")


# Excel kolon isimlerini Türkçe vereceğiz ve alanlara map edeceğiz.
class StudentResource(resources.ModelResource):
    # Tarih formatı: YYYY-MM-DD kullanın (örn: 2000-05-21)
    date_of_birth   = fields.Field(
        column_name="Doğum Tarihi",
        attribute="date_of_birth",
        widget=DateWidget(format="%Y-%m-%d"),
    )
    enrollment_date = fields.Field(
        column_name="Kayıt Tarihi",
        attribute="enrollment_date",
        widget=DateWidget(format="%Y-%m-%d"),
    )
    # CSV başlığındaki kolon adını kendi dosyana göre ayarla (örn. 'Şube')
    branch = fields.Field(
        column_name="Şube",
        attribute="branch",
        widget=BranchFromDisplayWidget(),
    )
 

    # Diğer alanlar (Türkçe kolon adları)
    student_number  = fields.Field(column_name="Öğrenci No", attribute="student_number")
    first_name      = fields.Field(column_name="Ad", attribute="first_name")
    last_name       = fields.Field(column_name="Soyad", attribute="last_name")
    gender          = fields.Field(column_name="Cinsiyet", attribute="gender")
    email           = fields.Field(column_name="E-posta", attribute="email")
    phone           = fields.Field(column_name="Telefon", attribute="phone")
    address         = fields.Field(column_name="Adres", attribute="address")
    # guardian_name   = fields.Field(column_name="Veli Ad Soyad", attribute="guardian_name")
    # guardian_phone  = fields.Field(column_name="Veli Telefon", attribute="guardian_phone")
    status          = fields.Field(column_name="Durum", attribute="status")
    notes           = fields.Field(column_name="Notlar", attribute="notes")

    class Meta:
        model = models.Student
        # Import’ta kayıt eşleştirmek için benzersiz alan:
        import_id_fields = ["student_number"]
        # İçe/dışa aktarılacak alanların sırası:
        fields = (
            "student_number",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "email",
            "phone",
            "address",
            # "guardian_name",
            # "guardian_phone",
            "branch",
            "status",
            "enrollment_date",
            "notes",
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True

@admin.register(models.Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource

    list_display  = ("student_number", "first_name", "last_name", "branch", "status", "enrollment_date")
    list_filter   = ("branch", "status", "gender")
    search_fields = ("student_number", "first_name", "last_name", "email", "phone") #"guardian_name", "guardian_phone")
    readonly_fields = ("student_number", "enrollment_date")

    # Admin içinden şablon indirme ipucu:
    # django-import-export üzerindeki "Export" ve "Import" sayfalarında
    # "Formats" kısmından XLSX seçebilirsiniz.



@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)

@admin.register(models.Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("name",)

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "organization", "branch")
    list_filter = ("role", "organization", "branch")
    search_fields = ("user__username", "user__first_name", "user__last_name")


#Ogretmenler için
class CourseInline(admin.TabularInline):
    model = models.Course
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
@admin.register(models.Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "email", "created_at")
    search_fields = ("first_name", "last_name", "phone", "email")
    list_filter = ("created_at",)

@admin.register(models.StudentGuardian)
class StudentGuardianAdmin(admin.ModelAdmin):
    list_display = ("student", "guardian", "relation", "is_primary", "is_emergency_contact", "legal_custody")
    list_filter = ("relation", "is_primary", "is_emergency_contact", "legal_custody")
    search_fields = ("student__first_name", "student__last_name", "guardian__first_name", "guardian__last_name")
admin.site.register(models.Announcement)
admin.site.register(models.PaymentPlan)
admin.site.register(models.Discount)
admin.site.register(models.Invoice)
admin.site.register(models.Payment)
admin.site.register(models.Lead)
admin.site.register(models.Application)