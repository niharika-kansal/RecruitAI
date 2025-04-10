import os
import time
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from src.agents import JDProcessor, CVProcessor, CVMatcher
from src.database.models import engine, Job, Candidate, Match

Session = sessionmaker(bind=engine)

def match_all(jd_path=None, resumes_dir=None):
    start_time = time.time()
    current_dir = Path(__file__).parent
    default_jd = os.path.join(current_dir, '..', 'data', 'job_description.csv')
    resumes_folder = resumes_dir or os.path.join(current_dir, '..', 'data', 'resumes')

    with Session() as session:
        # Process Job Descriptions
        jd_processor = JDProcessor(session)
        jd_file = jd_path if jd_path else default_jd
        print(f"📄 Processing job description CSV: {jd_file}")
        jd_processor.process_csv(jd_file)
        print("✅ Job descriptions processed.")

        # Process all PDF resumes
        cv_processor = CVProcessor(session)
        pdf_files = []
        if os.path.exists(resumes_folder):
            for f in os.listdir(resumes_folder):
                if f.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(resumes_folder, f))
        print(f"📁 Found {len(pdf_files)} resume(s) to process...")
        # Here we simulate the file objects expected by CVProcessor
        dummy_files = []
        for pdf in pdf_files:
            class DummyUploadedFile:
                def __init__(self, path):
                    self.path = path
                    self.name = os.path.basename(path)
                def getbuffer(self):
                    with open(self.path, "rb") as f:
                        return f.read()
            dummy_files.append(DummyUploadedFile(pdf))
        if dummy_files:
            cv_processor.process_pdfs(dummy_files)
        else:
            print("⚠️ No resumes found.")

        # Match candidates with jobs
        print("⚖️ Matching candidates to jobs...")
        matcher = CVMatcher()
        jobs = session.query(Job).all()
        candidates = session.query(Candidate).all()

        session.query(Match).delete()  # Clear old matches

        total_matches = len(jobs) * len(candidates)
        print(f"📊 Total potential matches to compute: {total_matches}")

        match_count = 0
        for i, job in enumerate(jobs, start=1):
            for j, candidate in enumerate(candidates, start=1):
                # Using the updated matching function from CVMatcher
                # If you updated the matching function signature, ensure to use it here.
                score, matched_skills = matcher._calculate_match(job, candidate)
                match = Match(
                    job_id=job.id,
                    candidate_id=candidate.id,
                    score=score,
                    matched_skills=matched_skills
                )
                session.add(match)
                match_count += 1
                if match_count % 20 == 0:
                    session.commit()
                    print(f"Processed {match_count}/{total_matches} matches...")
        session.commit()

        print(f"✅ All matching complete in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    match_all()
