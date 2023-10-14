from django.urls import path

from django.contrib.auth.views import LogoutView, LoginView
from .views import HomeView


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
