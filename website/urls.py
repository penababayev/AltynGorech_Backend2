from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentLookupByPhone
from .views import *

router = DefaultRouter()
router.register(r"website/teachers", TeacherProfileViewSet, basename="website-teachers")
router.register(r"website/branches", BranchWebViewSet, basename="website-branches")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/students/lookup", StudentLookupByPhone.as_view(), name="student-lookup-by-phone"),
]
