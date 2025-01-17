from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

@api_view(["POST"])
def send_file_to_archivate(request: Request):
    request.FILES
    return Response({"anws" : "answ"})