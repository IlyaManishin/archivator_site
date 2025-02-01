import subprocess
import os
from pathlib import Path

from archivator import models
from archivator.app_settings import arch_logger
from main.models import UserToken
from archivator import app_settings 

from django.utils.crypto import get_random_string

     
class SavingFileModelException(Exception):
    pass

class CreateArchiveException(Exception):
    pass

class DearchivatingException(Exception):
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
    archivated_file_name =f"{file_id}{app_settings.ARCHIVATOR_EXTENSION}"
    archivated_file_path = app_settings.ARCHIVATED_FILES_DIR / archivated_file_name
    _archivate(str(archivated_file_path), str(source_path), original_filename)
    
    archivated_file = models.UserFiles()
    archivated_file.user_token = user_token
    archivated_file.file_type = models.FileTypes.archive
    archivated_file.file_id = file_id
    archivated_file.file_path = archivated_file_path
    archivated_file.file_size = os.path.getsize(archivated_file_path)
    archivated_file.original_name = original_filename
    
    
    try:
        archivated_file.save()
        arch_logger.warning(f"new_archive, file_id={file_id}")
    except Exception as err:
        arch_logger.exception(err)
        arch_logger.error(err)
        
        if (os.path.exists(archivated_file_path)): 
            os.remove(archivated_file_path)
        raise SavingFileModelException()

def _clear_dir_if_exists(dir: Path | str):
    if not os.path.exists(dir): return
    
    str_dir = str(dir)
    file_names = os.listdir(str_dir)
    for name in file_names:
        path = os.path.join(str_dir, name)
        if os.path.exists(path): os.remove(path)
    os.rmdir(str_dir)

def _dearchivate(source_path: Path, dest_dir: Path, dest_path: str, file_id: str) -> str:
    parts = str(source_path).split(".")
    parts[-1] = "zip"
    zip_path = ".".join(parts)
    
    subprocess.call(["mv", source_path, zip_path])
    temp_dir = dest_dir / f"{file_id}_temp"
    temp_dir.mkdir()
    
    try:
        subprocess.call(["unzip", zip_path, "-d", temp_dir])
        
        paths = os.listdir(str(temp_dir))
        file_path = temp_dir / [i for i in paths if not i.endswith(".txt")][0] 
        txt_path = temp_dir / [i for i in paths if i.endswith(".txt")][0]
        
        file_name_inside = ""
        with open(txt_path, "r") as file:
            file_name_inside = file.read()

        subprocess.call(["mv", file_path, dest_path])
    except Exception as err:
        arch_logger.exception(err)
        arch_logger.error(err)
        
        if os.path.exists(dest_path): os.remove(dest_path)
        raise DearchivatingException()
    finally:
        _clear_dir_if_exists(temp_dir)
        if os.path.exists(zip_path): os.remove(zip_path)

    return file_name_inside
    
    
def dearchivate_file(user_token: UserToken, source_path: Path, file_id: str, original_filename: str):
    
    dest_path = app_settings.DEARCHIVATED_FILES_DIR / file_id

    file_name_inside = _dearchivate(source_path, app_settings.DEARCHIVATED_FILES_DIR, dest_path, file_id)

    archivated_file = models.UserFiles()
    archivated_file.user_token = user_token
    archivated_file.file_type = models.FileTypes.any_file
    archivated_file.file_id = file_id
    archivated_file.file_path = dest_path
    archivated_file.file_size = os.path.getsize(dest_path)
    archivated_file.original_name = original_filename
    archivated_file.result_file_name = file_id
    
    archivated_file.file_name_inside = file_name_inside
    archivated_file.save()
    
    
    
