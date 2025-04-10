import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.agents import JDProcessor, CVProcessor, CVMatcher
from src.database.models import Job, Candidate, Match, Base
import os
import time

# 🔧 Disable Streamlit file watcher to prevent torch errors
os.environ["STREAMLIT_WATCH"] = "false"

# Database setup
engine = create_engine("sqlite:///recruitment.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# App UI setup
st.set_page_config(page_title="AI Recruiter", layout="wide")
st.markdown("""
<style>
    .job-card { padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .top-match { color: #2ecc71; font-weight: 700; }
    .skill-chip { background: #f0f2f6; padding: 5px 10px; border-radius: 15px; margin: 3px; display: inline-block; }
    .stProgress > div > div > div { background-color: #3498db !important; }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🤖 AI Recruitment Dashboard")

    with st.sidebar:
        st.header("📁 Data Upload")
        jd_file = st.file_uploader("Upload Job Descriptions (CSV)", type=["csv"])
        cv_files = st.file_uploader("Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)

        if st.button("🚀 Process Files", type="primary"):
            with st.spinner("Analyzing files..."):
                start_time = time.time()
                with Session() as session:
                    # Process job descriptions
                    if jd_file:
                        st.info("Processing uploaded job description CSV...")
                        JDProcessor(session).process_csv(jd_file)
                    else:
                        # fallback to default job_description.csv
                        st.warning("No job description file uploaded. Using default `data/job_description.csv`.")
                        JDProcessor(session).process_csv("data/job_description.csv")

                    # Process resumes
                    if cv_files:
                        st.info(f"Processing {len(cv_files)} resumes...")
                        CVProcessor(session).process_pdfs(cv_files)
                    else:
                        st.warning("No resumes uploaded!")

                    # Match candidates to jobs
                    st.info("Calculating matches...")
                    jobs = session.query(Job).all()
                    candidates = session.query(Candidate).all()

                    matches = CVMatcher().calculate_matches(jobs, candidates)

                    session.query(Match).delete()
                    for idx, match in enumerate(matches):
                        session.add(Match(**match))
                        if idx % 5 == 0:
                            st.write(f"✅ {idx}/{len(matches)} matches processed...")

                    session.commit()
                    st.success(f"✅ All processing done in {time.time() - start_time:.2f} seconds!")

    # Display results
    with Session() as session:
        st.header("🏆 Best Matches Per Job")
        # jobs = session.query(Job).all()

        for job in jobs:
            with st.container():
                st.markdown(f"""
                <div class='job-card'>
                    <h3>{job.title}</h3>
                    <p>{job.description[:200]}...</p>
                </div>
                """, unsafe_allow_html=True)

                matches = (session.query(Match, Candidate)
                           .join(Candidate)
                           .filter(Match.job_id == job.id)
                           .order_by(Match.score.desc())
                           .limit(3)
                           .all())

                cols = st.columns(3)
                for idx, (match, candidate) in enumerate(matches):
                    with cols[idx]:
                        st.subheader(f"🥇 Top {idx+1}")
                        st.markdown(f"""
                            **Candidate:** {candidate.name}  
                            **Score:** <span class='top-match'>{match.score*100:.1f}%</span>
                        """, unsafe_allow_html=True)

                        st.write("**Key Matching Skills:**")
                        for skill in match.matched_skills[:5]:
                            st.markdown(f"<div class='skill-chip'>{skill}</div>", unsafe_allow_html=True)

                        with st.expander("📄 Resume Details"):
                            st.write("**Experience:**")
                            for exp in candidate.experience:
                                st.write(f"- {exp.get('title', '')} ({exp.get('years', '')} yrs)")

                            st.write("**Education:**")
                            for edu in candidate.education:
                                st.write(f"- {edu.get('degree', '')}")

if __name__ == "__main__":
    main()
