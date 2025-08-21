from django.db import models, transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
# from staffs.models import *
# from students.models import *
from django.db import models, transaction, IntegrityError
from django.core.validators import MinValueValidator



# Create your models here.

# --- Akademik temel ---

class Subject(models.Model):
    LEVEL_CHOICES = [
        ("A1", "A1"),
        ("A2", "A2"),
        ("B1", "B1"),
        ("B2", "B2"),
        ("C1", "C1"),
        ("C2", "C2"),
        ("BEGINNER", "Beginner"),
        ("INTERMEDIATE", "Intermediate"),
        ("ADVANCED", "Advanced"),
    ]

    code        = models.CharField("Ders Kodu", max_length=32, unique=True, db_index=True)  # örn: GER-B2
    name        = models.CharField("Ders Adı", max_length=120)                              # örn: Almanca
    level       = models.CharField("Seviye", max_length=16, choices=LEVEL_CHOICES, blank=True)
    description = models.TextField("Açıklama", blank=True, null=True)
    is_active   = models.BooleanField("Aktif", default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)


    # organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="subjects")
    # name = models.CharField(max_length=120)
    # code = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = "Sapak"
        verbose_name_plural = "Sapaklar"
        unique_together = ("organization", "name")
        indexes = [
            models.Index(fields=["name", "level"]),
            models.Index(fields=["is_active"]),
        ]
        unique_together = [("name", "level")]  # aynı isim + seviye tekrar etmesin (isteğe bağlı)

    def __str__(self):
        return f"{self.name} ({self.level})" if self.level else self.name




# ---- Course ----
class Course(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Taslak"),
        ("OPEN", "Kayıta Açık"),
        ("FULL", "Kontenjan Dolu"),
        ("ONGOING", "Devam Ediyor"),
        ("COMPLETED", "Tamamlandı"),
        ("CANCELLED", "İptal"),
    ]

    subject   = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="courses", verbose_name="Konu")
    branch    = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="courses", verbose_name="Şube")
    teacher   = models.ForeignKey("staffs.Teacher", on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="courses", verbose_name="Eğitmen")

    title     = models.CharField("Kurs Başlığı", max_length=160, blank=True,
                                 help_text="Boş bırakılırsa genelde konu + seviye ile gösterilir.")
    course_code = models.CharField("Kurs Kodu", max_length=32, unique=True, db_index=True)  # örn: GER-B2-2025-01

    start_date = models.DateField("Başlangıç Tarihi", null=True, blank=True)
    end_date   = models.DateField("Bitiş Tarihi", null=True, blank=True)
    time_start = models.TimeField("Ders Başlangıç Saati", null=True, blank=True)
    time_end   = models.TimeField("Ders Bitiş Saati", null=True, blank=True)
    days_of_week = models.CharField(
        "Günler", max_length=32, blank=True,
        help_text="Örn: MON,WED,FRI (basit CSV). Postgres'te ArrayField tercih edebilirsin."
    )

    room      = models.CharField("Sınıf/Salon", max_length=64, blank=True)
    capacity  = models.PositiveIntegerField("Kontenjan", null=True, blank=True, validators=[MinValueValidator(1)])
    price     = models.DecimalField("Ücret", max_digits=10, decimal_places=2, null=True, blank=True)
    currency  = models.CharField("Para Birimi", max_length=8, default="EUR")

    status    = models.CharField("Durum", max_length=12, choices=STATUS_CHOICES, default="OPEN")
    is_active = models.BooleanField("Aktif", default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ["-start_date", "subject__name"]
        indexes = [
            models.Index(fields=["status", "is_active"]),
            models.Index(fields=["branch", "start_date"]),
            models.Index(fields=["subject", "teacher"]),
        ]
        # Şube + konu + öğretmen + başlangıç tarihi kombinasyonu tekrar etmesin (isteğe bağlı kural):
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "subject", "teacher", "start_date"],
                name="uniq_course_per_branch_subject_teacher_start",
                condition=models.Q(start_date__isnull=False),
            )
        ]

    def __str__(self):
        if self.title:
            return self.title
        base = str(self.subject)
        return f"{base} @ {self.branch}" if self.branch_id else base

    @property
    def active_enrollment_count(self) -> int:
        """
        Aktif kayıt sayısı. Senin Enrollment.status alanın Student.STATUS_CHOICES'ı kullanıyor.
        Bu nedenle 'ACTIVE' olanları sayıyoruz. İleride Enrollment için ayrı bir durum kümesi tanımlarsan güncelle.
        """
        return self.enrollments.filter(status="ACTIVE").count()

    @property
    def is_full(self) -> bool:
        if not self.capacity:
            return False
        return self.active_enrollment_count >= self.capacity

    def clean(self):
        # Basit tutarlılık kontrolleri
        if self.start_date and self.end_date and self.end_date < self.start_date:
            from django.core.exceptions import ValidationError
            raise ValidationError({"end_date": "Bitiş tarihi başlangıç tarihinden önce olamaz."})
        if self.time_start and self.time_end and self.time_end <= self.time_start:
            from django.core.exceptions import ValidationError
            raise ValidationError({"time_end": "Bitiş saati başlangıç saatinden sonra olmalı."})



     # ------- KOD ÜRETİMİ -------

    def _base_code(self) -> str:
        """SUBJECTCODE-YYYY temelini üretir."""
        subj_code = ""
        # Subject modelinde code alanın varsa onu kullan; yoksa id/isim fallback
        if hasattr(self.subject, "code") and self.subject.code:
            subj_code = self.subject.code.strip().upper().replace(" ", "")
        else:
            subj_code = f"SJ{self.subject_id}"
        year = (self.start_date.year if self.start_date else timezone.now().year)
        return f"{subj_code}-{year}"

    def _next_code_candidate(self, base: str, seq: int) -> str:
        return f"{base}-{seq:02d}"  # GER-B2-2025-01

    def save(self, *args, **kwargs):
        """
        Eğer course_code manuel verilmemişse, SUBJECTCODE-YYYY-XX formatında
        benzersiz bir kod üretir. Çakışma olursa IntegrityError yakalanır ve tekrar denenir.
        """
        # Güncel kaydı güncelliyorsak ve code zaten varsa, normal kaydet
        if self.pk and self.course_code:
            return super().save(*args, **kwargs)

        if not self.course_code:
            base = self._base_code()
            seq = 1
            # Çakışma ihtimaline karşı güvenli tekrar denemesi
            while True:
                candidate = self._next_code_candidate(base, seq)
                self.course_code = candidate
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    # başka bir işlem aynı anda aynı kodu üretmiş; bir sonraki numarayı dene
                    seq += 1
                    if seq > 9999:
                        # Aşırı sıra denemesi durumunda ham hatayı yükselt
                        raise
        else:
            return super().save(*args, **kwargs)




