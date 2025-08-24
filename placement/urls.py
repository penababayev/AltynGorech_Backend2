# placement/urls.py
from django.urls import path
from . import api

urlpatterns = [
    path("api/website/placement/questions/", api.get_questions, name="placement-questions"),
    path("api/website/submit/",    api.submit,        name="placement-submit"),
]
