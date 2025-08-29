from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, viewsets, serializers
from rest_framework.decorators import action
from .serializers import TimetableEntrySerializer

from .models import TimetableEntry, TimetableException
from courses.models import ClassSession  # mevcut Session modelin
# NOT: Session modelini daha önce tanımlamıştık.



class WeeklyScheduleAPIView(APIView):
    """
    GET /api/schedule/weekly?week_start=YYYY-MM-DD&branch=&course=&teacher=
    Varsayılan week_start: mevcut haftanın Pazartesi'si.

    1) Haftalık programı al (varsayılan: içinde olunan haftanın Pazartesi’sinden itibaren):

    GET /api/schedule/weekly?branch=2&course=5&teacher=7
    2) Belirli bir haftanın programı:
    GET /api/schedule/weekly?week_start=2025-09-01&branch=2
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Filtreler
        qp = request.query_params
        branch = qp.get("branch")
        course = qp.get("course")
        teacher = qp.get("teacher")

        # Hafta başlangıcı
        today = timezone.localdate()
        if qp.get("week_start"):
            try:
                week_start = date.fromisoformat(qp["week_start"])
            except Exception:
                return Response({"detail":"week_start formatı YYYY-MM-DD olmalıdır."}, status=400)
        else:
            # içinde bulunduğumuz haftanın Pazartesi'si
            week_start = today - timedelta(days=today.weekday())

        week_days = [week_start + timedelta(days=i) for i in range(7)]
        # aktif timetable
        qs = TimetableEntry.objects.filter(is_active=True)
        if branch:  qs = qs.filter(branch_id=branch)
        if course:  qs = qs.filter(course_id=course)
        if teacher: qs = qs.filter(teacher_id=teacher)

        # valid_from / valid_to aralığına düşenler
        # (null ise sınırsız geçerli kabul ediyoruz)
        def _valid_on(entry, d):
            if entry.valid_from and d < entry.valid_from:
                return False
            if entry.valid_to and d > entry.valid_to:
                return False
            # repeat_every kontrolü: week_start baz alınır
            if entry.repeat_every and entry.repeat_every > 1:
                # entry'nin ilk geçerli haftası: valid_from (varsa) yoksa week_start
                base = entry.valid_from or week_start
                weeks_diff = (d - base).days // 7
                if weeks_diff % entry.repeat_every != 0:
                    return False
            return True

        # istisnaları mapleyelim
        exc_map = {}  # (entry_id, date) -> exception
        exceptions = TimetableException.objects.filter(date__range=(week_days[0], week_days[-1]))
        for e in exceptions:
            exc_map[(e.entry_id, e.date)] = e

        # çıktı: günlere göre dersler
        payload = {i: [] for i in range(7)}  # 0..6
        for entry in qs:
            dow = entry.day_of_week
            d = week_days[dow]
            if not _valid_on(entry, d):
                continue

            exc = exc_map.get((entry.id, d))
            if exc and exc.cancelled:
                continue  # o gün iptal

            # override saat/oda/url
            start_t = exc.override_start_time if exc and exc.override_start_time else entry.start_time
            end_t   = exc.override_end_time   if exc and exc.override_end_time   else entry.end_time
            room    = exc.override_room       if exc and exc.override_room       else entry.room
            meeting = exc.override_meeting_url if exc and exc.override_meeting_url else entry.meeting_url

            payload[dow].append({
                "entry_id": entry.id,
                "title": entry.title,
                "course": entry.course_id,
                "branch": entry.branch_id,
                "teacher": entry.teacher_id,
                "date": d.isoformat(),
                "start_time": start_t.strftime("%H:%M"),
                "end_time": end_t.strftime("%H:%M"),
                "room": room,
                "is_online": entry.is_online,
                "meeting_url": meeting,
                "capacity": entry.capacity,
                "notes": entry.notes,
                "exception_note": exc.note if exc else "",
            })

        # Gün adları ile döndür (0=Mon)
        day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        result = []
        for i in range(7):
            result.append({"weekday": i, "day_name": day_names[i], "date": week_days[i].isoformat(), "items": payload[i]})

        # limit opsiyonu (UI yükünü azaltmak için)
        try:
            limit = int(qp.get("limit", 500))
        except ValueError:
            limit = 500
        for day in result:
            day["items"] = day["items"][:max(1, min(limit, 1000))]

        return Response({"week_start": week_start.isoformat(), "days": result})

class TimetableEntryViewSet(viewsets.ModelViewSet):
    """
    Timetable CRUD + 'materialize' aksiyonu (opsiyonel)
    """
    queryset = TimetableEntry.objects.all()
    serializer_class = TimetableEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def materialize_sessions(self, request):
        """
        POST /api/timetable/materialize_sessions
        Body: { "from": "YYYY-MM-DD", "to": "YYYY-MM-DD", "branch":?, "course":?, "teacher":? }
        Verilen aralık için timetable'dan Session kayıtları üretir.
        """
        import itertools
        from datetime import date, timedelta

        b = request.data.get("branch")
        c = request.data.get("course")
        t = request.data.get("teacher")
        try:
            dfrom = date.fromisoformat(request.data.get("from"))
            dto   = date.fromisoformat(request.data.get("to"))
        except Exception:
            return Response({"detail":"from/to ISO (YYYY-MM-DD) olmalı."}, status=400)
        if dto < dfrom:
            return Response({"detail":"to, from'dan küçük olamaz."}, status=400)

        entries = TimetableEntry.objects.filter(is_active=True)
        if b: entries = entries.filter(branch_id=b)
        if c: entries = entries.filter(course_id=c)
        if t: entries = entries.filter(teacher_id=t)

        # İstisnalar
        exc_qs = TimetableException.objects.filter(date__range=(dfrom, dto))
        exc_map = {(e.entry_id, e.date): e for e in exc_qs}

        # gün gün dolaş
        created = 0
        cur = dfrom
        while cur <= dto:
            dow = cur.weekday()  # 0=Mon
            todays = [e for e in entries if e.day_of_week == dow]

            for entry in todays:
                # geçerlilik kontrolü
                if entry.valid_from and cur < entry.valid_from: 
                    continue
                if entry.valid_to and cur > entry.valid_to:
                    continue
                if entry.repeat_every and entry.repeat_every > 1:
                    base = entry.valid_from or dfrom
                    weeks_diff = (cur - base).days // 7
                    if weeks_diff % entry.repeat_every != 0:
                        continue

                exc = exc_map.get((entry.id, cur))
                if exc and exc.cancelled:
                    continue

                # override saat
                start_t = exc.override_start_time if exc and exc.override_start_time else entry.start_time
                end_t   = exc.override_end_time   if exc and exc.override_end_time   else entry.end_time

                kwargs = entry.to_session_kwargs(cur)
                kwargs["meeting_url"] = (exc.override_meeting_url or kwargs["meeting_url"]) if exc else kwargs["meeting_url"]
                kwargs["notes"] = (f"{kwargs['notes']} | {exc.note}" if (exc and exc.note) else kwargs["notes"])

                # saatleri override et
                tz = timezone.get_current_timezone()
                kwargs["start_at"] = timezone.make_aware(datetime.combine(cur, start_t), tz)
                kwargs["end_at"]   = timezone.make_aware(datetime.combine(cur, end_t), tz)

                # Aynı gün/başlangıçta zaten session var mı? (çakışma önleme)
                exists = ClassSession.objects.filter(
                    course_id=entry.course_id,
                    branch_id=entry.branch_id,
                    teacher_id=entry.teacher_id,
                    start_at=kwargs["start_at"],
                    end_at=kwargs["end_at"],
                    title=entry.title,
                ).exists()
                if not exists:
                    ClassSession.objects.create(**kwargs)
                    created += 1
            cur += timedelta(days=1)

        return Response({"created": created})
