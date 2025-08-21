from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
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





 
#Exam Events
class ExamEvents(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} on {self.date}"
    
#Exam Venues
class ExamVenues(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.name


#Contact/Inquiry
class Contacts(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)


#News
class News(models.Model):
    name = models.CharField(max_length=200)
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='news/', blank=True, null=True)

    def __str__(self):
        return f'{self.name}  {self.created_at} {self.image}'
    
    def delete(self):
        self.image.delete()
        super().delete()

    
#Activity
class Activity(models.Model):
    name = models.CharField(max_length=200)
    title = models.TextField()

    image = models.ImageField(upload_to='activity/', blank=True, null=True)
    def __str__(self):
        return f'{self.name}'
    
    def delete(self):
        self.image.delete()
        super().delete()


#Videos
class Video(models.Model):
    caption = models.CharField(max_length=100)
    video = models.FileField(upload_to="video/%Y/%M")

    def __str__(self):
        return f'{self.caption}'


#Adress/Location
class Adress(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    address = models.TextField()
    phone_num = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name} {self.title}'






# --- Kurumsal yapı ---
class Organization(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    tax_number = models.CharField(max_length=32, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class Branch(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Şahamça"
        verbose_name_plural = "Şahamçalar"
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "name"])]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


# --- Kullanıcı profili / roller ---

class Profile(models.Model):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("TEACHER", "Teacher"),
        ("STUDENT", "Student"),
        ("PARENT", "Parent/Guardian"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="STUDENT")
    phone = models.CharField(max_length=32, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"











class Announcement(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=150)
    body = models.TextField()
    visible_to = models.CharField(max_length=30, default="ALL")  # ALL/TEACHERS/STUDENTS/PARENTS
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="announcements_created")
    created_at = models.DateTimeField(auto_now_add=True)
    publish_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title








# --- CRM / Aday (opsiyonel) ---

class Lead(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="leads")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)  # referans, sosyal medya vb.
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default="NEW")  # NEW/CONTACTED/ENROLLED/LOST

    def __str__(self):
        return self.full_name


class Application(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="applications")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=30, default="PENDING")  # PENDING/APPROVED/REJECTED
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lead", "course")
    










