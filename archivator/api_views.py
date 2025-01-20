from pathlib import Path
import os

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.exceptions import bad_request
from django.utils.crypto import get_random_string

from archivator import app_settings
from main.models import UserToken


@api_view(["POST"])
def send_file_to_archivate(request: Request):
    if "file" not in request.FILES: 
        return bad_request(request, "Отсутствует файл")
    uploadedFile = request.FILES["file"]
    
    if uploadedFile.size > app_settings.MAX_FILE_SIZE_BYTES:
        return bad_request(request, "Превышен лимит размера файла")
    
    access_token = request.headers.get("Authorization", "")
    if not access_token or not UserToken.objects.filter(token=access_token).first():
        return Response("Не авторизован", status=401)
    
    file_name = uploadedFile.name
    new_file_name = f"{get_random_string(length=15)}_{file_name}"
    file_dest_path = app_settings.FILES_TO_ARCHIVATE_DIR / new_file_name
    with open(file_dest_path, "wb") as file:
        for chunk in uploadedFile.chunks():
            file.write(chunk)
    
    return Response("Файл загружен")