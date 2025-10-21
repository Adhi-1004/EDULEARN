"""
Assessment Model Rollback Script
Rolls back the unified model migration to the original structure
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class AssessmentRollback:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client
        self.assessments_collection = self.db.assessments
        self.submissions_collection = self.db.submissions
        self.batches_collection = self.db.batches
        
    async def rollback_assessments(self):
        """Rollback assessments to original model structure"""
        print("🔄 Starting assessment rollback...")
        
        # Get all unified assessments
        unified_assessments = await self.assessments_collection.find({}).to_list(length=None)
        
        rolled_back_count = 0
        for assessment in unified_assessments:
            try:
                # Convert back to original format
                original_assessment = await self._convert_to_original_assessment(assessment)
                
                # Update the document
                await self.assessments_collection.update_one(
                    {"_id": assessment["_id"]},
                    {"$set": original_assessment}
                )
                
                rolled_back_count += 1
                print(f"✅ Rolled back assessment: {assessment.get('title', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Failed to rollback assessment {assessment.get('_id')}: {e}")
        
        print(f"🎉 Rollback completed! {rolled_back_count} assessments rolled back.")
    
    async def _convert_to_original_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Convert unified assessment back to original structure"""
        
        # Convert questions back to original format
        original_questions = await self._convert_questions_to_original(assessment.get('questions', []))
        
        # Create original assessment structure
        original_assessment = {
            "title": assessment.get("title", ""),
            "description": assessment.get("description", ""),
            "subject": assessment.get("subject", ""),
            "difficulty": assessment.get("difficulty", "medium"),
            "time_limit": assessment.get("config", {}).get("time_limit", 60),
            "questions": original_questions,
            "created_by": assessment.get("created_by", ""),
            "created_at": assessment.get("created_at", datetime.utcnow()),
            "is_active": assessment.get("is_active", True),
            "total_questions": assessment.get("total_questions", 0),
            "batches": assessment.get("assigned_batches", []),
            "type": assessment.get("type", "mcq"),
            "max_attempts": assessment.get("config", {}).get("max_attempts", 1),
            "tags": assessment.get("tags", []),
            "metadata": assessment.get("metadata", {})
        }
        
        return original_assessment
    
    async def _convert_questions_to_original(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert questions back to original format"""
        original_questions = []
        
        for question in questions:
            if question.get("type") == "coding":
                # Convert coding question back
                original_question = {
                    "title": question.get("title", ""),
                    "description": question.get("description", ""),
                    "difficulty": question.get("difficulty", "medium"),
                    "language": question.get("language", "python"),
                    "starter_code": question.get("starter_code", ""),
                    "test_cases": question.get("test_cases", []),
                    "hints": question.get("hints", []),
                    "points": question.get("points", 1),
                    "time_limit": question.get("time_limit", 300),
                    "memory_limit": question.get("memory_limit", 128),
                    "tags": question.get("tags", []),
                    "metadata": question.get("metadata", {})
                }
            else:
                # Convert MCQ back
                options = []
                correct_answer = 0
                
                for i, option in enumerate(question.get("options", [])):
                    options.append(option.get("text", ""))
                    if option.get("is_correct", False):
                        correct_answer = i
                
                original_question = {
                    "question": question.get("question_text", ""),
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": question.get("explanation", ""),
                    "points": question.get("points", 1),
                    "difficulty": question.get("difficulty", "medium"),
                    "tags": question.get("tags", []),
                    "metadata": question.get("metadata", {})
                }
            
            original_questions.append(original_question)
        
        return original_questions
    
    async def rollback_submissions(self):
        """Rollback submissions to original model structure"""
        print("🔄 Starting submission rollback...")
        
        unified_submissions = await self.submissions_collection.find({}).to_list(length=None)
        
        rolled_back_count = 0
        for submission in unified_submissions:
            try:
                original_submission = await self._convert_to_original_submission(submission)
                
                await self.submissions_collection.update_one(
                    {"_id": submission["_id"]},
                    {"$set": original_submission}
                )
                
                rolled_back_count += 1
                print(f"✅ Rolled back submission: {submission.get('_id')}")
                
            except Exception as e:
                print(f"❌ Failed to rollback submission {submission.get('_id')}: {e}")
        
        print(f"🎉 Submission rollback completed! {rolled_back_count} submissions rolled back.")
    
    async def _convert_to_original_submission(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Convert unified submission back to original structure"""
        
        # Convert answers back to original format
        original_answers = []
        answers = submission.get("answers", [])
        
        for answer in answers:
            original_answer = {
                "question_id": answer.get("question_id", ""),
                "answer": answer.get("answer", ""),
                "is_correct": answer.get("is_correct"),
                "points_earned": answer.get("points_earned", 0),
                "time_spent": answer.get("time_spent", 0)
            }
            original_answers.append(original_answer)
        
        original_submission = {
            "assessment_id": submission.get("assessment_id", ""),
            "student_id": submission.get("student_id", ""),
            "batch_id": submission.get("batch_id"),
            "answers": original_answers,
            "total_score": submission.get("total_score", 0),
            "max_score": submission.get("max_score", 0),
            "percentage": submission.get("percentage", 0.0),
            "started_at": submission.get("started_at", datetime.utcnow()),
            "submitted_at": submission.get("submitted_at"),
            "attempt_number": submission.get("attempt_number", 1),
            "metadata": submission.get("metadata", {})
        }
        
        return original_submission
    
    async def rollback_batches(self):
        """Rollback batches to original model structure"""
        print("🔄 Starting batch rollback...")
        
        unified_batches = await self.batches_collection.find({}).to_list(length=None)
        
        rolled_back_count = 0
        for batch in unified_batches:
            try:
                original_batch = await self._convert_to_original_batch(batch)
                
                await self.batches_collection.update_one(
                    {"_id": batch["_id"]},
                    {"$set": original_batch}
                )
                
                rolled_back_count += 1
                print(f"✅ Rolled back batch: {batch.get('name', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Failed to rollback batch {batch.get('_id')}: {e}")
        
        print(f"🎉 Batch rollback completed! {rolled_back_count} batches rolled back.")
    
    async def _convert_to_original_batch(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Convert unified batch back to original structure"""
        
        original_batch = {
            "batch_name": batch.get("name", ""),
            "description": batch.get("description"),
            "created_by": batch.get("created_by", ""),
            "created_at": batch.get("created_at", datetime.utcnow()),
            "student_ids": batch.get("student_ids", []),
            "total_students": batch.get("total_students", 0),
            "average_performance": batch.get("average_performance", 0.0),
            "completion_rate": batch.get("completion_rate", 0.0),
            "weaknesses": batch.get("common_weaknesses", []),
            "is_active": batch.get("is_active", True),
            "settings": batch.get("settings", {})
        }
        
        return original_batch
    
    async def run_rollback(self):
        """Run the complete rollback process"""
        print("🚀 Starting unified assessment model rollback...")
        
        try:
            await self.rollback_assessments()
            await self.rollback_submissions()
            await self.rollback_batches()
            
            print("✅ Rollback completed successfully!")
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            raise

# Usage example
async def main():
    # Initialize MongoDB client
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.edulearn
    
    # Run rollback
    rollback = AssessmentRollback(db)
    await rollback.run_rollback()
    
    # Close client
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
