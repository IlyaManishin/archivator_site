from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from django.utils.crypto import get_random_string

from main import models


@api_view(["GET"])
def get_authenticate_token(request: Request):
    if request.headers.get("HTTP_X_FORWARDED_FOR", ""):
        ip_from = request.headers["HTTP_X_FORWARDED_FOR"]
        user_token = models.UserToken.objects.filter(user_ip_address=ip_from).first()
        token = user_token.token
        resp_data = {
            "token" : token
        }
        return Response(data=resp_data, status=200)
        
    if "Authorization" in request.headers and request.headers["Authorization"]:
        resp_data =  {
            "token" : request.headers["Authorization"]
        }
        return Response(data=resp_data, status=200)

    new_user_token = "Bearer " + get_random_string(length=40) #maybe check on exist
    user_token = models.UserToken()
    user_token.token = new_user_token
    user_token.save()
    resp_data =  {
        "token" : new_user_token
    }
    return Response(data=resp_data, status=201)
    