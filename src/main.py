from src.agents import JDProcessor, CVProcessor, CVMatcher  # Updated import path
from src.database.models import engine
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
import os
from pathlib import Path

current_dir = Path(__file__).parent
csv_path = os.path.join(current_dir, '..', 'data', 'job_description.csv')

pdf_path = os.path.join(current_dir, '..', 'data', 'C2808.pdf')


def match_all():
    with Session() as session:
        # Process Jobs
        jd_processor = JDProcessor(session)
        jd_processor.process_csv(csv_path)  # Path to your CSV
        
        # Process CVs
        cv_processor = CVProcessor(session)
        cv_processor.process_pdf(pdf_path)  # Your PDF path
        
        # Calculate Matches
        matcher = CVMatcher()
        jobs = session.query(Job).all()
        candidates = session.query(Candidate).all()
        
        for job in jobs:
            for candidate in candidates:
                score = matcher.calculate_score(job, candidate)
                match = MatchScore(
                    job_id=job.id,
                    candidate_id=candidate.id,
                    score=score
                )
                session.add(match)
        session.commit()

if __name__ == "__main__":
    match_all()