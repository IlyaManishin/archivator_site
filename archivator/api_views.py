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
from archivator import utils
from archivator.utils import arch_logger
from main.models import UserToken


@api_view(["POST"])
def get_file_from_web_archivator(request: Request):
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
    
    original_filename: str = uploaded_file.name
    is_archive = original_filename.endswith(app_settings.ARCHIVATOR_EXTENSION)
    
    file_id = utils.get_free_file_id()
    new_file_name = f"{file_id}_{original_filename}"
    file_dest_path = app_settings.TEMP_FILES_DIR / new_file_name
    
    with open(file_dest_path, "wb") as file:
        for chunk in uploaded_file.chunks():
            file.write(chunk)

    if not is_archive:
        try:
            archivation_logic.archivate_file(user_token, file_dest_path, file_id, original_filename)
        except Exception as err:
            arch_logger.exception(err)
    else:
        pass
    if os.path.exists(file_dest_path): os.remove(file_dest_path)
    time.sleep(2)
    return Response("Файл загружен", 200)