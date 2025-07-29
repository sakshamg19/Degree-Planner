from django.urls import path
from .views import course_list

urlpatterns = [
    path('courses/', course_list, name='course-list'),
]