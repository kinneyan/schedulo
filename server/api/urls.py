from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import Login, Register, GetUser

urlpatterns = [
    path('login', Login.as_view()),
    path('register', Register.as_view()),
    path('user', GetUser.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
