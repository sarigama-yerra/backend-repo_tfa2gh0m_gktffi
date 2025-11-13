import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Tutorprofile, Teachercandidate

app = FastAPI(title="Atomik API", description="Teen-to-Teen EdTech backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Atomik Backend Running"}

@app.get("/schema")
def get_schema_info():
    # Minimal schema exposure for DB viewer
    return {"schemas": ["tutorprofile", "teachercandidate"]}

# ---------- Tutor Profiles ----------
@app.post("/tutors")
def create_tutor(profile: Tutorprofile):
    try:
        inserted_id = create_document("tutorprofile", profile)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tutors")
def list_tutors(grade: Optional[int] = None, subject: Optional[str] = None, limit: int = 50):
    try:
        filt = {}
        if grade is not None:
            # Match array contains value
            filt["grade_levels"] = grade
        if subject is not None:
            filt["subjects"] = subject
        docs = get_documents("tutorprofile", filt, limit)
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
        return {"tutors": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Teacher Candidates + Aptitude ----------
class AptitudeSubmission(BaseModel):
    name: str
    email: EmailStr
    grade: int
    subjects: List[str]
    motivation: Optional[str] = None
    answers: List[int]

@app.post("/aptitude/submit")
def submit_aptitude(payload: AptitudeSubmission):
    try:
        # Simple scoring with an answer key of 5 questions (options: 1-4)
        answer_key = [2, 1, 3, 2, 4]
        score = 0
        for i, ans in enumerate(payload.answers[:len(answer_key)]):
            if ans == answer_key[i]:
                score += 1
        status = "passed" if score >= 4 else ("needs-review" if score >= 3 else "pending")
        candidate = Teachercandidate(
            name=payload.name,
            email=payload.email,
            grade=payload.grade,
            subjects=payload.subjects,
            motivation=payload.motivation,
            score=score,
            status=status,
        )
        inserted_id = create_document("teachercandidate", candidate)
        return {"id": inserted_id, "score": score, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/aptitude/candidates")
def list_candidates(status: Optional[str] = None, limit: int = 50):
    try:
        filt = {"status": status} if status else {}
        docs = get_documents("teachercandidate", filt, limit)
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
        return {"candidates": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
