# courses/views_public.py
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Assessment, AssessmentResult
from .serializers_public import (
    PublicAssessmentSerializer,
    PublicAssessmentRegisterSerializer,
)

class PublicAssessmentViewSet(mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class   = PublicAssessmentSerializer
    filter_backends    = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filtreler: kursa göre, şubeye göre, şehir vs.
    filterset_fields   = {
        "course": ["exact"],
        "branch": ["exact"],
        "venue_city": ["exact", "icontains"],
        "is_online": ["exact"],
    }
    search_fields      = ["title", "code", "description", "venue_name", "venue_address", "venue_city"]
    ordering_fields    = ["start_at", "end_at", "created_at"]
    ordering           = ["start_at"]

    def get_queryset(self):
        now = timezone.now()
        # Yalnızca yayımlanan ve (gelecek veya şu an açık) sınavlar
        qs = Assessment.objects.filter(status="PUBLISHED").order_by("start_at")
        # İstersen penceresi geçenleri gizlemek:
        # qs = qs.filter(end_at__gte=now)
        return qs

    @action(detail=False, methods=["post"], permission_classes=[AllowAny], url_path="register")
    def public_register(self, request):
        """
        Body:
        {
          "assessment_id": 123,
          "student_id": 456
        }
        """
        serializer = PublicAssessmentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({"ok": True, "result_id": result.id}, status=status.HTTP_201_CREATED)
