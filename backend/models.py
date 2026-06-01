import os
from sqlalchemy import create_engine, Column, String, Text, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scorpio_dna.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ReferenceSNP(Base):
    __tablename__ = "reference_snps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rsid = Column(String(50), index=True, nullable=False)
    category = Column(String(50), nullable=False)
    trait = Column(String(200), nullable=False)
    description = Column(Text, default="")
    risk_allele = Column(String(10), nullable=False)
    risk_genotype = Column(String(10), nullable=False)  # e.g. AA, AG, GG — the risk genotype
    risk_level = Column(String(20), default="elevated")  # typical, elevated, high, carrier
    population_freq = Column(Float, default=0.0)  # how common the risk allele is
    study_url = Column(Text, default="")
    note = Column(Text, default="")

class UploadSession(Base):
    __tablename__ = "upload_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    filename = Column(String(200))
    total_snps = Column(Integer, default=0)
    matched_snps = Column(Integer, default=0)
    created_at = Column(String(30))

def init_db():
    Base.metadata.create_all(bind=engine)
