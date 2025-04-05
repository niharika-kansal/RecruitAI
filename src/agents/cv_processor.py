from PyPDF2 import PdfReader
from ollama import Client
from src.database.models import Candidate
import re
import json

class CVProcessor:
    def __init__(self, db_session):
        self.llm = Client()
        self.db = db_session

    def process_pdf(self, file_path: str):
        text = self._extract_text(file_path)
        structured_data = self._structure_data(text)
        
        candidate = Candidate(
            name=structured_data.get("name", ""),
            email=structured_data.get("email", ""),
            education=structured_data.get("education", []),
            experience=structured_data.get("experience", []),
            skills=structured_data.get("skills", []),
            certifications=structured_data.get("certifications", [])
        )
        self.db.add(candidate)
        self.db.commit()
        return candidate

    def _extract_text(self, path: str) -> str:
        with open(path, "rb") as f:
            reader = PdfReader(f)
            return "\n".join([page.extract_text() for page in reader.pages])

    def _structure_data(self, text: str) -> dict:
        prompt = f"""Extract as JSON:
        {{
            "name": "full name",
            "email": "email address",
            "education": [{{"degree": "", "university": "", "years": ""}}],
            "experience": [{{"title": "", "company": "", "duration": ""}}],
            "skills": ["list of technical skills"],
            "certifications": ["list of certifications"]
        }}
        From Resume Text: {text}"""
        
        response = self.llm.generate(model="llama3", prompt=prompt)
        return self._clean_response(response["response"])

    def _clean_response(self, text: str) -> dict:
        try:
            clean = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)  # Remove non-printables
            return json.loads(clean)
        except:
            return {}