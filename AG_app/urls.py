from django.urls import path, include
from .views_rest import teacher_list, teacher_detail, news_list, activity_list, video_list, adress_list, course_list


urlpatterns = [
    path('teachers/list/', teacher_list),
    path('teachers/detail/<int:pk>', teacher_detail),
    path('news/', news_list),
    path('activity/', activity_list),
    path('video/', video_list),
    path('adress/', adress_list),
    path('courses/list/<int:pk>', course_list)

]
