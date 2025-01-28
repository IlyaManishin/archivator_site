from rest_framework.request import Request
from main.models import UserToken


def get_user_token(request: Request):
    access_token = request.headers.get("Authorization", "")
    if not access_token: return None
    
    user_token = UserToken.objects.filter(token=access_token).first()
    return user_token