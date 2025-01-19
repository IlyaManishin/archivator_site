from pathlib import Path

APP_DIR = Path(__file__).resolve().parent

FILES_TO_ARCHIVATE_DIR = APP_DIR / "storage" / "files_to_archivate"
ARCHIVATED_FILES_DIR = APP_DIR / "storage" / "archivated_files"

FILES_TO_ARCHIVATE_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVATED_FILES_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_BYTES = 1024 * 1024 * 100

#Temporaly
