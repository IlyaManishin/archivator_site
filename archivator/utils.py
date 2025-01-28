from archivator import models
from archivator import app_settings
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist

import logging

arch_logger = logging.getLogger("archivator_logger")
handler = logging.FileHandler(app_settings.ARCHIVATOR_LOGGER_PATH, encoding="utf-8")
arch_logger.addHandler(handler)
arch_logger.setLevel(logging.WARNING)

def get_free_file_id():
    while True:
        check_id = get_random_string(length=15)
        try:
            file = models.UserFiles.objects.get(file_id=check_id)
            continue
        except ObjectDoesNotExist:
            return check_id
        