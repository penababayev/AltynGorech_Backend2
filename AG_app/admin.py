from django.contrib import admin


from import_export import resources, fields
from import_export.widgets import DateWidget, Widget
from import_export.admin import ImportExportModelAdmin
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
    guardian_name   = fields.Field(column_name="Veli Ad Soyad", attribute="guardian_name")
    guardian_phone  = fields.Field(column_name="Veli Telefon", attribute="guardian_phone")
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
            "guardian_name",
            "guardian_phone",
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
    search_fields = ("student_number", "first_name", "last_name", "email", "phone", "guardian_name", "guardian_phone")
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

# Önemli diğerleri:
admin.site.register(models.Subject)
admin.site.register(models.Room)
admin.site.register(models.Course)
admin.site.register(models.ClassSession)
admin.site.register(models.Enrollment)
admin.site.register(models.Attendance)
admin.site.register(models.Assessment)
admin.site.register(models.AssessmentResult)
admin.site.register(models.Assignment)
admin.site.register(models.Submission)
admin.site.register(models.Material)
admin.site.register(models.Guardian)
admin.site.register(models.StudentGuardian)
admin.site.register(models.Announcement)
admin.site.register(models.PaymentPlan)
admin.site.register(models.Discount)
admin.site.register(models.Invoice)
admin.site.register(models.Payment)
admin.site.register(models.Lead)
admin.site.register(models.Application)