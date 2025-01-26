from pathlib import Path
import os
import time

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import bad_request

from django.utils.crypto import get_random_string
from django.core.files.base import File

from archivator import app_settings
from archivator import models
from archivator import archivation_logic
from main.models import UserToken


@api_view(["POST"])
def send_file_to_archivate(request: Request):
    if "file" not in request.FILES: 
        return bad_request(request, "Отсутствует файл")
    uploaded_file = request.FILES["file"]
    file_size = uploaded_file.size
    if file_size > app_settings.MAX_FILE_SIZE_BYTES:
        return bad_request(request, "Превышен лимит размера файла")
    
    access_token = request.headers.get("Authorization", "")
    user_token = UserToken.objects.filter(token=access_token).first()
    if not access_token or not user_token:
        return Response("Не авторизован", status=401)
    
    file_name = uploaded_file.name
    
    file_id, new_file_name, file_dest_path, check_path = "", "", "", ""
    while not file_id or os.path.exists(check_path):
        file_id = get_random_string(length=10)
        new_file_name = f"{file_id}_{file_name}"
        file_dest_path = app_settings.FILES_TO_ARCHIVATE_DIR / new_file_name
        check_path = app_settings.ARCHIVATED_FILES_DIR / f"{file_id}.rar"
    
    with open(file_dest_path, "wb") as file:
        for chunk in uploaded_file.chunks():
            file.write(chunk)
    archivation_logic.archivate_file(user_token, file_dest_path, file_id)

    if os.path.exists(file_dest_path): os.remove(file_dest_path)
    time.sleep(5)
    return Response("Файл загружен", 200)