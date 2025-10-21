"""
Assessment Model Migration Script
Migrates existing assessment data to the unified model structure
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class AssessmentMigration:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client
        self.assessments_collection = self.db.assessments
        self.submissions_collection = self.db.submissions
        self.batches_collection = self.db.batches
        
    async def migrate_assessments(self):
        """Migrate existing assessments to unified model"""
        print("🔄 Starting assessment migration...")
        
        # Get all existing assessments
        existing_assessments = await self.assessments_collection.find({}).to_list(length=None)
        
        migrated_count = 0
        for assessment in existing_assessments:
            try:
                # Convert to unified model
                unified_assessment = await self._convert_to_unified_assessment(assessment)
                
                # Update the document
                await self.assessments_collection.update_one(
                    {"_id": assessment["_id"]},
                    {"$set": unified_assessment}
                )
                
                migrated_count += 1
                print(f"✅ Migrated assessment: {assessment.get('title', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Failed to migrate assessment {assessment.get('_id')}: {e}")
        
        print(f"🎉 Migration completed! {migrated_count} assessments migrated.")
    
    async def _convert_to_unified_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Convert existing assessment to unified model structure"""
        
        # Determine assessment type
        assessment_type = self._determine_assessment_type(assessment)
        
        # Convert questions to unified format
        unified_questions = await self._convert_questions(assessment.get('questions', []), assessment_type)
        
        # Create unified assessment structure
        unified_assessment = {
            # Basic Information
            "title": assessment.get("title", ""),
            "description": assessment.get("description", ""),
            "subject": assessment.get("subject", ""),
            "topic": assessment.get("topic"),
            "difficulty": assessment.get("difficulty", "medium"),
            
            # Assessment Type and Status
            "type": assessment_type,
            "status": "published" if assessment.get("is_active", False) else "draft",
            
            # Questions
            "questions": unified_questions,
            "total_questions": len(unified_questions),
            "total_points": sum(q.get("points", 1) for q in unified_questions),
            
            # Configuration
            "config": {
                "time_limit": assessment.get("time_limit", 60),
                "max_attempts": assessment.get("max_attempts", 1),
                "shuffle_questions": True,
                "shuffle_options": True,
                "show_correct_answers": False,
                "show_explanations": False,
                "allow_review": True,
                "auto_submit": False,
                "proctoring_enabled": False
            },
            
            # Schedule
            "schedule": {
                "start_date": None,
                "end_date": None,
                "duration": assessment.get("time_limit", 60),
                "timezone": "UTC",
                "is_scheduled": False
            },
            
            # Assignment and Access
            "assigned_batches": assessment.get("batches", []),
            "assigned_students": [],
            "access_control": {},
            
            # Metadata
            "created_by": assessment.get("created_by", ""),
            "created_at": assessment.get("created_at", datetime.utcnow()),
            "updated_at": datetime.utcnow(),
            "published_at": assessment.get("created_at") if assessment.get("is_active", False) else None,
            
            # Analytics
            "analytics": {
                "total_attempts": 0,
                "average_score": 0.0,
                "completion_rate": 0.0,
                "average_time": 0.0,
                "difficulty_distribution": {},
                "question_analytics": {},
                "last_updated": datetime.utcnow()
            },
            
            # Additional Fields
            "tags": assessment.get("tags", []),
            "metadata": assessment.get("metadata", {}),
            "is_active": assessment.get("is_active", True)
        }
        
        return unified_assessment
    
    def _determine_assessment_type(self, assessment: Dict[str, Any]) -> str:
        """Determine the assessment type based on existing data"""
        if assessment.get("type") == "ai_generated":
            return "ai_generated"
        elif assessment.get("type") == "coding":
            return "coding"
        elif assessment.get("type") == "challenge":
            return "challenge"
        else:
            return "mcq"
    
    async def _convert_questions(self, questions: List[Dict[str, Any]], assessment_type: str) -> List[Dict[str, Any]]:
        """Convert questions to unified format"""
        unified_questions = []
        
        for i, question in enumerate(questions):
            if assessment_type == "coding":
                # Convert to coding question format
                unified_question = {
                    "id": f"q_{i + 1}",
                    "type": "coding",
                    "title": question.get("title", f"Question {i + 1}"),
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
                # Convert to MCQ format
                options = question.get("options", [])
                unified_options = []
                
                for j, option in enumerate(options):
                    unified_options.append({
                        "id": f"opt_{j + 1}",
                        "text": option,
                        "is_correct": j == question.get("correct_answer", 0),
                        "explanation": None
                    })
                
                unified_question = {
                    "id": f"q_{i + 1}",
                    "type": "multiple_choice",
                    "question_text": question.get("question", ""),
                    "options": unified_options,
                    "correct_answer": question.get("correct_answer", 0),
                    "explanation": question.get("explanation", ""),
                    "points": question.get("points", 1),
                    "difficulty": question.get("difficulty", "medium"),
                    "tags": question.get("tags", []),
                    "metadata": question.get("metadata", {})
                }
            
            unified_questions.append(unified_question)
        
        return unified_questions
    
    async def migrate_submissions(self):
        """Migrate existing submissions to unified model"""
        print("🔄 Starting submission migration...")
        
        existing_submissions = await self.submissions_collection.find({}).to_list(length=None)
        
        migrated_count = 0
        for submission in existing_submissions:
            try:
                unified_submission = await self._convert_to_unified_submission(submission)
                
                await self.submissions_collection.update_one(
                    {"_id": submission["_id"]},
                    {"$set": unified_submission}
                )
                
                migrated_count += 1
                print(f"✅ Migrated submission: {submission.get('_id')}")
                
            except Exception as e:
                print(f"❌ Failed to migrate submission {submission.get('_id')}: {e}")
        
        print(f"🎉 Submission migration completed! {migrated_count} submissions migrated.")
    
    async def _convert_to_unified_submission(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Convert existing submission to unified model structure"""
        
        # Convert answers to unified format
        unified_answers = []
        answers = submission.get("answers", [])
        
        for answer in answers:
            unified_answer = {
                "question_id": answer.get("question_id", ""),
                "answer": answer.get("answer", ""),
                "is_correct": answer.get("is_correct"),
                "points_earned": answer.get("points_earned", 0),
                "time_spent": answer.get("time_spent", 0)
            }
            unified_answers.append(unified_answer)
        
        # Calculate timing
        started_at = submission.get("started_at", datetime.utcnow())
        submitted_at = submission.get("submitted_at")
        time_spent = 0
        
        if submitted_at:
            time_spent = int((submitted_at - started_at).total_seconds())
        
        unified_submission = {
            "assessment_id": submission.get("assessment_id", ""),
            "student_id": submission.get("student_id", ""),
            "batch_id": submission.get("batch_id"),
            
            # Submission Data
            "answers": unified_answers,
            "total_score": submission.get("total_score", 0),
            "max_score": submission.get("max_score", 0),
            "percentage": submission.get("percentage", 0.0),
            
            # Timing
            "started_at": started_at,
            "submitted_at": submitted_at,
            "time_spent": time_spent,
            
            # Status
            "status": "submitted" if submitted_at else "in_progress",
            "attempt_number": submission.get("attempt_number", 1),
            
            # Additional Data
            "metadata": submission.get("metadata", {})
        }
        
        return unified_submission
    
    async def migrate_batches(self):
        """Migrate existing batches to unified model"""
        print("🔄 Starting batch migration...")
        
        existing_batches = await self.batches_collection.find({}).to_list(length=None)
        
        migrated_count = 0
        for batch in existing_batches:
            try:
                unified_batch = await self._convert_to_unified_batch(batch)
                
                await self.batches_collection.update_one(
                    {"_id": batch["_id"]},
                    {"$set": unified_batch}
                )
                
                migrated_count += 1
                print(f"✅ Migrated batch: {batch.get('batch_name', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Failed to migrate batch {batch.get('_id')}: {e}")
        
        print(f"🎉 Batch migration completed! {migrated_count} batches migrated.")
    
    async def _convert_to_unified_batch(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Convert existing batch to unified model structure"""
        
        unified_batch = {
            "name": batch.get("batch_name", ""),
            "description": batch.get("description"),
            "created_by": batch.get("created_by", ""),
            "created_at": batch.get("created_at", datetime.utcnow()),
            "updated_at": datetime.utcnow(),
            
            # Students
            "student_ids": batch.get("student_ids", []),
            "total_students": batch.get("total_students", 0),
            
            # Analytics
            "average_performance": batch.get("average_performance", 0.0),
            "completion_rate": batch.get("completion_rate", 0.0),
            "common_weaknesses": batch.get("weaknesses", []),
            
            # Settings
            "is_active": batch.get("is_active", True),
            "settings": batch.get("settings", {})
        }
        
        return unified_batch
    
    async def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting unified assessment model migration...")
        
        try:
            await self.migrate_assessments()
            await self.migrate_submissions()
            await self.migrate_batches()
            
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

# Usage example
async def main():
    # Initialize MongoDB client
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.edulearn
    
    # Run migration
    migration = AssessmentMigration(db)
    await migration.run_migration()
    
    # Close client
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
