import subprocess
import os
from pathlib import Path

from archivator import models
from main.models import UserToken
from archivator import app_settings 

from django.utils.crypto import get_random_string

def _archivate(dest_path: str, src_path: str, original_filename: str):
    #create txt with original name
    zip_path = dest_path.replace(app_settings.ARCHIVATOR_EXTENSION, ".zip")
    
    txt_path = f"{dest_path}.txt"
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write(original_filename)
    
    subprocess.call(["zip", "-Dj", zip_path, src_path, txt_path])
    
    if os.path.exists(txt_path): os.remove(txt_path)
    
    subprocess.call(["mv", zip_path, dest_path])
    

def archivate_file(user_token: UserToken, source_path: Path, file_id: str, original_filename: str) -> str:
    archivated_file_path = app_settings.ARCHIVATED_FILES_DIR / f"{file_id}{app_settings.ARCHIVATOR_EXTENSION}"
    _archivate(str(app_settings.ARCHIVATED_FILES_DIR), str(archivated_file_path), str(source_path), original_filename)
    
    archivated_file = models.UserFiles()
    archivated_file.user_token = user_token
    archivated_file.file_type = models.FileTypes.archive
    archivated_file.file_id = file_id
    archivated_file.file_path = archivated_file_path
    archivated_file.file_size = os.path.getsize(archivated_file_path)
    archivated_file.save()
    
def dearchivate_file(*args, **kwargs):
    return
