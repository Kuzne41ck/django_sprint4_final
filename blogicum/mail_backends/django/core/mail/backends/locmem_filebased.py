from django.conf import settings
from django.core.mail.backends.filebased import (
    EmailBackend as FilebasedEmailBackend,
)


class EmailBackend(FilebasedEmailBackend):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("file_path", settings.EMAIL_FILE_PATH)
        super().__init__(*args, **kwargs)
