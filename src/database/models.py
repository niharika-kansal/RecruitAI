from sqlalchemy import create_engine, Column, Integer, String, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    description = Column(Text)
    parsed_data = Column(JSON)  # {skills: [], min_experience: int, qualifications: []}

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    education = Column(JSON)  # {degree: str, university: str, years: str}
    experience = Column(JSON)  # [{title: str, company: str, duration: str}]
    skills = Column(JSON)      # [skill1, skill2,...]
    certifications = Column(JSON)

class MatchScore(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer)
    candidate_id = Column(Integer)
    score = Column(Float)
    skill_match = Column(JSON)

engine = create_engine("sqlite:///recruitment.db")
Base.metadata.create_all(engine)