from django.contrib import admin
from .models import Teachers, ExamEvents, News

# Register your models here.

admin.site.register(Teachers)
admin.site.register(ExamEvents)
admin.site.register(News)
