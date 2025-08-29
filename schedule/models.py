from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time

# Varsayıyoruz: Course, Branch, Teacher ve Session modellerin mevcut.
# Session: start_at, end_at, course, branch, teacher, title, is_online, meeting_url, capacity, notes, is_active

WEEKDAY_CHOICES = (
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
)

class TimetableEntry(models.Model):
    """
    Haftalık tekrar eden ders kalemi:
    - Gün: day_of_week (0=Mon)
    - Saat: start_time, end_time
    - Geçerlilik aralığı: valid_from, valid_to (opsiyonel)
    - Tekrar: repeat_every (hafta)
    """
    course  = models.ForeignKey("courses.Course",  on_delete=models.CASCADE, related_name="timetable_entries")
    branch  = models.ForeignKey("core.Branch",  on_delete=models.CASCADE, related_name="timetable_entries", null=True, blank=True)
    teacher = models.ForeignKey("staffs.Teacher", on_delete=models.SET_NULL,   related_name="timetable_entries", null=True, blank=True)

    title = models.CharField(max_length=200, help_text="Örn: Matematik - Trigonometri")
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time  = models.TimeField()
    end_time    = models.TimeField()

    room = models.CharField(max_length=80, blank=True)
    is_online   = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True)

    capacity = models.PositiveIntegerField(default=0)
    notes    = models.CharField(max_length=255, blank=True)

    # Tekrarlama ve geçerlilik
    repeat_every = models.PositiveIntegerField(default=1, help_text="Hafta sayısı (1=her hafta)")
    valid_from = models.DateField(null=True, blank=True)
    valid_to   = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        indexes = [
            models.Index(fields=["day_of_week", "start_time"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["course"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["teacher"]),
        ]

    def __str__(self):
        return f"{self.title} • {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("end_time, start_time'tan sonra olmalıdır.")
        if self.is_online and not self.meeting_url:
            raise ValidationError("Online dersler için meeting_url gereklidir.")
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValidationError("valid_to, valid_from’tan önce olamaz.")
        if self.repeat_every < 1:
            raise ValidationError("repeat_every en az 1 olmalıdır.")

    # ---- yardımcı: belirli bir tarih için Session alanlarını hazırla ----
    def to_session_kwargs(self, for_date):
        """
        for_date: date (o haftanın ilgili günü)
        """
        tz = timezone.get_current_timezone()
        start_dt = timezone.make_aware(datetime.combine(for_date, self.start_time), tz)
        end_dt   = timezone.make_aware(datetime.combine(for_date, self.end_time), tz)
        return dict(
            title=self.title,
            course_id=self.course_id,
            branch_id=self.branch_id,
            teacher_id=self.teacher_id,
            start_at=start_dt,
            end_at=end_dt,
            is_online=self.is_online,
            meeting_url=self.meeting_url or "",
            capacity=self.capacity,
            notes=self.notes,
            is_active=True,
        )

class TimetableException(models.Model):
    """
    Tek bir tarih için iptal/taşıma/üzerine yazma.
    """
    entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name="exceptions")
    date = models.DateField()
    cancelled = models.BooleanField(default=False)

    override_start_time = models.TimeField(null=True, blank=True)
    override_end_time   = models.TimeField(null=True, blank=True)
    override_room       = models.CharField(max_length=80, blank=True)
    override_meeting_url = models.URLField(blank=True)

    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("entry", "date")
        indexes = [
            models.Index(fields=["entry", "date"]),
        ]

    def __str__(self):
        tag = "Cancelled" if self.cancelled else "Override"
        return f"{self.entry} @ {self.date} ({tag})"
