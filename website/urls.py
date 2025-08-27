from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentLookupByPhone, AssessmentResultViewSet
from courses.views_public import PublicAssessmentViewSet
from .views import *

router = DefaultRouter()
router.register(r"website/teachers", TeacherProfileViewSet, basename="website-teachers")
router.register(r"website/branches", BranchWebViewSet, basename="website-branches")
router.register(r"website/subjects", CourseListViewSet, basename="subject")
router.register(r"website/subject-items", CourseItemViewSet, basename="subject-items")
router.register(r"website/assessment-results", AssessmentResultViewSet, basename="assessment-result")
router.register(r"website/assessments", PublicAssessmentViewSet, basename="public-assessment")


urlpatterns = [
    path("api/", include(router.urls)),
    path("api/website/students/lookup", StudentLookupByPhone.as_view(), name="student-lookup-by-phone"),
    path("api/website/announcements", announcement_website_list, name="website-announcement-list"),
    path("api/website/announcements/<int:pk>", announcement_website_detail, name="website-announcement-detail"),
    path("api/website/events", event_website_list, name="website-event-list"),
    path("api/website/events/<int:pk>", event_website_detail, name="website-event-detail"),
]
