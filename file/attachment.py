import mimetypes
import os
import tempfile

import requests


class AttachmentManager:
    def __init__(self):
        self.list = []

    def download(self, url=None, sent_date=None, filename=None, description=None, user=None, lesson=None, message_id=None):
        print(f"Downloading attachment {url}")
        response = requests.get(url)

        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type)

        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            temp_file.write(response.content)
            self.list.append(Attachment(url, temp_file.name, sent_date, filename, description, user, lesson, message_id))

    def clear(self):
        for attachment in self.list:
            os.remove(attachment.path)
        self.list.clear()


class Attachment:
    def __init__(self, url, path, sent_date=None, filename=None, description=None, user=None,
                 subject=None, lesson=None, message_id=None):
        self.url = url
        self.path = path

        self.sent_date = sent_date
        self.filename = filename
        self.description = description
        self.user = user
        self.subject = subject
        self.lesson = lesson
        self.message_id = None
