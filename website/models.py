from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError


#-----Ogretmen-----
def teacher_image_upload_path(instance, filename):
    return f"website/teachers/{timezone.now():%Y/%m}/{filename}"

def _unique_slugify(instance, base_value, max_length=140):
    base = slugify(base_value)[:max_length].strip("-") or "teacher"
    slug = base
    i = 2
    Model = instance.__class__
    filters = {"slug": slug}
    # organization bazında benzersiz yap
    if instance.organization_id:
        filters["organization_id"] = instance.organization_id
    while Model.objects.filter(**filters).exists():
        suffix = f"-{i}"
        slug = (base[: max_length - len(suffix)] + suffix).strip("-")
        filters["slug"] = slug
        i += 1
    instance.slug = slug

class TeacherProfile(models.Model):
    """
    Web sitesinde gösterilecek öğretmen vitrin kartı.
    """
    organization = models.ForeignKey("core.Organization", on_delete=models.CASCADE,
                                     related_name="teacher_profiles")
    branch       = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="teacher_profiles")
    teacher      = models.ForeignKey("staffs.Teacher", on_delete=models.CASCADE,
                                     related_name="web_profiles")

    title_override = models.CharField("Unvan (Web)", max_length=120, blank=True)
    bio_public     = models.TextField("Kısa Biyografi", blank=True)

    photo     = models.ImageField(upload_to=teacher_image_upload_path, blank=True, null=True)
    photo_alt = models.CharField("Foto ALT", max_length=160, blank=True)

    slug       = models.SlugField(max_length=140, db_index=True, blank=True)
    is_visible = models.BooleanField("Yayında", default=True)
    sort_order = models.PositiveIntegerField("Sıra", default=100, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("organization", "slug"),)
        indexes = [
            models.Index(fields=["organization", "is_visible", "sort_order"]),
            models.Index(fields=["organization", "branch", "is_visible"]),
        ]
        ordering = ["sort_order", "teacher__last_name"]
        verbose_name = "Öğretmen Profili"
        verbose_name_plural = "Öğretmen Profilleri"

    def __str__(self):
        return f"{getattr(self.teacher, 'full_name', str(self.teacher))} (Web)"

    def _slug_source(self):
        base = self.title_override or ""
        if not base:
            # staffs.Teacher'da full_name yoksa ad-soyad kullan
            t = self.teacher
            base = getattr(t, "full_name", f"{getattr(t, 'first_name', '')} {getattr(t, 'last_name', '')}".strip())
        return base or "teacher"

    def save(self, *args, **kwargs):
        if not self.slug:
            _unique_slugify(self, self._slug_source())
        super().save(*args, **kwargs)

#-----Ogretmen ------







def branch_image_upload_path(instance, filename):
    return f"website/branches/{timezone.now():%Y/%m}/{filename}"

class BranchWeb(models.Model):
    """
    Web sitesinde gösterilecek şube kartı (Branch verisini besler,
    web'e özel alanlar ekler). Her Branch için en fazla 1 kayıt.
    """
    branch = models.OneToOneField(
        "core.Branch", on_delete=models.CASCADE, related_name="website_profile"
    )

    # Web'e özel alanlar (override edilebilen)
    title_override   = models.CharField("Başlık (Web)", max_length=140, blank=True)
    description      = models.TextField("Açıklama (Web)", blank=True)
    address_override = models.CharField("Adres (Web)", max_length=255, blank=True)
    phone_override   = models.CharField("Telefon (Web)", max_length=40, blank=True)
    email_override   = models.EmailField("E-posta (Web)", blank=True)

    # Harita ve görsel
    photo        = models.ImageField(upload_to=branch_image_upload_path, blank=True, null=True)
    photo_alt    = models.CharField("Görsel ALT", max_length=160, blank=True)
    map_lat      = models.DecimalField("Enlem", max_digits=9, decimal_places=6, null=True, blank=True)
    map_lng      = models.DecimalField("Boylam", max_digits=9, decimal_places=6, null=True, blank=True)
    map_embed_url= models.URLField("Harita Embed URL", blank=True)

    # Yayınlama
    slug       = models.SlugField(max_length=140, unique=True, blank=True, db_index=True)
    is_visible = models.BooleanField("Yayında", default=True)
    sort_order = models.PositiveIntegerField("Sıra", default=100, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Şube (Web)"
        verbose_name_plural = "Şubeler (Web)"
        ordering = ["sort_order", "branch__name"]
        indexes = [
            models.Index(fields=["is_visible", "sort_order"]),
        ]

    def __str__(self):
        return self.display_title

    # ---- Okunabilir alanlar (override varsa onu kullan) ----
    @property
    def display_title(self):
        return self.title_override or getattr(self.branch, "name", f"Şube #{self.branch_id}")

    @property
    def display_address(self):
        return self.address_override or getattr(self.branch, "address", "")

    @property
    def display_phone(self):
        return self.phone_override or getattr(self.branch, "phone", "")

    @property
    def display_email(self):
        return self.email_override or getattr(self.branch, "email", "")

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.display_title or f"sube-{self.branch_id}"
            base = slugify(base) or f"sube-{self.branch_id}"
            slug = base
            i = 2
            while BranchWeb.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)



