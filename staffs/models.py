from django.contrib.auth.models import User
from django.conf import settings
# from core.models import Branch

from django.db import models
from django.contrib.auth import get_user_model
import re


def normalize_phone(raw: str) -> str:
    """+ hariç tüm non-digit karakterleri temizle; E.164 gibi bir standarda yakınlaştır."""
    if not raw:
        return raw
    raw = raw.strip()
    if raw.startswith("+"):
        return "+" + re.sub(r"\D", "", raw[1:])
    return re.sub(r"\D", "", raw)




#--- Ögretmenler ---
User = get_user_model()

class Teacher(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Aktif"),
        ("ON_LEAVE", "İzinde"),
        ("INACTIVE", "Pasif"),
        ("LEFT", "Ayrıldı"),
    ]
    EMPLOYMENT_CHOICES = [
        ("FULL_TIME", "Tam Zamanlı"),
        ("PART_TIME", "Yarı Zamanlı"),
        ("CONTRACT", "Sözleşmeli"),
        ("FREELANCE", "Freelance"),
    ]

    # Opsiyonel: sisteme giriş yapacak kullanıcı ile 1–1 ilişki
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="teacher_profile", verbose_name="Kullanıcı"
    )

    # Kimlik
    first_name = models.CharField("Ad", max_length=80)
    last_name  = models.CharField("Soyad", max_length=80)
    title      = models.CharField("Unvan", max_length=80, blank=True, help_text="Örn: Almanca Eğitmeni")

    # İletişim
    email   = models.EmailField("E-posta", unique=True, null=True, blank=True)
    phone   = models.CharField("Telefon", max_length=40, unique=True)
    address = models.TextField("Adres", blank=True, null=True)

    # İlişkiler
    branch   = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="teachers", verbose_name="Şube")
    subjects = models.ManyToManyField("courses.Subject", blank=True,
                                      related_name="teachers", verbose_name="Verdiği Konular")

    # İş bilgileri
    employment_type = models.CharField("Çalışma Tipi", max_length=12,
                                       choices=EMPLOYMENT_CHOICES, default="FULL_TIME")
    status     = models.CharField("Durum", max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    hire_date  = models.DateField("İşe Başlama", null=True, blank=True)
    leave_date = models.DateField("Ayrılış", null=True, blank=True)

    # Opsiyonel
    hourly_rate = models.DecimalField("Saatlik Ücret", max_digits=8, decimal_places=2, null=True, blank=True)
    bio         = models.TextField("Hakkında", blank=True, null=True)

    # Takip
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mugallym"
        verbose_name_plural = "Mugallymlar"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["branch", "status"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        # En az bir iletişim bilgisi kuralı (istersen kaldırabilirsin)
        if not self.email and not self.phone:
            raise ValidationError("En az bir iletişim bilgisi (telefon veya e-posta) girilmelidir.")
        if self.leave_date and self.hire_date and self.leave_date < self.hire_date:
            raise ValidationError({"leave_date": "Ayrılış tarihi işe başlama tarihinden önce olamaz."})

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)




