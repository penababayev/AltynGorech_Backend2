from django.db import models, transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator
from django.db import models, transaction, IntegrityError
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _



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
    name        = models.JSONField(_("Ders Adı"), blank=False, default=dict)                              # örn: Almanca
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

    subject   = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="courses", verbose_name="Sapagyň ady")
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


#---Room---
# courses/models.py  (veya uygun app)


class Room(models.Model):
    branch    = models.ForeignKey("core.Branch", on_delete=models.CASCADE,
                                  related_name="rooms", verbose_name="Şube")
    code      = models.CharField("Oda Kodu", max_length=32, blank=True, null=True, db_index=True)
    name      = models.CharField("Oda Adı", max_length=50)
    capacity  = models.PositiveIntegerField("Kapasite", default=20, validators=[MinValueValidator(1)])
    building  = models.CharField("Bina", max_length=60, blank=True)
    floor     = models.CharField("Kat", max_length=20, blank=True)
    features  = models.JSONField("Özellikler", default=list, blank=True)  # ["projector","whiteboard","ac"]
    is_active = models.BooleanField("Aktif", default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Synp/Otag"
        verbose_name_plural = "Synplar/Otaglar"
        ordering = ["branch", "name"]
        indexes = [
            models.Index(fields=["branch", "name"]),
            models.Index(fields=["branch", "is_active"]),
        ]
        unique_together = (("branch", "name"),)
        constraints = [
            # code opsiyonel; doluysa branch içinde benzersiz
            models.UniqueConstraint(
                fields=["branch", "code"],
                name="uniq_room_code_per_branch",
                condition=~Q(code=None)
            ),
        ]

    def __str__(self):
        return f"{self.branch} / {self.name}"

    # Basit doğrulama
    def clean(self):
        if self.capacity and self.capacity < 1:
            raise ValidationError({"capacity": "Kapasite 1 veya daha büyük olmalı."})

    # Otomatik kod üretimi: R-<BRANCHCODE|ID>-NN
    def _base_code(self) -> str:
        br_code = getattr(self.branch, "code", None)  # Branch'te code alanın varsa
        return f"R-{br_code}" if br_code else f"R-{self.branch_id}"

    def save(self, *args, **kwargs):
        # boş stringleri None yap
        if self.code == "":
            self.code = None

        if not self.code:
            base = self._base_code()
            seq = 1
            while True:
                candidate = f"{base}-{seq:02d}"
                # race condition'a karşı atomic blok
                try:
                    with transaction.atomic():
                        # aynı branch + candidate var mı?
                        if Room.objects.select_for_update().filter(branch=self.branch, code=candidate).exists():
                            seq += 1
                            if seq > 9999:
                                raise IntegrityError("Room code sequence overflow")
                            continue
                        self.code = candidate
                        break
                except IntegrityError:
                    seq += 1
                    if seq > 9999:
                        raise

        return super().save(*args, **kwargs)

    # Müsaitlik kontrolü (ClassSession ile)
    def is_available(self, date, start_time, end_time, exclude_session_id=None) -> bool:
        """
        Aynı odada aynı tarih & zaman aralığında çakışma var mı?
        Kullanım: room.is_available(date, start, end)
        """
        qs = self.sessions.filter(date=date)
        qs = qs.filter(Q(start_time__lt=end_time) & Q(end_time__gt=start_time))
        if exclude_session_id:
            qs = qs.exclude(id=exclude_session_id)
        return not qs.exists()
#---End Rooom ---



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







MATERIAL_STATUS = [
    ("DRAFT", "Taslak"),
    ("PUBLISHED", "Yayında"),
    ("ARCHIVED", "Arşiv"),
]

MATERIAL_VISIBILITY = [
    ("PUBLIC", "Herkes"),
    ("ENROLLED", "Kayıtlı Öğrenciler"),
    ("STAFF", "Sadece Personel"),
]

MATERIAL_TYPE = [
    ("FILE", "Dosya"),
    ("LINK", "Bağlantı"),
    ("VIDEO", "Video (YouTube/Vimeo)"),
    ("EMBED", "Gömülü (iframe/HTML)"),
    ("HTML", "Serbest Metin/HTML"),
]


def material_upload_to(instance, filename):
    """/materials/<org>/<course>/<yyyy>/<mm>/<filename>"""
    y = timezone.now().strftime("%Y")
    m = timezone.now().strftime("%m")
    org = instance.organization_id or "org"
    course = instance.course_id or "course"
    return f"materials/{org}/{course}/{y}/{m}/{filename}"


class Tag(models.Model):
    name = models.CharField(max_length=48, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(models.Model):
    # İlişkiler
    organization = models.ForeignKey("core.Organization", on_delete=models.CASCADE, related_name="materials")
    branch       = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="materials")
    course       = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="materials")
    owner        = models.ForeignKey("staffs.Teacher", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="owned_materials", verbose_name="Yükleyen")

    # İçerik
    title        = models.CharField("Başlık", max_length=180)
    code         = models.CharField("Kod", max_length=40, db_index=True, help_text="Kurum içinde benzersiz olmalı.")
    description  = models.TextField("Açıklama", blank=True)

    status       = models.CharField("Durum", max_length=10, choices=MATERIAL_STATUS, default="DRAFT", db_index=True)
    visibility   = models.CharField("Görünürlük", max_length=10, choices=MATERIAL_VISIBILITY, default="ENROLLED", db_index=True)
    material_type= models.CharField("Tür", max_length=8, choices=MATERIAL_TYPE, default="FILE", db_index=True)

    # Yayın penceresi
    publish_start_at = models.DateTimeField("Yayın Başlangıcı", null=True, blank=True)
    publish_end_at   = models.DateTimeField("Yayın Bitişi", null=True, blank=True)

    # Tür bazlı içerik alanları
    file = models.FileField(
        "Dosya", upload_to=material_upload_to, null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=[
            "pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx",
            "zip", "rar", "jpg", "jpeg", "png", "mp4", "mp3"
        ])]
    )
    link_url     = models.URLField("Bağlantı URL", blank=True)
    video_url    = models.URLField("Video URL", blank=True, help_text="YouTube/Vimeo gibi bir link.")
    embed_html   = models.TextField("Embed HTML", blank=True)
    html_content = models.TextField("Serbest Metin/HTML", blank=True)

    # Ek
    order        = models.PositiveIntegerField("Sıra", default=0, db_index=True)
    tags         = models.ManyToManyField(Tag, blank=True, related_name="materials")

    # Sayaçlar
    view_count     = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    # İzleme
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Materyal"
        verbose_name_plural = "Materyaller"
        unique_together = [("organization", "course", "code")]
        ordering = ["order", "-publish_start_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "course", "status"]),
            models.Index(fields=["visibility", "material_type"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.course}"

    def is_published_now(self) -> bool:
        """Şu an yayında mı? (admin listesinde kullanılacak)"""
        if self.status != "PUBLISHED":
            return False
        now = timezone.now()
        if self.publish_start_at and now < self.publish_start_at:
            return False
        if self.publish_end_at and now >= self.publish_end_at:
            return False
        return True

    def clean(self):
        # Yayın zamanı mantığı
        if self.publish_start_at and self.publish_end_at and self.publish_end_at <= self.publish_start_at:
            raise ValidationError({"publish_end_at": "Yayın bitişi, başlangıçtan sonra olmalı."})

        # Tür bazlı zorunlu alanlar
        t = self.material_type
        if t == "FILE" and not self.file:
            raise ValidationError({"file": "Dosya materyali için dosya yükleyin."})
        if t == "LINK" and not self.link_url:
            raise ValidationError({"link_url": "Link materyali için URL girin."})
        if t == "VIDEO" and not self.video_url:
            raise ValidationError({"video_url": "Video materyali için URL girin."})
        if t == "EMBED" and not self.embed_html:
            raise ValidationError({"embed_html": "Embed materyali için HTML girin."})
        if t == "HTML" and not self.html_content:
            raise ValidationError({"html_content": "HTML materyali için içerik girin."})


class MaterialFile(models.Model):
    """Materyale bağlı ek dosyalar (opsiyonel)."""
    material   = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="attachments")
    file       = models.FileField(upload_to=material_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.material.title} - {self.file.name}"





# --- Ölçme & Değerlendirme ---



ASSESSMENT_STATUS = [
    ("DRAFT", "Taslak"),
    ("PUBLISHED", "Yayında"),
    ("CLOSED", "Kapandı"),
    ("ARCHIVED", "Arşiv"),
]

class Assessment(models.Model):
    # Bağlantılar (app label'leri kendi projenize göre bırakın/değiştirin)
    organization = models.ForeignKey("core.Organization", on_delete=models.CASCADE, related_name="assessments")
    branch       = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments")
    course       = models.ForeignKey("courses.Course", on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments")

    # Temel bilgiler
    title       = models.CharField("Başlık", max_length=180)
    code        = models.CharField("Kod", max_length=40, db_index=True, help_text="Kurum içinde benzersiz olmalı.")
    description = models.TextField("Açıklama", blank=True)

    status      = models.CharField("Durum", max_length=12, choices=ASSESSMENT_STATUS, default="DRAFT", db_index=True)
    start_at    = models.DateTimeField("Başlangıç", null=True, blank=True)
    end_at      = models.DateTimeField("Bitiş", null=True, blank=True)
    duration_min= models.PositiveIntegerField("Süre (dk)", null=True, blank=True)
    capacity    = models.PositiveIntegerField("Kontenjan", null=True, blank=True)

    # Sınav yeri (fiziksel / online)
    is_online     = models.BooleanField("Online Sınav", default=False)
    meeting_url   = models.URLField("Toplantı/Sınav Linki", blank=True)
    venue_name    = models.CharField("Mekân Adı", max_length=160, blank=True)
    venue_address = models.TextField("Adres", blank=True)
    venue_room    = models.CharField("Salon/No", max_length=80, blank=True)
    venue_city    = models.CharField("Şehir", max_length=80, blank=True)
    venue_lat     = models.DecimalField("Enlem", max_digits=9, decimal_places=6, null=True, blank=True)
    venue_lng     = models.DecimalField("Boylam", max_digits=9, decimal_places=6, null=True, blank=True)
    map_embed_url = models.URLField("Harita Embed URL", blank=True)

    # Gözetmen(ler) – istersen kullan
    proctors = models.ManyToManyField("staffs.Teacher", blank=True, related_name="proctored_assessments", verbose_name="Gözetmenler")

    # Takip
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Synag"
        verbose_name_plural = "Synaglar"
        unique_together = [("organization", "code")]
        ordering = ["-start_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "branch", "status"]),
            models.Index(fields=["course", "start_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.code})"

    # Durum yardımcıları
    @property
    def is_open_now(self):
        now = timezone.now()
        if self.status != "PUBLISHED":
            return False
        if self.start_at and now < self.start_at:
            return False
        if self.end_at and now >= self.end_at:
            return False
        return True

    # Basit validasyonlar
    def clean(self):
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValidationError({"end_at": "Bitiş, başlangıçtan sonra olmalı."})

        # Yer zorunlulukları
        if self.is_online:
            if not self.meeting_url:
                raise ValidationError({"meeting_url": "Online sınavlar için bir bağlantı (meeting_url) belirtin."})
        else:
            if not (self.venue_name or self.venue_address):
                raise ValidationError("Fiziksel sınavlarda en azından bir mekân adı veya adres girin.")





ASSESSMENT_RESULT_STATUS = [
    ("REGISTERED", "Kayıtlı"),
    ("STARTED",    "Başladı"),
    ("SUBMITTED",  "Teslim Edildi"),
    ("GRADED",     "Notlandı"),
    ("ABSENT",     "Gelmedi"),
    ("CANCELLED",  "İptal"),
]

class AssessmentResult(models.Model):
    # Bağlantılar
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="results"
    )
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="assessment_results"
    )
    graded_by = models.ForeignKey(
        "staffs.Teacher", on_delete=models.SET_NULL, null=True, blank=True, related_name="graded_results"
    )

    # Deneme & durum
    attempt = models.PositiveIntegerField(default=1, help_text="Aynı sınav için kaçıncı deneme.")
    status  = models.CharField(max_length=12, choices=ASSESSMENT_RESULT_STATUS, default="REGISTERED", db_index=True)

    # Zamanlar
    registered_at = models.DateTimeField(auto_now_add=True)
    started_at    = models.DateTimeField(null=True, blank=True)
    submitted_at  = models.DateTimeField(null=True, blank=True)
    graded_at     = models.DateTimeField(null=True, blank=True)

    # Puanlama
    raw_score  = models.DecimalField("Ham Puan", max_digits=7, decimal_places=2, null=True, blank=True)
    max_score  = models.DecimalField("Maksimum Puan", max_digits=7, decimal_places=2, null=True, blank=True)
    percent    = models.DecimalField("Yüzde", max_digits=6, decimal_places=2, null=True, blank=True, help_text="Otomatik hesaplanır.")
    pass_mark  = models.DecimalField("Geçme Yüzdesi", max_digits=5, decimal_places=2, default=50.00, help_text="% cinsinden")
    passed     = models.BooleanField("Geçti", default=False)

    # Devamsızlık / notlar
    is_absent  = models.BooleanField("Devamsız", default=False)
    notes      = models.TextField("Değerlendirici Notu", blank=True)

    # İzleme
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Synag Netijesi"
        verbose_name_plural = "Synag Netijeleri"
        # Aynı assessment + student + attempt kombinasyonu tekil olsun
        unique_together = [("assessment", "student", "attempt")]
        indexes = [
            models.Index(fields=["assessment", "student"]),
            models.Index(fields=["status"]),
            models.Index(fields=["passed"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.assessment} (Attempt {self.attempt})"

    # Yardımcılar
    @property
    def duration_minutes(self):
        """STARTED → SUBMITTED arası dakika (varsa)."""
        if self.started_at and self.submitted_at:
            delta = self.submitted_at - self.started_at
            return max(0, int(delta.total_seconds() // 60))
        return None

    def clean(self):
        # ABSENT ise puanlanamaz
        if self.is_absent and (self.raw_score is not None or self.submitted_at):
            raise ValidationError("Devamsız (ABSENT) sonuç için puan/teslim zamanı olmamalı.")

        # Zaman sırası
        if self.started_at and self.submitted_at and self.submitted_at < self.started_at:
            raise ValidationError({"submitted_at": "Teslim zamanı, başlama zamanından önce olamaz."})

        # Puan mantığı
        if self.raw_score is not None and (self.max_score is None or self.max_score <= 0):
            raise ValidationError({"max_score": "Ham puan varsa maksimum puan > 0 olmalı."})
        if self.raw_score is not None and self.max_score is not None:
            if self.raw_score < 0 or self.raw_score > self.max_score:
                raise ValidationError({"raw_score": "Ham puan 0 ile maksimum puan arasında olmalı."})

        # Assessment penceresi (varsa) dışında başlatma/teslim etme uyarısı
        if self.started_at:
            a = self.assessment
            if a.start_at and self.started_at < a.start_at:
                raise ValidationError({"started_at": "Sınav başlangıç saatinden önce başlatılamaz."})
            if a.end_at and self.started_at >= a.end_at:
                raise ValidationError({"started_at": "Sınav bitiş saatinden sonra başlatılamaz."})
        if self.submitted_at:
            a = self.assessment
            if a.end_at and self.submitted_at > a.end_at:
                # İstersen burada uyarı yerine hata da verebilirsin
                pass

        # Kapasite kontrolünü kayıt (REGISTERED) sırasında yapmak istersen:
        # if self._state.adding and self.status == "REGISTERED":
        #     reg_count = AssessmentResult.objects.filter(assessment=self.assessment, status__in=["REGISTERED","STARTED","SUBMITTED","GRADED"]).count()
        #     if self.assessment.capacity and reg_count >= self.assessment.capacity:
        #         raise ValidationError("Bu sınav için kontenjan dolu.")

    def _compute_scores(self):
        """raw_score + max_score → percent ve passed hesapla."""
        if self.raw_score is not None and self.max_score:
            pct = (float(self.raw_score) / float(self.max_score)) * 100.0
            self.percent = round(pct, 2)
            self.passed = self.percent >= float(self.pass_mark)
        else:
            # Puan yoksa yüzde/passed reset
            self.percent = None
            if self.is_absent:
                self.passed = False

    def save(self, *args, **kwargs):
        # Durum otomasyonu
        if self.is_absent:
            self.status = "ABSENT"

        # Puan/Geçti hesapla
        self._compute_scores()

        # GRADED durumuna geçişte graded_at set et
        if self.status == "GRADED" and self.graded_at is None:
            self.graded_at = timezone.now()

        # STARTED yokken SUBMITTED geldiyse (ör. optikten içeri alındı), started_at tahmini vermiyoruz; isteğe bağlı eklenebilir
        super().save(*args, **kwargs)



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