#Course Items
class CourseItem(models.Model):
    subject = models.ForeignKey("courses.Subject", on_delete=models.CASCADE, related_name='items', verbose_name="Sapagyň ady" )
    name = models.JSONField("Sapagyň kurs adlandyrmalary", blank=False, default=dict)
    description = models.JSONField(
        _("Açyklama"),
        blank=False,           # formda boş bırakılabilir
        default=dict,           # mevcut kayıtlara migration'da sorun çıkarmaz
        help_text=_("Kursuň giňişleýin açyklamasy"))
    

    class Meta:
        verbose_name = "Okuw (Web)"
        verbose_name_plural = "Okuwlar (Web)"

    def __str__(self):
        return f'{self.subject} {self.name}'






#----Announcements -------

# announcements/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

AUDIENCE = [
    ("PUBLIC",   "Public (Herkes)"),
    ("STUDENTS", "Öğrenciler"),
    ("TEACHERS", "Öğretmenler"),
    ("ENROLLED", "Kayıtlı Öğrenciler"),
    ("STAFF",    "Personel"),
]

STATUS = [
    ("DRAFT",     "Taslak"),
    ("SCHEDULED", "Zamanlanmış"),
    ("PUBLISHED", "Yayında"),
    ("ARCHIVED",  "Arşiv"),
]

PRIORITY = [
    ("INFO",    "Bilgi"),
    ("SUCCESS", "Başarılı"),
    ("WARNING", "Uyarı"),
    ("DANGER",  "Acil"),
]

def announcement_upload_to(instance, filename):
    y = timezone.now().strftime("%Y")
    m = timezone.now().strftime("%m")
    org = getattr(instance, "organization_id", None) or "org"
    return f"website/announcements/{org}/{y}/{m}/{filename}"

class Announcement(models.Model):
    # İlişkiler
    organization = models.ForeignKey("core.Organization", on_delete=models.CASCADE, related_name="announcements")
    branch       = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="announcements")
    course       = models.ForeignKey("courses.Course", on_delete=models.SET_NULL, null=True, blank=True, related_name="announcements")
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_announcements")

    # İçerik
    title     = models.CharField("Başlık", max_length=160)
    body      = models.TextField("İçerik", blank=True)
    link_url  = models.URLField("Bağlantı", blank=True)

    audience  = models.CharField("Hedef", max_length=10, choices=AUDIENCE, default="PUBLIC", db_index=True)
    status    = models.CharField("Durum",  max_length=10, choices=STATUS, default="DRAFT", db_index=True)
    priority  = models.CharField("Öncelik", max_length=10, choices=PRIORITY, default="INFO", db_index=True)
    pinned    = models.BooleanField("Üste Sabitle", default=False)
    is_active = models.BooleanField("Aktif", default=True)

    # Yayın penceresi
    publish_start_at = models.DateTimeField("Yayın Başlangıcı", null=True, blank=True)
    publish_end_at   = models.DateTimeField("Yayın Bitişi", null=True, blank=True)

    # Sayaç
    view_count = models.PositiveIntegerField(default=0)

    # İzleme
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Duyuru"
        verbose_name_plural = "Duyurular"
        ordering = ["-pinned", "-publish_start_at", "-created_at"]
        indexes = [
            models.Index(fields=["audience", "status", "is_active"]),
            models.Index(fields=["branch", "course"]),
            models.Index(fields=["pinned", "priority"]),
        ]

    def __str__(self):
        scope = self.branch or self.course or "Global"
        return f"{self.title} ({scope})"

    def clean(self):
        if self.publish_start_at and self.publish_end_at and self.publish_end_at <= self.publish_start_at:
            raise ValidationError({"publish_end_at": "Bitiş, başlangıçtan sonra olmalı."})

    @property
    def is_published_now(self) -> bool:
        if self.status != "PUBLISHED" or not self.is_active:
            return False
        now = timezone.now()
        if self.publish_start_at and now < self.publish_start_at:
            return False
        if self.publish_end_at and now >= self.publish_end_at:
            return False
        return True

class AnnouncementImage(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="images")
    image   = models.ImageField(upload_to=announcement_upload_to)
    caption = models.CharField("Başlık/Alt Yazı", max_length=160, blank=True)
    alt     = models.CharField("Alt Metin (SEO/erişilebilirlik)", max_length=160, blank=True)
    order   = models.PositiveIntegerField("Sıra", default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["announcement","order"])]

    def __str__(self):
        return self.caption or self.image.name

class AnnouncementAttachment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=announcement_upload_to)
    name = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name or self.file.name







# events/models.py


AUDIENCE = [
    ("PUBLIC",   "Public (Herkes)"),
    ("STUDENTS", "Öğrenciler"),
    ("TEACHERS", "Öğretmenler"),
    ("ENROLLED", "Kayıtlı Öğrenciler"),
    ("STAFF",    "Personel"),
]

