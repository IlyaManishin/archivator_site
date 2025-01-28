from archivator import models
from archivator import app_settings

from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist


def get_free_file_id():
    while True:
        check_id = get_random_string(length=15)
        try:
            file = models.UserFiles.objects.get(file_id=check_id)
            continue
        except ObjectDoesNotExist:
            return check_id
    
