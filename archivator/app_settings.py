import logging
from pathlib import Path
from archivator_site import settings as site_settings


APP_DIR = Path(__file__).resolve().parent
ARCHIVATOR_LOGGER_PATH = APP_DIR / "archivator_logger.log"

MEDIA_DIR = site_settings.MEDIA_ROOT
STORAGE_PATH = MEDIA_DIR / "storage"

TEMP_FILES_DIR = STORAGE_PATH / "temp"
ARCHIVATED_FILES_DIR = STORAGE_PATH / "archivated_files"
DEARCHIVATED_FILES_DIR = STORAGE_PATH / "dearchivated_files"

MAX_FILE_SIZE_BYTES = 1024 * 1024 * 100
ARCHIVATED_FILE_TIME_TO_LIVE_DAYS = 7

# ARCHIVATOR_EXTENSION = ".zip"
ARCHIVATOR_EXTENSION = ".machine"


arch_logger = logging.getLogger("archivator_logger")
formatter = logging.Formatter("%(name)s :: %(levelname)s :: (%(filename)s).%(funcName)s(%(lineno)d) :: %(message)s")
handler = logging.FileHandler(ARCHIVATOR_LOGGER_PATH, encoding="utf-8")
handler.formatter = formatter
arch_logger.addHandler(handler)
arch_logger.setLevel(logging.DEBUG)

TEMP_FILES_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVATED_FILES_DIR.mkdir(parents=True, exist_ok=True)
DEARCHIVATED_FILES_DIR.mkdir(parents=True, exist_ok=True)
#Temporaly
