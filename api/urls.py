from django.urls import path
from api import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('planned-courses/', views.planned_course_list, name='planned-course-list'),
    path('planned-courses/<int:pk>/', views.planned_course_detail, name='planned-course-detail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), #for login token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), #for refresh token
    path('register/', views.register, name='register'),
    path('protected/', views.protected_view, name='protected-view'),
]