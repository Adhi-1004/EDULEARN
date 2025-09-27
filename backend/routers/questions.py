from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import os
import json
from dotenv import load_dotenv

# Optional Google AI import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from database import get_db
from models.schemas import QuestionCreate, QuestionResponse
from models.models import QuestionModel
from routers.auth import get_current_user_id

load_dotenv()

router = APIRouter()

# Configure Google Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    # Set generation config for faster responses
    model.generation_config = {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
else:
    model = None

async def add_questions_to_db(topic: str, difficulty: str, questions: List[dict]):
    """Add generated questions to database"""
    try:
        db = await get_db()
        
        for question_data in questions:
            question_doc = {
                "topic": topic.strip(),
                "difficulty": difficulty.strip(),
                "question": question_data["question"],
                "answer": question_data.get("correctAnswer") or question_data.get("correct_answer") or question_data.get("answer"),
                "options": question_data["options"],
                "explanation": question_data.get("explanation")
            }
            
            # Check if question already exists
            existing = await db.questions.find_one({
                "question": question_data["question"],
                "topic": topic.strip()
            })
            
            if not existing:
                await db.questions.insert_one(question_doc)
        
        return True
    except Exception as e:
        print(f"Error adding questions to database: {e}")
        return False

@router.get("/questions")
async def fetch_questions_from_gemini(
    topic: str = Query(..., description="Topic for questions"),
    difficulty: str = Query(..., description="Difficulty level (easy/medium/hard)"),
    count: int = Query(..., ge=1, le=50, description="Number of questions to generate"),
    user_id: str = Depends(get_current_user_id)
):
    """Generate questions using Google Gemini AI"""
    print(f"🤖 User {user_id} requesting {count} {difficulty} questions for topic: {topic}")
    
    try:
        if not model:
            print("❌ Gemini API key not configured")
            raise HTTPException(
                status_code=500, 
                detail="Gemini API key is not configured properly"
            )
        
        print(f"🤖 Generating questions via Gemini AI for user {user_id}")
        
        # Create prompt for Gemini
        prompt = f"""
Generate {count} multiple-choice questions for the topic '{topic}' with a difficulty of '{difficulty}'.
Return the output as a valid JSON object. The root of the object should be a key named "questions" which is an array.
Each object in the "questions" array must have the following exact keys: "question", "options", "correct_answer", and "explanation".
The "options" key must be an array of 4 strings.
The "explanation" key must contain a clear and concise explanation for why the correct_answer is right.

DO NOT include any other text or formatting outside of the main JSON object.
"""
        
        # Generate questions using Gemini
        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            # Clean the response text
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            payload = json.loads(response_text)
            
            questions = payload.get("questions") if isinstance(payload, dict) else None
            if questions is None:
                # Fallback: accept top-level list
                parsed_alt = payload
                if isinstance(parsed_alt, list):
                    questions = parsed_alt
                else:
                    raise ValueError("Response does not contain 'questions' array")
            
            print(f"🤖 Generated {len(questions)} questions from Gemini AI")
            
            # Store questions in database
            await add_questions_to_db(topic, difficulty, questions)
            
            # Format questions for frontend
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    "question": q["question"],
                    "options": q["options"],
                    "answer": q.get("correct_answer") or q.get("correctAnswer") or q.get("answer"),
                    "explanation": q.get("explanation")
                })
            
            print(f"✅ Successfully generated and stored {len(formatted_questions)} questions for user {user_id}")
            return formatted_questions
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse questions from Gemini API"
            )
        except Exception as e:
            print(f"Error processing Gemini response")
            raise HTTPException(
                status_code=500,
                detail="Failed to process questions from Gemini API"
            )
            
    except Exception as e:
        print(f"Error generating questions")
        if "API key" in str(e):
            raise HTTPException(
                status_code=500,
                detail="Gemini API key is not configured properly"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate questions from Gemini API"
            )

@router.post("/questions")
async def add_questions(
    topic: str,
    difficulty: str,
    questions: List[dict],
    user_id: str = Depends(get_current_user_id)
):
    """Add questions to database manually"""
    try:
        success = await add_questions_to_db(topic, difficulty, questions)
        
        if success:
            return {
                "status": 201,
                "message": "Questions added successfully"
            }
        else:
            return {
                "status": 400,
                "error": "Error adding questions"
            }
    except Exception as e:
        return {
            "status": 500,
            "error": f"Error adding questions: {str(e)}"
        }

@router.get("/questions/{topic}")
async def get_questions_by_topic(
    topic: str,
    difficulty: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id)
):
    """Get questions by topic from database"""
    try:
        db = await get_db()
        
        # Build query
        query = {"topic": {"$regex": topic, "$options": "i"}}
        if difficulty:
            query["difficulty"] = difficulty
        
        # Get questions
        questions = await db.questions.find(query).limit(limit).to_list(None)
        
        # Format response
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                "question": q["question"],
                "options": q["options"],
                "answer": q["answer"]
            })
        
        return formatted_questions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions/explanations")
async def deprecated_generate_explanations():
    raise HTTPException(status_code=410, detail="Endpoint removed. Explanations are now included in /db/questions.")