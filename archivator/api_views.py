import os
import time

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import bad_request

from django.utils.crypto import get_random_string

from archivator import app_settings
from archivator import models
from archivator import serializators
from archivator import archivation_logic
from archivator.archivation_logic import (
    SavingFileModelException,
    CreateArchiveException,
)
from archivator import utils
from archivator.app_settings import arch_logger
from main.utils import get_user_token


@api_view(["POST"])
def send_file_to_archivator(request: Request):
    if "file" not in request.FILES: 
        return bad_request(request, "file not found")

    uploaded_file = request.FILES["file"]
    file_size = uploaded_file.size
    if file_size > app_settings.MAX_FILE_SIZE_BYTES:
        return bad_request(request, "file size limit exceded")
    
    user_token = get_user_token(request)
    if not user_token:
        return Response("not authorized", status=401)
    
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
        except SavingFileModelException():
            return Response("invalid file", 500)
        except CreateArchiveException():
            return Response("archivation error", 500)
        except Exception as err:
            arch_logger.exception(err)
            arch_logger.error(err)
            
            return Response("smth wrong", 500)
    else:
        pass
    if os.path.exists(file_dest_path):
        os.remove(file_dest_path)

    time.sleep(2)
    return Response("File uploaded", 200)

@api_view(["GET"])
def get_all_user_files(request: Request):
    user_token = get_user_token(request)
    if not user_token:
        return Response("not authorized", status=401)

    user_files = models.UserFiles.objects.filter(user_token=user_token).order_by("-download_time")
    serializer = serializators.UserFilesSerializer(user_files, many=True)
    return Response(serializer.data, 200)

@api_view(["GET"])
@renderer_classes([TemplateHTMLRenderer])
def get_history_item(request: Request):
    return Response(data={}, status=200, template_name="archivator/history_item.html")
    