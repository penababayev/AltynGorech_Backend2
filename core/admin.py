from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import DateWidget, Widget
from import_export.admin import ImportExportModelAdmin
from django.db.models import Count, Q
from . import models





@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)

@admin.register(models.Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("name",)

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "organization", "branch")
    list_filter = ("role", "organization", "branch")
    search_fields = ("user__username", "user__first_name", "user__last_name")


# admin.site.register(models.Announcement)
admin.site.register(models.Lead)
admin.site.register(models.Application)