import pandas as pd
from ollama import Client
 
from src.database.models import Job
from sqlalchemy.orm import Session
import json

class JDProcessor:
    def __init__(self, db_session: Session):
        self.llm = Client()
        self.db = db_session
        self._verify_model()
        
    def _verify_model(self):
        try:
            # Check if model exists
            self.llm.show('llama3')
        except Exception:
            raise RuntimeError(
                "Model 'llama3' not found. Run 'ollama pull llama3' first!"
            )

    def process_csv(self, csv_path: str):
        try:
            try:
                df = pd.read_csv(csv_path)
            except UnicodeDecodeError:
                df = pd.read_csv(csv_path, encoding='latin-1')
                
            for _, row in df.iterrows():
                parsed_data = self._parse_jd(row["Job Description"])
                job = Job(
                    title=row["Job Title"],
                    description=row["Job Description"],
                    parsed_data=parsed_data
                )
                self.db.add(job)
            self.db.commit()
        except Exception as e:
            print(f"Error processing CSV: {e}")
            raise

    def _parse_jd(self, description: str) -> dict:
        prompt = f"""Extract as JSON:
        {{
            "skills": ["list of technical skills"],
            "min_experience": "years",
            "qualifications": ["degree requirements"]
        }}
        From Job Description: {description}"""
        
        response = self.llm.generate(model="llama3", prompt=prompt)
        return self._clean_response(response["response"])

    def _clean_response(self, text: str) -> dict:
        try:
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"skills": [], "min_experience": 0, "qualifications": []}