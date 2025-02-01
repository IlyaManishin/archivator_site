from rest_framework.request import Request
from rest_framework.response import Response

from main.models import UserToken


def get_user_token(request: Request):
    access_token = request.headers.get("Authorization", "")
    if not access_token: return None
    
    user_token = UserToken.objects.filter(token=access_token).first()
    return user_token

def check_user_token_api_decorator(view_func):
    def wrapper(request: Request):
        user_token = get_user_token(request)
        if not user_token:
            return Response("Not authenticated", 401)
        view_func(request, user_token)
        
    return wrapper
    