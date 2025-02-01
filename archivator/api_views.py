import os
import time

from django.http import FileResponse
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import bad_request

from archivator import app_settings
from archivator import models
from archivator import serializators
from archivator import archivation_logic
from archivator.archivation_logic import (
    SavingFileModelException,
    CreateArchiveException,
    DearchivatingException
)
from archivator import utils
from archivator.app_settings import arch_logger

from main.utils import get_user_token, check_user_token_api_decorator


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
        return Response("Not authenticated", status=401)
    
    original_filename: str = uploaded_file.name
    is_archive = original_filename.endswith(app_settings.ARCHIVATOR_EXTENSION)
    
    file_id = utils.get_free_file_id()
    new_file_name = f"{file_id}_{original_filename}"
    file_dest_path = app_settings.TEMP_FILES_DIR / new_file_name
    
    with open(file_dest_path, "wb") as file:
        for chunk in uploaded_file.chunks():
            file.write(chunk)

    try:
        if not is_archive:
            archivation_logic.archivate_file(user_token, file_dest_path, file_id, original_filename)
        else:
            archivation_logic.dearchivate_file(user_token, file_dest_path, file_id, original_filename)
            
    except SavingFileModelException:
        return Response("invalid file", 500)
    except CreateArchiveException:
        return Response("archivation error", 500)
    except DearchivatingException:
        return Response("dearchivation error", 500)
    except Exception as err:
        arch_logger.exception(err)
        arch_logger.error(err)
        
        return Response("smth wrong", 500)
    finally:
        if os.path.exists(file_dest_path):
            os.remove(file_dest_path)

    time.sleep(2)
    return Response("File uploaded", 200)

@api_view(["GET"])
def get_all_user_files(request: Request):
    user_token = get_user_token(request)
    if not user_token:
        return Response("Not authenticated", status=401)

    user_files = models.UserFiles.objects.filter(user_token=user_token).order_by("-download_time")
    serializer = serializators.UserFilesSerializer(user_files, many=True)
    return Response(serializer.data, 200)

@api_view(["GET"])
@renderer_classes([TemplateHTMLRenderer])
def get_history_item(request: Request):
    return Response(data={}, status=200, template_name="archivator/history_item.html")
    
@api_view(["POST"])
def delete_user_file(request: Request):
    user_token = get_user_token(request)
    if not user_token:
        return Response("Not authenticated", 401)
    
    if "file_id" not in request.data or not request.data["file_id"]:
        return bad_request(request, "not file id")
    file_id = request.data["file_id"]
    
    delete_file = models.UserFiles.objects.filter(user_token=user_token).filter(file_id=file_id).first()
    if not delete_file:
        return Response("Not file to delete", status=204)
    
    path = delete_file.file_path
    if os.path.exists(path): os.remove(path)
    delete_file.delete()
    return Response("Successfully", 200)

@api_view(["POST"])
def download_file(request: Request):
    user_token = get_user_token(request)
    if not user_token:
        return Response("Not authenticated", 401)
    if "file_id" not in request.data or not request.data["file_id"]:
        return bad_request(request, "Has not file id")
    
    file_id = request.data["file_id"]
    user_file = models.UserFiles.objects.filter(user_token=user_token).filter(file_id=file_id).first()
    if not user_file:
        return bad_request(request, "No file to download")
    original_name = user_file.original_name
    file_path = user_file.file_path
    file_type = user_file.file_type
    
    if file_type == models.FileTypes.archive:
        user_file_name = f"{original_name}{app_settings.ARCHIVATOR_EXTENSION}"
    elif file_type == models.FileTypes.any_file:
        user_file_name = user_file.file_name_inside
    else:
        return bad_request(request, "smth wrong")
            
    file = open(file_path, "rb")
    response = FileResponse(file, as_attachment=True, filename=user_file_name)
    response["Content-Disposition"] = f'attachment; filename="{user_file_name.replace('"', "'")}"'
    response["Access-Control-Expose-Headers"] = "Content-Disposition" 

    return response 
    