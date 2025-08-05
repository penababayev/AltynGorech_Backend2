from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_rest import TeacherViewSet, ExamEventViewSet

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'exams', ExamEventViewSet, basename='exam')


urlpatterns = [
    path('api/', include(router.urls))
]
