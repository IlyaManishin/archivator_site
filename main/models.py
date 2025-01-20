from django.db import models

class UserToken(models.Model):
    token = models.CharField(max_length=32, primary_key=True)
    user_ip_address = models.CharField(max_length=64)
    created_token_date = models.TimeField(auto_now=True)