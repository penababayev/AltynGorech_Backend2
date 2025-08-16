from django.db import models

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
class Course(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'

#Course Items
class CourseItem(models.Model):
    item = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='items' )
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return f'{self.name} {self.title}'


#Certificates
class Certificate(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Upper', 'Upper'),
        ('Advanced', 'Advanced'),
    ]

    COURSE_CHOICES = [
        ('Iňlis dili', 'Iňlis dili'),
        ('Rus dili', 'Rus dili'),
        ('Matematika', 'Matematika'),
        ('Kompýuter', 'Kompýuter'),
    ]

    COURSE_LOC_CHOICES = [
        ('Merkez Şahamçasy, Mary ş.', 'Merkez Şahamçasy, Mary ş.'),
        ('Şapak Şahamçasy, Mary ş.', 'Şapak Şahamçasy, Mary ş.'),
        ('Miras Şahamçasy, Mary ş.', 'Miras Şahamçasy, Mary ş.'),
        ('Ýolöten Şahamçasy, Ýolöten ş.', 'Ýolöten Şahamçasy, Ýolöten ş.'),
    ]


    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=12, default="+993") 
    course_level = models.CharField(max_length=200, choices=LEVEL_CHOICES, default='Tapgyryny sayla')
    course_name = models.CharField(max_length=200, choices=COURSE_CHOICES, default='Kurs adyny saýla')
    course_location = models.CharField(max_length=200, choices=COURSE_LOC_CHOICES, default='Kurs ýeri' )
    certificate = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.fathers_name} {self.phone_num}'
