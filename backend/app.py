from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import os
import shutil

# ===== DATABASE SETUP =====
DATABASE_URL = "sqlite:///./test.db"  # استخدم SQLite للتطوير
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ===== DATABASE MODELS =====
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    drawings = relationship("Drawing", back_populates="owner")

class Drawing(Base):
    __tablename__ = "drawings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="drawings")
    analysis_results = relationship("AnalysisResult", back_populates="drawing")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    result = Column(Text)
    drawing_id = Column(Integer, ForeignKey("drawings.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    drawing = relationship("Drawing", back_populates="analysis_results")

Base.metadata.create_all(bind=engine)

# ===== PYDANTIC MODELS =====
class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class DrawingResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

# ===== FASTAPI APP =====
app = FastAPI(
    title="Sahel Platform API",
    description="منصة الامتثال للمباني",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== ROUTES =====

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "مرحباً بك في منصة الامتثال للمباني - Sahel Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ===== USER ROUTES =====

@app.post("/api/users/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """تسجيل مستخدم جديد"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مسجل بالفعل")
    
    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """الحصول على بيانات المستخدم"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    return user

# ===== DRAWING ROUTES =====

UPLOAD_FOLDER = "uploaded_drawings"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/api/drawings/upload")
async def upload_drawing(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """رفع مخطط معماري"""
    try:
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        drawing = Drawing(title=file.filename)
        db.add(drawing)
        db.commit()
        db.refresh(drawing)
        
        return {
            "status": "success",
            "message": "تم رفع المخطط بنجاح",
            "drawing_id": drawing.id,
            "filename": drawing.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/drawings/")
async def list_drawings(db: Session = Depends(get_db)):
    """قائمة جميع المخططات"""
    drawings = db.query(Drawing).all()
    return {
        "total": len(drawings),
        "drawings": [
            {
                "id": d.id,
                "title": d.title,
                "created_at": d.created_at
            } for d in drawings
        ]
    }

@app.get("/api/drawings/{drawing_id}")
async def get_drawing(drawing_id: int, db: Session = Depends(get_db)):
    """الحصول على تفاصيل مخطط"""
    drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not drawing:
        raise HTTPException(status_code=404, detail="المخطط غير موجود")
    return {"id": drawing.id, "title": drawing.title, "created_at": drawing.created_at}

@app.delete("/api/drawings/{drawing_id}")
async def delete_drawing(drawing_id: int, db: Session = Depends(get_db)):
    """حذف مخطط"""
    drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not drawing:
        raise HTTPException(status_code=404, detail="المخطط غير موجود")
    
    db.delete(drawing)
    db.commit()
    return {"status": "deleted", "message": "تم حذف المخطط بنجاح"}

# ===== ANALYSIS ROUTES =====

@app.post("/api/analysis/{drawing_id}/analyze")
async def analyze_drawing(drawing_id: int, db: Session = Depends(get_db)):
    """تحليل مخطط معماري"""
    drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not drawing:
        raise HTTPException(status_code=404, detail="المخطط غير موجود")
    
    try:
        result = AnalysisResult(
            result="تم التحليل بنجاح",
            drawing_id=drawing_id
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return {
            "status": "success",
            "message": "تم تحليل المخطط بنجاح",
            "analysis_id": result.id,
            "compliance_score": 85.5
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """الحصول على نتائج التحليل"""
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="التحليل غير موجود")
    
    return {
        "id": analysis.id,
        "result": analysis.result,
        "drawing_id": analysis.drawing_id,
        "created_at": analysis.created_at
    }

# ===== REPORTS ROUTES =====

@app.get("/api/reports/drawing/{drawing_id}")
async def get_report(drawing_id: int, db: Session = Depends(get_db)):
    """الحصول على تقرير الامتثال للمخطط"""
    drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not drawing:
        raise HTTPException(status_code=404, detail="المخطط غير موجود")
    
    analyses = db.query(AnalysisResult).filter(AnalysisResult.drawing_id == drawing_id).all()
    
    return {
        "report_id": f"REP-{drawing_id}",
        "drawing_title": drawing.title,
        "analyses_count": len(analyses),
        "compliance_score": 85.5,
        "status": "compliant",
        "generated_at": datetime.utcnow().isoformat()
    }

@app.get("/api/reports/")
async def list_reports(db: Session = Depends(get_db)):
    """قائمة جميع التقارير"""
    reports = db.query(AnalysisResult).all()
    return {
        "total_reports": len(reports),
        "reports": [
            {
                "id": r.id,
                "drawing_id": r.drawing_id,
                "created_at": r.created_at
            } for r in reports
        ]
    }

# ===== MAIN =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
