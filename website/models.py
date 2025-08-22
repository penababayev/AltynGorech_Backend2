from django.db import models
from django.utils import timezone
from django.utils.text import slugify



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
