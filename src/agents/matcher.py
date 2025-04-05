from sentence_transformers import SentenceTransformer
import numpy as np
from src.database.models import MatchScore

class CVMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def calculate_score(self, job, candidate):
        # Skill Matching
        job_skills = " ".join(job.parsed_data["skills"])
        candidate_skills = " ".join(candidate.skills)
        skill_sim = self._cosine_sim(job_skills, candidate_skills)
        
        # Experience Scoring
        exp_score = min(int(candidate.experience[0]["duration"].split()[0])/int(job.parsed_data["min_experience"]), 1)
        
        # Qualification Bonus
        qual_bonus = 0.2 if any(q in candidate.education[0]["degree"] for q in job.parsed_data["qualifications"]) else 0
        
        total = (skill_sim * 0.6) + (exp_score * 0.3) + qual_bonus
        return min(total, 1.0)
    
    def _cosine_sim(self, text1: str, text2: str) -> float:
        emb1 = self.model.encode(text1)
        emb2 = self.model.encode(text2)
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))