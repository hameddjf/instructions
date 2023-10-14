from django.urls import path

from .views import EmailCreateView

urlpatterns = [
    path("writeEmail/", EmailCreateView.as_view(), name="create_email"),
]
