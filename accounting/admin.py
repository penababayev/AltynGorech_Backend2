from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import DateWidget, Widget
from import_export.admin import ImportExportModelAdmin
from django.db.models import Count, Q
from . import models

# Register your models here.
admin.site.register(models.PaymentPlan)
admin.site.register(models.Discount)
admin.site.register(models.Invoice)
admin.site.register(models.Payment)