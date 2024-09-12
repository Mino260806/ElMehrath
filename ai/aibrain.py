import google.generativeai as genai

from model.subject import Subject


class AiBrain:
    def __init__(self):
        # Warning put API token
        genai.configure(api_key="")
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def test(self):
        response = self.model.generate_content("SAY testsuccess AND NOTHING ELSE")
        return response.text.strip()

    def get_subject(self, file):
        print(f"Uploading file {file} to gemini servers")
        gemini_file = genai.upload_file(path=file, display_name="Target Document")
        print(f"Querying type for file {file}")
        response = self.model.generate_content(["""
You are a subject identifier and you are asked to determine the subject for the document you get sent. You can ONLY ANSWER WITH THE NAME OF THE DOCUMENT AND NO ADDITIONAL INFO

answers list:
- math
- physics
- chemistry

ONLY SAY ANSWER FROM ANSWER LIST

example answer:
chemistry

Now take this document and tell me its subject
""", gemini_file])
        subject_name = response.text.strip()
        try:
            subject = Subject(subject_name)
            return subject
        except ValueError:
            return Subject.Other
