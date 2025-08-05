from rest_framework import viewsets, filters
from .models import Teachers, ExamEvents
from .serializers import TeacherSerializer, ExamEventSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teachers.objects.all().order_by('first_name')
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'first_name', 'last_name']
    ordering_fields = ['experience_years', 'first_name']


class ExamEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExamEvents.objects.all().order_by('name')
    serializer_class = ExamEventSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['date']