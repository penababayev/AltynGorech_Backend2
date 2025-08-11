from django.urls import path, include
from .views_rest import teacher_list, teacher_detail, news_list


urlpatterns = [
    path('teachers/list/', teacher_list),
    path('teachers/detail/<int:pk>', teacher_detail),
    path('news/', news_list)
]
