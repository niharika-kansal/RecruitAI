from sqlalchemy import Column, Integer, String, Text, JSON, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), unique=True)
    description = Column(Text)
    requirements = Column(JSON)
    matches = relationship("Match", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    skills = Column(JSON)
    experience = Column(JSON)
    education = Column(JSON)
    resume_path = Column(String(300))
    # matches = relationship("Match", back_populates="candidate")  # 👈 Add this
class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer)
    candidate_id = Column(Integer)
    score = Column(Float)
    matched_skills = Column(JSON)
    # job = relationship("Job", back_populates="matches")  # 👈 Add this

    # candidate = relationship("Candidate", back_populates="matches")  # 👈 Add this

# ✅ Add these lines to define engine and session
engine = create_engine("sqlite:///recruitment.db")
Session = sessionmaker(bind=engine)
