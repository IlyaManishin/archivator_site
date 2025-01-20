from django.urls import path
from main import api_views, views


urlpatterns = [
    path("authenticate/", api_views.get_authenticate_token),
]
