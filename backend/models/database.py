from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    drawings = relationship('Drawing', back_populates='author')
    comments = relationship('Comment', back_populates='user')

class Drawing(Base):
    __tablename__ = 'drawings'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_results = relationship('AnalysisResult', back_populates='drawing', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='drawing', cascade='all, delete-orphan')
    author = relationship('User', back_populates='drawings')

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    id = Column(Integer, primary_key=True)
    result = Column(Text, nullable=False)
    drawing_id = Column(Integer, ForeignKey('drawings.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    drawing = relationship('Drawing', back_populates='analysis_results')

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    drawing_id = Column(Integer, ForeignKey('drawings.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='comments')
    drawing = relationship('Drawing', back_populates='comments')

class ComplianceRule(Base):
    __tablename__ = 'compliance_rules'
    id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

DATABASE_URL = 'postgresql://user:password@localhost/sahel_platform'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
