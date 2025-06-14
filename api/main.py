from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.utils import answer_question

app = FastAPI()

# Enable CORS for frontend use (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class QuestionRequest(BaseModel):
    question: str
    image: str = None  # Optional, for image questions

# Response endpoint
@app.post("/api/")
async def respond_to_question(payload: QuestionRequest):
    try:
        answer, links = answer_question(payload.question, payload.image)
        return {"answer": answer, "sources": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
