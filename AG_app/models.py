from django.db import models, transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
import uuid

# Create your models here.

#Teachers
class Teachers(models.Model):
    teacher_id = models.AutoField(primary_key = True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(null = True, blank = True)
    credentials = models.CharField(max_length=200, blank = True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
 
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

#Courses
# class Course(models.Model):
#     name = models.CharField(max_length=200)

#     def __str__(self):
#         return f'{self.name}'

#Course Items
# class CourseItem(models.Model):
#     item = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='items' )
#     name = models.CharField(max_length=200)
#     title = models.CharField(max_length=200)
#     description = models.TextField()

#     def __str__(self):
#         return f'{self.name} {self.title}'


# #Certificates
# class Certificate(models.Model):
#     LEVEL_CHOICES = [
#         ('Beginner', 'Beginner'),
#         ('Intermediate', 'Intermediate'),
#         ('Upper', 'Upper'),
#         ('Advanced', 'Advanced'),
#     ]

#     COURSE_CHOICES = [
#         ('Iňlis dili', 'Iňlis dili'),
#         ('Rus dili', 'Rus dili'),
#         ('Matematika', 'Matematika'),
#         ('Kompýuter', 'Kompýuter'),
#     ]

#     COURSE_LOC_CHOICES = [
#         ('Merkez Şahamçasy, Mary ş.', 'Merkez Şahamçasy, Mary ş.'),
#         ('Şapak Şahamçasy, Mary ş.', 'Şapak Şahamçasy, Mary ş.'),
#         ('Miras Şahamçasy, Mary ş.', 'Miras Şahamçasy, Mary ş.'),
#         ('Ýolöten Şahamçasy, Ýolöten ş.', 'Ýolöten Şahamçasy, Ýolöten ş.'),
#     ]


#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     fathers_name = models.CharField(max_length=100)
#     phone_num = models.CharField(max_length=12, default="+993") 
#     course_level = models.CharField(max_length=200, choices=LEVEL_CHOICES, default='Tapgyryny sayla')
#     course_name = models.CharField(max_length=200, choices=COURSE_CHOICES, default='Kurs adyny saýla')
#     course_location = models.CharField(max_length=200, choices=COURSE_LOC_CHOICES, default='Kurs ýeri' )
#     certificate = models.CharField(max_length=200)

#     def __str__(self):
#         return f'{self.first_name} {self.last_name} {self.fathers_name} {self.phone_num}'




#Profesyonel Dershane veritabani




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


# --- Akademik temel ---

class Subject(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        unique_together = ("organization", "name")
        indexes = [models.Index(fields=["organization", "name"])]

    def __str__(self):
        return self.name


class Room(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=20)

    class Meta:
        unique_together = ("branch", "name")
        indexes = [models.Index(fields=["branch", "name"])]

    def __str__(self):
        return f"{self.branch} / {self.name}"


class Course(models.Model):
    LEVEL_CHOICES = [
        ("BEGINNER", "Beginner"),
        ("INTERMEDIATE", "Intermediate"),
        ("UPPER", "Upper"),
        ("ADVANCED", "Advanced"),
    ]
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="courses")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="courses")
    name = models.CharField(max_length=150)  # Örn: TYT Matematik Hafta Sonu Grubu
    code = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="teaching_courses")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="BEGINNER")
    capacity = models.PositiveIntegerField(default=25)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["branch", "subject", "is_active"])]

    def __str__(self):
        return f"{self.name} ({self.branch})"


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


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "student")
        indexes = [models.Index(fields=["course", "student", "status"])]

    def __str__(self):
        return f"{self.student} -> {self.course}"


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


class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to="materials/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# --- Veli / İletişim ---

class Guardian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="guardian_profile")
    phone = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class StudentGuardian(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="guardian_links")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name="students")
    relation = models.CharField(max_length=50, blank=True, null=True)  # anne/baba/vasi

    class Meta:
        unique_together = ("student", "guardian")


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


# --- Muhasebe ---

class PaymentPlan(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="payment_plans")
    name = models.CharField(max_length=120)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    installments = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.course} - {self.name}"


class Discount(models.Model):
    name = models.CharField(max_length=120)
    percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Örn: %10 için 10.00")

    def __str__(self):
        return f"{self.name} %{self.percent}"


class Invoice(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="invoices")
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # indirimsiz/indirimli net tutar tercihinize göre
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.enrollment}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=30, default="CASH")  # CASH/CARD/TRANSFER

    def __str__(self):
        return f"Payment #{self.id} - Invoice {self.invoice_id}"


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
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=30, default="PENDING")  # PENDING/APPROVED/REJECTED
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lead", "course")
    




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

    # Veli
    guardian_name  = models.CharField("Veli Ad Soyad", max_length=120, blank=True, null=True)
    guardian_phone = models.CharField("Veli Telefon", max_length=40, blank=True, null=True)

    # Dershane bilgisi
    branch         = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="students", verbose_name="Şube")
    status         = models.CharField("Durum", max_length=12, choices=STATUS_CHOICES, default="ACTIVE")

    # Takip
    enrollment_date = models.DateField("Kayıt Tarihi", auto_now_add=True)
    notes           = models.TextField("Notlar", blank=True, null=True)

    class Meta:
        verbose_name = "Öğrenci"
        verbose_name_plural = "Öğrenciler"
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
