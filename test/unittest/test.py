import os
import unittest

from ai.aibrain import AiBrain
from file.attachment import AttachmentManager
from model.subject import Subject


class TestAttachmentManager(unittest.TestCase):
    def test_download_attachment(self):
        attachment_manager = AttachmentManager()
        attachment_manager.download("https://picsum.photos/200")
        self.assertEqual(1, len(attachment_manager.list))
        self.assertTrue(os.path.exists(attachment_manager.list[0].path))

        os.remove(attachment_manager.list[0])


class AiBrainTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.aibrain = AiBrain()
        super().__init__(*args, **kwargs)

    def test_message(self):
        answer = self.aibrain.test()
        print(f"Answer is {answer}")
        self.assertEqual("testsuccess", answer)

    def test_attachment_type(self):
        result_type = self.aibrain.get_subject(os.path.abspath("../media/math.pdf"))
        print(f"Result is {result_type}")
        self.assertEqual(Subject.Math, result_type)


if __name__ == '__main__':
    unittest.main()
