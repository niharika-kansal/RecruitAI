import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///recruitment.db")
Session = sessionmaker(bind=engine)

# Custom CSS
st.markdown("""
<style>
    .match-header { color: #2ecc71; font-size: 1.8rem !important; }
    .skill-match { padding: 8px; background: #f0f2f6; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🔍 CV-Job Matching Dashboard")
    
    with Session() as session:
        # File Uploaders
        col1, col2 = st.columns(2)
        with col1:
            jd_file = st.file_uploader("Upload Job Descriptions CSV", type=["csv"])
            if jd_file:
                processor = JDProcessor(session)
                processor.process_csv(jd_file)
                
        with col2:
            cv_file = st.file_uploader("Upload Candidate CV (PDF)", type=["pdf"])
            if cv_file:
                processor = CVProcessor(session)
                processor.process_pdf(cv_file.name)
        
        # Display Matches
        st.subheader("📊 Best Matches", divider="green")
        matches = pd.read_sql("""
            SELECT j.title, c.name, m.score 
            FROM matches m
            JOIN jobs j ON m.job_id = j.id
            JOIN candidates c ON m.candidate_id = c.id
            ORDER BY m.score DESC
        """, session.connection())
        
        if not matches.empty:
            st.dataframe(matches.style.background_gradient(cmap="Blues"), use_container_width=True)
            
            best = matches.iloc[0]
            st.markdown(f"""
                ### 🏆 Top Match
                **Job:** {best['title']}  
                **Candidate:** {best['name']}  
                **Score:** <span class='match-header'>{best['score']*100:.1f}%</span>
            """, unsafe_allow_html=True)
            
            # Skill Matching Details
            st.subheader("🔧 Skill Alignment")
            match_data = session.query(MatchScore).first()
            if match_data:
                cols = st.columns(3)
                for i, skill in enumerate(match_data.skill_match[:6]):
                    cols[i%3].markdown(f"""
                        <div class='skill-match'>
                            ✅ {skill}
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No matches found. Upload data first!")

if __name__ == "__main__":
    main()