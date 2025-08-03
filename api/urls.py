from django.urls import path
from api import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('courses/', views.course_list, name='course-list'),
    path('courses/<int:pk>/', views.course_detail, name='course-detail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), #for login token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), #for refresh token
    path('register/', views.register, name='register'),
    path('protected/', views.protected_view, name='protected-view'),
]