from pathlib import Path
from archivator_site import settings as site_settings

APP_DIR = Path(__file__).resolve().parent
MEDIA_DIR = site_settings.MEDIA_ROOT

FILES_TO_ARCHIVATE_DIR = MEDIA_DIR / "storage" / "files_to_archivate"
ARCHIVATED_FILES_DIR = MEDIA_DIR / "storage" / "archivated_files"

FILES_TO_ARCHIVATE_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVATED_FILES_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_BYTES = 1024 * 1024 * 100
ARCHIVATED_FILE_TIME_TO_LIVE_DAYS = 7
#Temporaly
