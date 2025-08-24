# placement/models.py
from django.db import models
from django.utils import timezone

CEFR = [("A1","A1"),("A2","A2"),("B1","B1"),("B2","B2"),("C1","C1")]

class PlacementQuestion(models.Model):
    SKILL = [("grammar","Grammar"), ("vocab","Vocabulary"), ("reading","Reading"), ("listening","Listening")]
    text        = models.TextField()
    skill       = models.CharField(max_length=12, choices=SKILL, default="grammar")
    cefr_hint   = models.CharField(max_length=2, choices=CEFR, blank=True)   # opsiyonel zorluk ipucu
    audio_url   = models.URLField(blank=True)                                 # listening varsa
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.skill}] {self.text[:60]}"

class PlacementChoice(models.Model):
    question    = models.ForeignKey(PlacementQuestion, on_delete=models.CASCADE, related_name="choices")
    text        = models.CharField(max_length=300)
    is_correct  = models.BooleanField(default=False)

    def __str__(self):
        return f"Q{self.question_id} -> {self.text[:40]}"

class PlacementTestResult(models.Model):
    email           = models.EmailField(blank=True)
    created_at      = models.DateTimeField(default=timezone.now)
    total_score     = models.PositiveIntegerField(default=0)
    estimated_level = models.CharField(max_length=2, choices=CEFR, blank=True)
    raw_payload     = models.JSONField(default=dict)   # {"answers":[{"q":id,"choice":id},...]}
    ua              = models.CharField(max_length=200, blank=True)
    ip_hash         = models.CharField(max_length=128, blank=True)

    # opsiyonel: beceri kırılımı kaydı
    skill_breakdown = models.JSONField(default=dict, blank=True)  # {"grammar":{"correct":x,"total":y}, ...}

    def __str__(self):
        return f"{self.estimated_level} ({self.total_score}) @ {self.created_at:%Y-%m-%d}"
