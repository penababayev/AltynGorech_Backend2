from django.contrib import admin
from .models import *

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display  = ("teacher", "organization", "branch", "is_visible", "sort_order", "slug", "updated_at")
    list_filter   = ("organization", "branch", "is_visible")
    search_fields = ("teacher__first_name", "teacher__last_name", "title_override", "slug")
    autocomplete_fields = ("organization", "branch", "teacher")
    ordering      = ("sort_order", "teacher__last_name")






@admin.register(BranchWeb)
class BranchWebAdmin(admin.ModelAdmin):
    list_display  = ("display_title", "branch", "is_visible", "sort_order", "slug", "updated_at")
    list_filter   = ("is_visible",)
    search_fields = ("title_override", "slug", "branch__name", "branch__address")
    autocomplete_fields = ("branch",)
    ordering      = ("sort_order", "branch__name")

    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Bağlantı", {"fields": ("branch",)}),
        ("Görünüm", {"fields": ("title_override", "description", "photo", "photo_alt")}),
        ("İletişim", {"fields": ("address_override", "phone_override", "email_override")}),
        ("Harita", {"fields": ("map_lat", "map_lng", "map_embed_url")}),
        ("Yayın", {"fields": ("is_visible", "sort_order", "slug", "created_at", "updated_at")}),
    )
