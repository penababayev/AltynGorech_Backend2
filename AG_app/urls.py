from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_rest import TeacherViewSet

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('api/', include(router.urls))
]
