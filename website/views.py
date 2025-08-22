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

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated  # istersen
from django_filters.rest_framework import DjangoFilterBackend

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
    """
    Basit normalize: baştaki '+' hariç tüm boşluk, tire, parantez vb. temizlenir.
    Eğer DB'de + ülke koduyla saklıyorsan, bu fonksiyonu aynı formatı üretecek şekilde ayarla.
    strip() → Baştaki ve sondaki boşlukları siler.
    Örn: " +90 532 123 45 67 " → "+90 532 123 45 67"
    if raw.startswith("+"):
        return "+" + re.sub(r"\D", "", raw[1:])
    raw.startswith("+") → Eğer numara + ile başlıyorsa (ör: +90...).

    raw[1:] → İlk karakteri (+) at, geri kalan kısmı al (örn: "90 532 123 45 67").
    re.sub(r"\D", "", raw[1:]) → Regex ile rakam olmayan her şeyi sil.
    \D = digit olmayan karakter.
    Boşluk, tire, parantez vs. hepsi silinir.
    Sonuç olarak başına tekrar "+" eklenir.
    Örn: "+90 532-123-4567" → "+905321234567"
    return re.sub(r"\D", "", raw)
    Eğer numara + ile başlamıyorsa → doğrudan tüm rakam olmayan karakterleri sil.
    Örn: "0532 123 45 67" → "05321234567"
    Örn: "0 (532) 123-45-67" → "05321234567"
    """
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
