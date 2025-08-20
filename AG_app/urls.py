from django.urls import path, include
from .views_rest import *

urlpatterns = [
    path('teachers/list/', teacher_list),
    path('teachers/detail/<int:pk>', teacher_detail),
    path('news/', news_list),
    path('activity/', activity_list),
    path('video/', video_list),
    path('adress/', adress_list),
    # path('courses/list/<int:pk>', course_list),
    path("students/lookup", StudentLookupByPhone.as_view(), name="student-lookup-by-phone"),

]
