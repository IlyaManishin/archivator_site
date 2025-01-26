import subprocess
import os

from archivator import models
from archivator import app_settings 

from django.utils.crypto import get_random_string

def _archivate(dest_path, src_path):
    subprocess.call(["zip", str(dest_path), str(src_path)])
    

def archivate_file(user_token: models.ArchivatedFiles, file_path_to_archivate, file_id) -> str:
    file_path = app_settings.ARCHIVATED_FILES_DIR / f"{file_id}.rar"
    _archivate(file_path, file_path_to_archivate)
    
    archivated_file = models.ArchivatedFiles()
    archivated_file.user_token = user_token
    archivated_file.file_id = file_id
    archivated_file.file_path = file_path
    archivated_file.file_size = os.path.getsize(file_path)
    archivated_file.save()
    
