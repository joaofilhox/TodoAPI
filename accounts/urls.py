from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("accounts/", views.AccountView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("login/refresh/", TokenRefreshView.as_view()),

]
