
from sentence_transformers import SentenceTransformer
import numpy as np
from src.database.models import Match

class CVMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.skill_weights = {
            'required_skills': 0.6,
            'experience': 0.3,
            'education': 0.1
        }

    def calculate_matches(self, jobs, candidates):
        all_matches = []
        for job in jobs:
            for candidate in candidates:
                score, matched_skills = self._calculate_match(job, candidate)
                all_matches.append({
                    'job_id': job.id,
                    'candidate_id': candidate.id,
                    'score': score,
                    'matched_skills': matched_skills
                })
        return sorted(all_matches, key=lambda x: x['score'], reverse=True)

    def _calculate_match(self, job, candidate):
        job_skills = " ".join(job.requirements.get('required_skills', []))
        candidate_skills = " ".join(candidate.skills)
        skill_sim = self._cosine_sim(job_skills, candidate_skills)

        req_exp = job.requirements.get('min_experience', 0)
        candidate_exp = sum([float(exp.get('years', 0)) for exp in candidate.experience])
        exp_score = min(candidate_exp / max(req_exp, 1), 1.0)

        edu_score = 1.0 if any(edu['degree'] in job.requirements.get('preferred_education', []) 
                          for edu in candidate.education) else 0.0

        total_score = (
            self.skill_weights['required_skills'] * skill_sim +
            self.skill_weights['experience'] * exp_score +
            self.skill_weights['education'] * edu_score
        )

        return total_score, list(set(job.requirements['required_skills']) & set(candidate.skills))

    def _cosine_sim(self, text1, text2):
        emb1 = self.model.encode(text1)
        emb2 = self.model.encode(text2)
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))