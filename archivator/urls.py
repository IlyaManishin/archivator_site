from django.urls import path
from archivator import views, api_views


urlpatterns = [
    path("archivate/", api_views.send_file_to_archivator),
    path("history-item/", api_views.get_history_item),
    
    path("files-list/", api_views.get_all_user_files),
    path("file-delete/", api_views.delete_user_file),
    path("file-download/", api_views.download_file),
]
