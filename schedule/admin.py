from django.contrib import admin
from .models import TimetableEntry, TimetableException

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display  = ("id","title","course","branch","teacher","day_of_week","start_time","end_time","repeat_every","is_active")
    list_filter   = ("day_of_week","is_active","course","branch","teacher","is_online")
    search_fields = ("title","notes","room","course__name","branch__name","teacher__name")
    autocomplete_fields = ("course","branch","teacher")
    readonly_fields = ("created_at","updated_at")
    fieldsets = (
        ("Ders", {"fields": ("title","course","branch","teacher","capacity","notes","is_active")}),
        ("Zaman", {"fields": ("day_of_week","start_time","end_time","repeat_every","valid_from","valid_to")}),
        ("Yer/Online", {"fields": ("room","is_online","meeting_url")}),
        ("Sistem", {"classes": ("collapse",), "fields": ("created_at","updated_at")}),
    )

@admin.register(TimetableException)
class TimetableExceptionAdmin(admin.ModelAdmin):
    list_display  = ("id","entry","date","cancelled")
    list_filter   = ("cancelled", "date")
    search_fields = ("entry__title","note")
    autocomplete_fields = ("entry",)
