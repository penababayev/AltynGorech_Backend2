from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from courses.models import *
from courses.serializers import *
from students.models import *
from students.serializers import *
import re
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # istersen
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Q
from .models import Event
from .serializers import EventOut




# Create your views here.




class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.select_related("organization", "branch", "teacher")
    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "organization": ["exact"],
        "branch": ["exact"],
        "teacher": ["exact"],
        "is_visible": ["exact"],
        "slug": ["exact"],
    }
    search_fields   = ["teacher__first_name", "teacher__last_name", "title_override", "slug"]
    ordering_fields = ["sort_order", "created_at"]
    ordering        = ["sort_order", "teacher__last_name"]

    @action(detail=False, methods=["get"])
    def public(self, request):
        """
        Yayında olan öğretmenleri (vitrin) döner.
        /api/website/teachers/public/?organization=<id>&branch=<id>
        """
        qs = self.filter_queryset(self.get_queryset()).filter(is_visible=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        return Response(self.get_serializer(qs, many=True).data, status=status.HTTP_200_OK)







class BranchWebViewSet(viewsets.ModelViewSet):
    """
    /api/website/subeler/  (CRUD)
    /api/website/subeler/public/  (sadece yayında olanlar)
    """
    queryset = BranchWeb.objects.select_related("branch", "branch__organization")
    serializer_class = BranchWebSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "is_visible": ["exact"],
        "branch": ["exact"],
        "branch__organization": ["exact"],
        "slug": ["exact"],
    }
    search_fields   = ["title_override", "slug", "branch__name", "branch__address"]
    ordering_fields = ["sort_order", "created_at"]
    ordering        = ["sort_order", "branch__name"]

    @action(detail=False, methods=["get"])
    def public(self, request):
        qs = self.filter_queryset(self.get_queryset()).filter(is_visible=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        return Response(self.get_serializer(qs, many=True).data, status=status.HTTP_200_OK)










# Create your views here.


#StudentLookupByPhone

def normalize_phone(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("+"):
        return "+" + re.sub(r"\D", "", raw[1:])
    # Örn. yerel formatları + ülke koduna çevirmek istersen burada mantık ekleyebilirsin.
    return re.sub(r"\D", "", raw)


class StudentLookupByPhone(APIView):
    """
    GET /api/students/lookup?phone=+49...  (veya 0532..., 532..., vs.)
    JSON:
    - found: bool
    - message: str
    - student: {...} (found=True ise)
    - enrolled: bool
    - enrollments: [ { id, course:{id,name}, status, enrolled_at }, ... ]
    """

    def get(self, request, *args, **kwargs):
        phone = request.query_params.get("phone")
        if not phone:
            return Response(
                {"detail": "Telefon nomeri ýazmadyňyz, nomer hökmanydyr!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized = normalize_phone(phone)

        try:
            student = (
                Student.objects.select_related("branch")
                .get(phone=normalized)
            )
        except Student.DoesNotExist:
            # İstersen 404 yerine 200 + found:false döndürüp UI'ı basitleştirebilirsin.
            return Response(
                {
                    "found": False,
                    "message": "Bu nomerde registrasiya edilen okuwcy tapylmady",
                    "phone": phone,
                },
                status=status.HTTP_200_OK,
            )

        enrollments_qs = (
            Enrollment.objects
            .filter(student=student)
            .select_related("course")
            .order_by("-enrolled_at")
        )

        student_data = StudentSerializer(student).data
        enrollments_data = EnrollmentSerializer(enrollments_qs, many=True).data
        enrolled = len(enrollments_data) > 0

        return Response(
            {
                "found": True,
                "message": "Okuwcy tapyldy we maglumatlary sergilendi."
                if enrolled
                else "Okuwcy tapyldy, emma hic hili kursa registrasiya edilmedik",
                "student": student_data,
                "enrolled": enrolled,
                "enrollments": enrollments_data,
            },
            status=status.HTTP_200_OK,
        )









class AssessmentResultViewSet(viewsets.ModelViewSet):
    queryset = AssessmentResult.objects.select_related(
        "assessment", "student", "graded_by"
    ).all()
    serializer_class = AssessmentResultSerializer
    permission_classes = [IsAuthenticated]  # projene göre güncelle

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "assessment": ["exact"],
        "student": ["exact"],
        "status": ["exact"],
        "passed": ["exact"],
    }
    search_fields = ["assessment__title", "assessment__code", "notes", "student__first_name", "student__last_name"]
    ordering_fields = ["created_at", "updated_at", "percent", "attempt"]
    ordering = ["-created_at"]



class CourseListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]




class CourseItemViewSet(viewsets.ModelViewSet):
    queryset = CourseItem.objects.select_related("subject")
    serializer_class = CourseItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        """
        /api/courses/<pk>/items/
        """
        course = self.get_object()  # 404'ü DRF otomatik verir
        qs = course.items.all().order_by("id")  # varsa sort_order ekleyebilirsin
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = CourseItemSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(ser.data)
        ser = CourseItemSerializer(qs, many=True, context={"request": request})
        return Response(ser.data, status=status.HTTP_200_OK)
    



# announcements/api.py


def announcement_base_queryset():
    return (Announcement.objects
            .select_related("branch","course")
            .prefetch_related("images","attachments"))

@api_view(["GET"])
@permission_classes([AllowAny])
def announcement_website_list(request):
    """
    Public list:
      ?branch=   ?course=   ?limit=20
      ?active_only=1        ?pinned_first=1
    Sadece PUBLIC & PUBLISHED & aktif yayın penceresi (default).
    """
    qs = announcement_base_queryset().filter(status="PUBLISHED", is_active=True, audience="PUBLIC")

    active_only = request.GET.get("active_only", "1").lower() in {"1","true","yes"}
    if active_only:
        now = timezone.now()
        qs = qs.filter(
            Q(publish_start_at__isnull=True) | Q(publish_start_at__lte=now),
            Q(publish_end_at__isnull=True)   | Q(publish_end_at__gt=now),
        )

    branch = request.GET.get("branch")
    course = request.GET.get("course")
    if branch: qs = qs.filter(branch_id=branch)
    if course: qs = qs.filter(course_id=course)

    pinned_first = request.GET.get("pinned_first","1").lower() in {"1","true","yes"}
    qs = qs.order_by("-pinned","-publish_start_at","-created_at") if pinned_first else qs.order_by("-publish_start_at","-created_at")

    try:
        limit = int(request.GET.get("limit", 20))
    except ValueError:
        limit = 20
    qs = qs[:min(max(limit,1), 100)]

    ser = AnnouncementOut(qs, many=True, context={"request": request})
    return Response({"results": ser.data})

@api_view(["GET"])
@permission_classes([AllowAny])
def announcement_website_detail(request, pk:int):
    try:
        obj = announcement_base_queryset().get(pk=pk, status="PUBLISHED", is_active=True, audience="PUBLIC")
    except Announcement.DoesNotExist:
        return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)

    if not obj.is_published_now:
        return Response({"detail":"Not available."}, status=status.HTTP_404_NOT_FOUND)

    Announcement.objects.filter(pk=obj.pk).update(view_count=obj.view_count + 1)

    ser = AnnouncementOut(obj, context={"request": request})
    return Response(ser.data)




# events/api.py

def event_base_qs():
    return Event.objects.select_related("branch","course").prefetch_related("images","attachments")

@api_view(["GET"])
@permission_classes([AllowAny])
def event_website_list(request):
    """
    Public list:
      ?branch=  ?course=  ?limit=20
      ?upcoming=1         (start_at >= now)
      ?active_only=1      (PUBLISHED + publish window içinde)
      ?pinned_first=1
      ?order=asc|desc     (start_at)
      ?from=YYYY-MM-DD    ?to=YYYY-MM-DD
    Sadece PUBLIC & is_active varsayılan filtreler uygulanır.
    """
    now = timezone.now()
    qs = event_base_qs().filter(status="PUBLISHED", is_active=True, audience="PUBLIC")


    # Yayın/publish ve durum
    active_only = (request.GET.get("active_only","1").lower() in {"1","true","yes"})
    if active_only:
        qs = qs.filter(status="PUBLISHED").filter(
            Q(publish_start_at__isnull=True) | Q(publish_start_at__lte=now),
            Q(publish_end_at__isnull=True)   | Q(publish_end_at__gt=now),
        )
    else:
        qs = qs.filter(status__in=["PUBLISHED","SCHEDULED"])

    # # Zaman filtreleri
    # if request.GET.get("upcoming","1").lower() in {"1","true","yes"}:
    #     qs = qs.filter(start_at__gte=now)
    # date_from = request.GET.get("from")
    # date_to   = request.GET.get("to")
    # if date_from:
    #     qs = qs.filter(start_at__date__gte=date_from)
    # if date_to:
    #     qs = qs.filter(start_at__date__lte=date_to)

    # Scope filtreleri
    branch = request.GET.get("branch")
    course = request.GET.get("course")
    if branch: qs = qs.filter(branch_id=branch)
    if course: qs = qs.filter(course_id=course)

    # Sıralama
    order = request.GET.get("order","asc")
    pinned_first = request.GET.get("pinned_first","1").lower() in {"1","true","yes"}
    if pinned_first:
        qs = qs.order_by("-pinned", ("start_at" if order=="asc" else "-start_at"), "-created_at")
    else:
        qs = qs.order_by(("start_at" if order=="asc" else "-start_at"), "-created_at")

    # Limit
    try:
        limit = int(request.GET.get("limit", 20))
    except ValueError:
        limit = 20
    qs = qs[:min(max(limit,1), 100)]

    ser = EventOut(qs, many=True, context={"request": request})
    return Response({"results": ser.data})

@api_view(["GET"])
@permission_classes([AllowAny])
def event_website_detail(request, pk:int):
    try:
        obj = event_base_qs().get(pk=pk, is_active=True, audience="PUBLIC")
    except Event.DoesNotExist:
        return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)

    # aktif yayın penceresi ve durum kontrolü
    if obj.status != "PUBLISHED" or not obj.is_published_now:
        return Response({"detail":"Not available."}, status=status.HTTP_404_NOT_FOUND)

    # basit görüntülenme sayacı
    Event.objects.filter(pk=obj.pk).update(view_count=obj.view_count + 1)

    ser = EventOut(obj, context={"request": request})
    return Response(ser.data)
