from pydantic import BaseModel
from typing import Optional

class QuestionPayload(BaseModel):
    question: str
    image: Optional[str] = None  # base64 image string (optional)

class AnswerResponse(BaseModel):
    answer: str
    links: list[str]
