from rest_framework import viewsets, filters
from .models import Teachers
from .serializers import TeacherSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teachers.objects.all().order_by('first_name')
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'first_name', 'last_name']
    ordering_fields = ['experience_years', 'first_name']