# placement/admin.py
from django.contrib import admin
from .models import PlacementQuestion, PlacementChoice, PlacementTestResult

class PlacementChoiceInline(admin.TabularInline):
    model = PlacementChoice
    extra = 2

@admin.register(PlacementQuestion)
class PlacementQuestionAdmin(admin.ModelAdmin):
    list_display = ("id","skill","cefr_hint","is_active","short_text","created_at")
    list_filter  = ("skill","cefr_hint","is_active")
    search_fields = ("text",)
    inlines = [PlacementChoiceInline]

    def short_text(self, obj):
        return (obj.text[:80] + "…") if len(obj.text) > 80 else obj.text

@admin.register(PlacementTestResult)
class PlacementTestResultAdmin(admin.ModelAdmin):
    list_display = ("id","estimated_level","total_score","created_at","email")
    list_filter  = ("estimated_level", "created_at")
    search_fields = ("email",)
    readonly_fields = ("created_at","total_score","estimated_level","raw_payload","ua","ip_hash","skill_breakdown")
