# Expose main components
from .agents import JDProcessor, CVProcessor, CVMatcher
from .database.models import Base, Job, Candidate, Match

__version__ = "0.1.0"
__all__ = ['JDProcessor', 'CVProcessor', 'CVMatcher', 'Base', 'Job', 'Candidate', 'Match']