import subprocess
import os
from pathlib import Path

from archivator import models
from archivator.app_settings import arch_logger
from main.models import UserToken
from archivator import app_settings 

from django.utils.crypto import get_random_string


class ArchivatorException(Exception):
    def __init__(self, msg=""):
        self.msg = msg
    def __repr__(self):
        return self.msg
     
class SavingFileModelException(ArchivatorException):
    pass

class CreateArchiveException(ArchivatorException):
    pass
    
    
def _archivate(dest_path: str, src_path: str, original_filename: str):
    parts = dest_path.split(".")
    parts[-1] = "zip"
    zip_path = ".".join(parts)
        
    txt_path = f"{src_path}.txt"
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write(original_filename)

    try:
        subprocess.call(["zip", "-Djq", zip_path, src_path, txt_path])
    except Exception as err:
        arch_logger.exception(err)
        arch_logger.error(err)
        
        if os.path.exists(zip_path):
            os.remove(zip_path)

        raise CreateArchiveException()
    finally:
        if os.path.exists(txt_path): 
            os.remove(txt_path)
        
    subprocess.call(["mv", zip_path, dest_path])
    

def archivate_file(user_token: UserToken, source_path: Path, file_id: str, original_filename: str) -> str:
    archivated_file_path = app_settings.ARCHIVATED_FILES_DIR / f"{file_id}{app_settings.ARCHIVATOR_EXTENSION}"
    _archivate(str(archivated_file_path), str(source_path), original_filename)
    
    archivated_file = models.UserFiles()
    archivated_file.user_token = user_token
    archivated_file.file_type = models.FileTypes.archive
    archivated_file.file_id = file_id
    archivated_file.file_path = archivated_file_path
    archivated_file.file_size = os.path.getsize(archivated_file_path)
    
    try:
        archivated_file.save()
        arch_logger.warning(f"new_archive, file_id={file_id}")
    except Exception as err:
        arch_logger.exception(err)
        arch_logger.error(err)
        
        if (os.path.exists(archivated_file_path)): 
            os.remove(archivated_file_path)
        raise SavingFileModelException()
    
def dearchivate_file(*args, **kwargs):
    return