STATUS = [
    ("DRAFT",     "Taslak"),
    ("SCHEDULED", "Zamanlanmış"),
    ("PUBLISHED", "Yayında"),
    ("CANCELLED", "İptal"),
    ("ARCHIVED",  "Arşiv"),
]

PRIORITY = [
    ("INFO",    "Bilgi"),
    ("SUCCESS", "Başarılı"),
    ("WARNING", "Uyarı"),
    ("DANGER",  "Acil"),
]

def event_upload_to(instance, filename):
    y = timezone.now().strftime("%Y")
    m = timezone.now().strftime("%m")
    org = getattr(instance, "organization_id", None) or "org"
    return f"website/events/{org}/{y}/{m}/{filename}"

class Event(models.Model):
    # İlişkiler
    organization = models.ForeignKey("core.Organization", on_delete=models.CASCADE, related_name="events")
    branch       = models.ForeignKey("core.Branch", on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    course       = models.ForeignKey("courses.Course", on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_events")

    # İçerik
    title       = models.CharField("Başlık", max_length=160)
    description = models.TextField("Açıklama", blank=True)
    link_url    = models.URLField("Dış Bağlantı", blank=True)

    audience  = models.CharField("Hedef", max_length=10, choices=AUDIENCE, default="PUBLIC", db_index=True)
    status    = models.CharField("Durum",  max_length=10, choices=STATUS, default="DRAFT", db_index=True)
    priority  = models.CharField("Öncelik", max_length=10, choices=PRIORITY, default="INFO", db_index=True)
    pinned    = models.BooleanField("Üste Sabitle", default=False)
    is_active = models.BooleanField("Aktif", default=True)

    # Etkinlik zamanı
    start_at = models.DateTimeField("Başlangıç", db_index=True)
    end_at   = models.DateTimeField("Bitiş", null=True, blank=True)

    # Yayın penceresi (siteye ne zaman düşsün?)
    publish_start_at = models.DateTimeField("Yayın Başlangıcı", null=True, blank=True)
    publish_end_at   = models.DateTimeField("Yayın Bitişi", null=True, blank=True)

    # Mekân / Online
    is_online   = models.BooleanField("Online", default=False)
    meeting_url = models.URLField("Toplantı Linki", blank=True)
    venue_name    = models.CharField("Mekân Adı", max_length=160, blank=True)
    venue_address = models.TextField("Adres", blank=True)
    venue_city    = models.CharField("Şehir", max_length=80, blank=True)
    venue_room    = models.CharField("Salon/No", max_length=80, blank=True)

    # Kapasite
    capacity   = models.PositiveIntegerField("Kapasite", null=True, blank=True)

    # Sayaç
    view_count = models.PositiveIntegerField(default=0)

    # İzleme
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Etkinlik"
        verbose_name_plural = "Etkinlikler"
        ordering = ["-pinned", "start_at", "-created_at"]
        indexes = [
            models.Index(fields=["audience", "status", "is_active"]),
            models.Index(fields=["branch", "course"]),
            models.Index(fields=["start_at"]),
            models.Index(fields=["pinned", "priority"]),
        ]

    def __str__(self):
        scope = self.branch or self.course or "Global"
        return f"{self.title} ({scope}) @ {self.start_at:%Y-%m-%d}"

    # Doğrulamalar
    def clean(self):
        if self.end_at and self.end_at <= self.start_at:
            raise ValidationError({"end_at": "Bitiş, başlangıçtan sonra olmalı."})
        if self.publish_start_at and self.publish_end_at and self.publish_end_at <= self.publish_start_at:
            raise ValidationError({"publish_end_at": "Yayın bitişi, yayın başlangıcından sonra olmalı."})

        if self.is_online:
            if not self.meeting_url:
                raise ValidationError({"meeting_url": "Online etkinlik için toplantı linki zorunludur."})
        else:
            if not (self.venue_name or self.venue_address):
                raise ValidationError("Fiziksel etkinlik için en az mekân adı veya adres girin.")

    # Durum yardımcıları
    @property
    def is_published_now(self) -> bool:
        if self.status != "PUBLISHED" or not self.is_active:
            return False
        now = timezone.now()
        if self.publish_start_at and now < self.publish_start_at:
            return False
        if self.publish_end_at and now >= self.publish_end_at:
            return False
        return True

    @property
    def is_live_now(self) -> bool:
        now = timezone.now()
        if self.end_at:
            return self.start_at <= now < self.end_at
        return now >= self.start_at

    @property
    def is_upcoming(self) -> bool:
        return timezone.now() < self.start_at

class EventImage(models.Model):
    event   = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image   = models.ImageField(upload_to=event_upload_to)
    caption = models.CharField("Başlık/Alt Yazı", max_length=160, blank=True)
    alt     = models.CharField("Alt Metin (SEO/erişilebilirlik)", max_length=160, blank=True)
    order   = models.PositiveIntegerField("Sıra", default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["event","order"])]

    def __str__(self):
        return self.caption or self.image.name

class EventAttachment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attachments")
    file  = models.FileField(upload_to=event_upload_to)
    name  = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name or self.file.name
