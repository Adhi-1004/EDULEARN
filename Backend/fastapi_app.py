from typing import List, Optional, Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from Backend.llm_api import (
    generate_personalized_coding_problems,
    evaluate_code_with_ai,
)


class GenerateCodingRequest(BaseModel):
    user_id: str = Field(..., description="Unique ID to ensure per-user uniqueness")
    topic: str
    difficulty: str = Field(..., pattern=r"^(easy|medium|hard)$")
    count: int = Field(..., ge=1, le=10)
    preferred_languages: Optional[List[str]] = []


class EvaluateCodeRequest(BaseModel):
    language: str
    code: str
    problem: Dict[str, Any]
    test_cases: List[Dict[str, str]]


app = FastAPI(title="EduLearn AI - Coding Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/coding/generate")
def generate_coding(req: GenerateCodingRequest) -> Dict[str, Any]:
    try:
        payload = req.model_dump()
        result = generate_personalized_coding_problems(payload)
        return result
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")


@app.post("/coding/evaluate")
def evaluate_code(req: EvaluateCodeRequest) -> Dict[str, Any]:
    try:
        payload = req.model_dump()
        result = evaluate_code_with_ai(payload)
        return result
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


