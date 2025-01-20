from django.db import models
from main.models import UserToken

class UserFile(models.Model):
    user_token = models.ForeignKey(UserToken, on_delete=models.CASCADE)
    
    file = models.FileField()
    download_time = models.TimeField(auto_now=True)
    
