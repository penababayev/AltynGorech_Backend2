from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from .views_rest import teacher_list, teacher_detail

# router = DefaultRouter()
# router.register(r'teachers', teacher_list, basename='teacher')
# router.register(r'exams', ExamEventViewSet, basename='exam')


urlpatterns = [
    path('teachers/', teacher_list),
    path('detail/<int:pk>', teacher_detail)
]
