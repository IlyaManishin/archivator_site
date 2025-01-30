from django.db import models
import django.utils.timezone
from main.models import UserToken

class FileTypes():
    archive = "archive"
    any_file = "any_file"

class UserFiles(models.Model):
    user_token = models.ForeignKey(UserToken, on_delete=models.CASCADE, max_length=64)
    file_id = models.CharField(max_length=32)
    original_name = models.CharField(max_length=128)
    
    file_path = models.CharField(unique=True, max_length=256)
    file_type = models.CharField(max_length=32)
    file_size = models.IntegerField()
    download_time = models.TimeField(default=django.utils.timezone.now)
    
    #for archive
    file_name_inside = models.CharField(max_length=128)
    
    class Meta:
        db_table = "user_files"
        verbose_name = "user_files"
    
