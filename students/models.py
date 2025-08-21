from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
# from core.models import Branch
from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
import uuid
import re




# Create your models here.

def normalize_phone(raw: str) -> str:
    """+ hariç tüm non-digit karakterleri temizle; E.164 gibi bir standarda yakınlaştır."""
    if not raw:
        return raw
    raw = raw.strip()
    if raw.startswith("+"):
        return "+" + re.sub(r"\D", "", raw[1:])
    return re.sub(r"\D", "", raw)





# --- Ögrenciler ---

# def default_student_number():
#     # Otomatik benzersiz öğrenci numarası (8 haneli)
#     return uuid.uuid4().hex[:8].upper()




class StudentNumberSequence(models.Model):
    """
    Her okul_kodu + yıl için artan güvenli (transaction'lı) sayaç.
    Örn: BRN + 2025 -> last_seq 1,2,3... -> BRN-2025-0001
    """
    school_code = models.CharField(max_length=10)
    year = models.PositiveIntegerField()
    last_seq = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("school_code", "year")
        indexes = [models.Index(fields=["school_code", "year"])]

    def __str__(self):
        return f"{self.school_code}-{self.year}: {self.last_seq}"


def next_student_number(school_code: str, year: int) -> str:
    """
    Aynı anda birden fazla kayıt geldiğinde dahi çakışmasın diye
    DB kilidi ile (select_for_update) güvenli sıra üretir.
    """
    with transaction.atomic():
        seq, _created = (
            StudentNumberSequence.objects
            .select_for_update()
            .get_or_create(
                school_code=school_code,
                year=year,
                defaults={"last_seq": 0},
            )
        )
        seq.last_seq += 1
        seq.save(update_fields=["last_seq"])
        return f"{school_code}-{year}-{seq.last_seq:04d}"  # 4 hane: 0001, 0002, ...






class Student(models.Model):
    GENDER_CHOICES = [
        ("M", "Erkek"),
        ("F", "Kadın"),
        ("O", "Diğer/Belirtmek İstemiyorum"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Aktif"),
        ("GRADUATED", "Mezun"),
        ("SUSPENDED", "Donduruldu"),
        ("LEFT", "Ayrıldı"),
    ]

    # Otomatik üretilecek alan
    student_number = models.CharField(
        "Öğrenci No",
        max_length=24,            # BRN-2025-0001 gibi formlar için yeterli
        unique=True,
        editable=False,
        db_index=True,
        help_text="Biçim: KOD-YIL-XXXX (örn: BRN-2025-0001)",
    )

    first_name     = models.CharField("Ad", max_length=80)
    last_name      = models.CharField("Soyad", max_length=80)
    gender         = models.CharField("Cinsiyet", max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth  = models.DateField("Doğum Tarihi", blank=True, null=True)

    # İletişim
    email          = models.EmailField("E-posta", blank=True, null=True, unique=True)
    phone          = models.CharField("Telefon", max_length=40, blank=False, null=False, unique=True)
    address        = models.TextField("Adres", blank=True, null=True)

    # # Veli
    # guardian_name  = models.CharField("Veli Ad Soyad", max_length=120, blank=True, null=True)
    # guardian_phone = models.CharField("Veli Telefon", max_length=40, blank=True, null=True)

    # Dershane bilgisi
    branch         = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="students", verbose_name="Şube")
    status         = models.CharField("Durum", max_length=12, choices=STATUS_CHOICES, default="ACTIVE")

    # Takip
    enrollment_date = models.DateField("Kayıt Tarihi", auto_now_add=True)
    notes           = models.TextField("Notlar", blank=True, null=True)

    class Meta:
        verbose_name = "Okuwçy"
        verbose_name_plural = "Okuwçylar"
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["branch", "status"]),
        ]
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}({self.student_number})"

    def save(self, *args, **kwargs):
        # İLK KAYITTA otomatik numara ver. (Import'ta el ile numara verirsen korunur.)
        if not self.student_number:
            school_code = getattr(settings, "SCHOOL_CODE", "SCH").upper()
            year = timezone.now().year  # istersen enrollment_date.year kullanacak şekilde değiştirilebilir
            self.student_number = next_student_number(school_code, year)
        super().save(*args, **kwargs)






class Guardian(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="guardian_profile")
    first_name  = models.CharField("Ad", max_length=80)
    last_name   = models.CharField("Soyad", max_length=80)
    phone = models.CharField("Veli Telefon", max_length=40, blank=True, null=True)
    email       = models.EmailField("E-posta", blank=True, null=True, unique=False)
    address        = models.TextField("Adres", blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ene-Ata"
        verbose_name_plural = "Ene-Atalar"
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["phone"]),
        ]
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        # En az bir iletişim bilgisi: phone veya email zorunlu
        if not self.phone and not self.email:
            raise ValidationError("En az bir iletişim bilgisi (telefon veya e-posta) girilmelidir.")

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)


class StudentGuardian(models.Model):
    RELATION_CHOICES = [
        ("MOTHER", "Anne"),
        ("FATHER", "Baba"),
        ("SIBLING", "Kardeş"),
        ("RELATIVE", "Akraba"),
        ("GUARDIAN", "Yasal Veli"),
        ("OTHER", "Diğer"),
    ]



    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="guardian_links")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name="student_links")
    relation  = models.CharField("İlişki", max_length=16, choices=RELATION_CHOICES, default="GUARDIAN")
    is_primary = models.BooleanField("Birincil veli", default=False)
    is_emergency_contact = models.BooleanField("Acil durum kişisi", default=True)
    legal_custody = models.BooleanField("Yasal velayet", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Okuwçy–Hossary"
        verbose_name_plural = "Okuwçy–Hossarlary"
        unique_together = ("student", "guardian")
        indexes = [
            models.Index(fields=["student", "guardian"]),
            models.Index(fields=["student", "is_primary"]),
        ]
        # PostgreSQL kullanıyorsanız şu koşullu tekillik ile her öğrenciye 1 birincil veli kuralı:
        constraints = [
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(is_primary=True),
                name="uniq_primary_guardian_per_student",
            ),
        ]

    def __str__(self):
        return f"{self.student} ↔ {self.guardian} ({self.get_relaton_display() if hasattr(self,'get_relaton_display') else self.relation})"


