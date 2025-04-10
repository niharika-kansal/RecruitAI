
import pandas as pd
from ollama import Client
from sqlalchemy.orm import Session
import json
from src.database.models import Job

class JDProcessor:
    def __init__(self, db_session: Session):
        self.client = Client()
        self.db = db_session

    def process_csv(self, csv_path: str):
        df = pd.read_csv(csv_path, encoding='cp1252')

        for _, row in df.iterrows():
            requirements = self._parse_jd(row['Job Description'])
            job = Job(
                title=row['Job Title'],
                description=row['Job Description'],
                requirements=requirements
            )
            self.db.merge(job)
        self.db.commit()

    def _parse_jd(self, text: str) -> dict:
        prompt = f"""Extract as JSON:
        {{
            "required_skills": ["list"],
            "min_experience": years,
            "preferred_education": ["degrees"]
        }}
        From: {text}"""

        try:
            response = self.client.generate(model='llama3', prompt=prompt)
            return json.loads(response['response'])
        except:
            return {"required_skills": [], "min_experience": 0, "preferred_education": []}