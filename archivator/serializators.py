from rest_framework.serializers import Serializer, ModelSerializer
from archivator import models


class UserFilesSerializer(ModelSerializer):
    class Meta:
        model = models.UserFiles
        fields = ["original_name", "file_id", "file_type", "download_time"]