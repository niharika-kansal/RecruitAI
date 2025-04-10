import os
from PyPDF2 import PdfReader
import json
from src.database.models import Candidate
from ollama import Client

class CVProcessor:
    def __init__(self, db_session, upload_folder="data/resumes"):
        self.client = Client()
        self.db = db_session
        self.upload_folder = upload_folder

    def process_pdfs(self, pdf_files):
        with self.db.no_autoflush:
            for idx, pdf_file in enumerate(pdf_files, start=1):
                file_path = self._save_pdf(pdf_file)
                text = self._extract_text(file_path)
                candidate_data = self._parse_cv(text)
                candidate = Candidate(
                    name=candidate_data.get('name', 'Unknown'),
                    skills=candidate_data.get('skills', []),
                    experience=candidate_data.get('experience', []),
                    education=candidate_data.get('education', []),
                    resume_path=file_path
                )
                self.db.merge(candidate)
                if idx % 5 == 0:
                    self.db.commit()
                    print(f"Processed {idx} resumes...")
        self.db.commit()

    def _parse_cv(self, text: str) -> dict:
        prompt = f"""Extract JSON:
{{
    "name": "full name",
    "skills": ["list"],
    "experience": [{{"title": "", "years": ""}}],
    "education": [{{"degree": "", "university": ""}}]
}}
From: {text}"""
        try:
            response = self.client.generate(model='llama3', prompt=prompt)
            return json.loads(response['response'])
        except Exception as e:
            print("CV parsing error:", e)
            return {}

    def _save_pdf(self, uploaded_file):
        os.makedirs(self.upload_folder, exist_ok=True)
        file_path = os.path.join(self.upload_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path

    def _extract_text(self, path: str):
        with open(path, "rb") as f:
            return "\n".join([page.extract_text() for page in PdfReader(f).pages])
