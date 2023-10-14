from django.urls import path
from .views import YourCSVUploadView

urlpatterns = [
    # ...
    path("upload-csv/", YourCSVUploadView.as_view(), name="upload_csv"),
    # ...
]