class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "student")
        indexes = [models.Index(fields=["course", "student", "status"])]

    def __str__(self):
        return f"{self.student} -> {self.course}"



class Room(models.Model):
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=20)

    class Meta:
        unique_together = ("branch", "name")
        indexes = [models.Index(fields=["branch", "name"])]

    def __str__(self):
        return f"{self.branch} / {self.name}"



class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["date", "start_time"]
        indexes = [models.Index(fields=["course", "date"])]

    def __str__(self):
        return f"{self.course.name} - {self.date} {self.start_time}-{self.end_time}"





    





class Attendance(models.Model):
    STATUS_CHOICES = [("PRESENT", "Present"), ("ABSENT", "Absent"), ("LATE", "Late"), ("EXCUSED", "Excused")]
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PRESENT")
    note = models.CharField(max_length=255, blank=True, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "student")
        indexes = [models.Index(fields=["session", "student"])]

    def __str__(self):
        return f"{self.session} - {self.student} - {self.status}"





class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to="materials/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




# --- Ölçme & Değerlendirme ---

class Assessment(models.Model):
    TYPE_CHOICES = [("EXAM", "Exam"), ("QUIZ", "Quiz"), ("ASSIGNMENT", "Assignment")]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="EXAM")
    date = models.DateField()
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)

    def __str__(self):
        return f"{self.course} - {self.title}"


class AssessmentResult(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessment_results")
    score = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("assessment", "student")
        indexes = [models.Index(fields=["assessment", "student"])]

    def __str__(self):
        return f"{self.assessment} - {self.student} : {self.score}"


# --- Ödev / Materyal ---

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course} - {self.title}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to="submissions/%Y/%m/")
    note = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ("assignment", "student")
        indexes = [models.Index(fields=["assignment", "student"])]

    def __str__(self):
        return f"{self.assignment} - {self.student}"



