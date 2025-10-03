from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from ..db import get_db
from ..schemas import ResultCreate, ResultResponse, DetailedResult, TestHistoryItem, QuestionReview, DetailedResultResponse
from ..models import ResultModel
from .endpoints.auth import get_current_user_id

router = APIRouter()

@router.get("/health")
async def results_health_check():
    """Health check endpoint for results router"""
    try:
        print("[DEBUG] [RESULTS_HEALTH] Health check requested")
        
        # Test database connection
        try:
            db = await get_db()
            print("[OK] [RESULTS_HEALTH] Database connection successful")
        except Exception as db_error:
            print(f"[ERROR] [RESULTS_HEALTH] Database connection failed: {str(db_error)}")
            return {
                "success": False,
                "status": "unhealthy",
                "message": "Database connection failed",
                "error": str(db_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Test database ping
        try:
            await db.command("ping")
            print("[OK] [RESULTS_HEALTH] Database ping successful")
        except Exception as ping_error:
            print(f"[ERROR] [RESULTS_HEALTH] Database ping failed: {str(ping_error)}")
            return {
                "success": False,
                "status": "unhealthy",
                "message": "Database ping failed",
                "error": str(ping_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Test basic query
        try:
            total_results = await db.results.count_documents({})
            print(f"[OK] [RESULTS_HEALTH] Database query successful, total results: {total_results}")
        except Exception as query_error:
            print(f"[ERROR] [RESULTS_HEALTH] Database query failed: {str(query_error)}")
            return {
                "success": False,
                "status": "unhealthy",
                "message": "Database query failed",
                "error": str(query_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        print("[OK] [RESULTS_HEALTH] All health checks passed")
        return {
            "success": True,
            "status": "healthy",
            "message": "Results router is healthy",
            "database": "connected",
            "total_results": total_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] [RESULTS_HEALTH] Unexpected error in health check: {str(e)}")
        import traceback
        print(f"[ERROR] [RESULTS_HEALTH] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "status": "error",
            "message": "Unexpected error in health check",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the results router is working"""
    try:
        print("[DEBUG] [RESULTS_TEST] Test endpoint called")
        
        # Test basic functionality
        test_data = {
            "success": True,
            "message": "Results router is working!",
            "endpoints": [
                "/api/health - Health check for results router",
                "/api/test - This test endpoint",
                "/api/test-db - Database connection test",
                "/api/results - Create new assessment result",
                "/api/results/user/{user_id} - Get user results",
                "/api/results/analytics/{user_id} - Get user analytics",
                "/api/results/{result_id} - Get specific result",
                "/api/results/{result_id}/detailed - Get detailed result",
                "/api/results/topic/{topic} - Get results by topic"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print("[OK] [RESULTS_TEST] Test endpoint response prepared")
        return test_data
        
    except Exception as e:
        print(f"[ERROR] [RESULTS_TEST] Error in test endpoint: {str(e)}")
        import traceback
        print(f"[ERROR] [RESULTS_TEST] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": "Results router test failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/test-db")
async def test_database_connection():
    """Test database connection and data for results router"""
    try:
        print("[DEBUG] [RESULTS_TEST_DB] Testing database connection...")
        
        # Test basic connection
        try:
            db = await get_db()
            print("[OK] [RESULTS_TEST_DB] Database connection successful")
        except Exception as db_error:
            print(f"[ERROR] [RESULTS_TEST_DB] Database connection failed: {str(db_error)}")
            return {
                "success": False,
                "message": "Database connection failed",
                "error": str(db_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Test database ping
        try:
            await db.command("ping")
            print("[OK] [RESULTS_TEST_DB] Database ping successful")
        except Exception as ping_error:
            print(f"[ERROR] [RESULTS_TEST_DB] Database ping failed: {str(ping_error)}")
            return {
                "success": False,
                "message": "Database ping failed",
                "error": str(ping_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Count total results
        try:
            total_results = await db.results.count_documents({})
            print(f"[STATS] [RESULTS_TEST_DB] Total results in database: {total_results}")
        except Exception as count_error:
            print(f"[ERROR] [RESULTS_TEST_DB] Count query failed: {str(count_error)}")
            return {
                "success": False,
                "message": "Database count query failed",
                "error": str(count_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get sample results
        try:
            sample_results = await db.results.find().limit(3).to_list(None)
            print(f"[LIST] [RESULTS_TEST_DB] Sample results: {len(sample_results)}")
        except Exception as sample_error:
            print(f"[ERROR] [RESULTS_TEST_DB] Sample query failed: {str(sample_error)}")
            return {
                "success": False,
                "message": "Database sample query failed",
                "error": str(sample_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Test ObjectId conversion
        try:
            if sample_results:
                first_result = sample_results[0]
                result_id = str(first_result["_id"])
                user_id = str(first_result.get("user_id", ""))
                print(f"[OK] [RESULTS_TEST_DB] ObjectId conversion test successful - Result ID: {result_id}, User ID: {user_id}")
            else:
                print("[WARNING] [RESULTS_TEST_DB] No results to test ObjectId conversion")
        except Exception as oid_error:
            print(f"[ERROR] [RESULTS_TEST_DB] ObjectId conversion test failed: {str(oid_error)}")
            return {
                "success": False,
                "message": "ObjectId conversion test failed",
                "error": str(oid_error),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        print("[OK] [RESULTS_TEST_DB] All database tests passed")
        return {
            "success": True,
            "message": "Database connection and queries successful",
            "database_status": "healthy",
            "total_results": total_results,
            "sample_results_count": len(sample_results),
            "objectid_test": "passed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"[ERROR] [RESULTS_TEST_DB] Database test failed: {str(e)}")
        import traceback
        print(f"[ERROR] [RESULTS_TEST_DB] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": "Database test failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/results")
async def create_result(result_data: ResultCreate, user_id: str = Depends(get_current_user_id)):
    """Create a new assessment result"""
    try:
        print(f"[NOTE] [CREATE_RESULT] User {user_id} submitting assessment result for topic: {result_data.topic}")
        
        # Get database with timeout
        try:
            db = await get_db()
            print(f"[OK] [CREATE_RESULT] Database connection successful")
        except Exception as e:
            print(f"[ERROR] [CREATE_RESULT] Database connection failed: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Unable to connect to the database. Please try again later."
            )
        
        # Test database connection
        try:
            await db.command("ping")
            print(f"[OK] [CREATE_RESULT] Database ping successful")
        except Exception as ping_error:
            print(f"[ERROR] [CREATE_RESULT] Database ping failed: {str(ping_error)}")
            raise HTTPException(
                status_code=503,
                detail="Database connection test failed. Please try again later."
            )
        
        # Validate required fields
        if not result_data.user_id or result_data.score is None or not result_data.questions:
            print(f"[ERROR] [CREATE_RESULT] Missing required fields for user {user_id}")
            raise HTTPException(
                status_code=400,
                detail="Missing required fields for result creation"
            )
        
        # Validate user_id format
        try:
            user_object_id = ObjectId(result_data.user_id)
            print(f"[OK] [CREATE_RESULT] Valid user ID format: {result_data.user_id}")
        except Exception as e:
            print(f"[ERROR] [CREATE_RESULT] Invalid user ID format for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID format"
            )
        
        # Calculate additional metrics
        try:
            correct_answers = result_data.score
            incorrect_answers = result_data.total_questions - result_data.score
            percentage = (correct_answers / result_data.total_questions) * 100 if result_data.total_questions > 0 else 0
            
            print(f"[STATS] [CREATE_RESULT] User {user_id} scored {correct_answers}/{result_data.total_questions} ({percentage:.1f}%) on {result_data.difficulty} {result_data.topic}")
        except Exception as calc_error:
            print(f"[ERROR] [CREATE_RESULT] Error calculating metrics: {str(calc_error)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid score or question count data"
            )
        
        # Create result document with enhanced data
        result_doc = {
            "user_id": user_object_id,  # Use validated ObjectId
            "score": result_data.score,
            "total_questions": result_data.total_questions,
            "questions": result_data.questions,
            "user_answers": result_data.user_answers,
            "topic": result_data.topic,
            "difficulty": result_data.difficulty,
            "time_taken": result_data.time_taken,
            "explanations": result_data.explanations,
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
            "percentage": percentage,
            "date": datetime.utcnow()
        }
        
        # Insert into database with timeout handling
        try:
            result = await db.results.insert_one(result_doc)
            result_doc["_id"] = result.inserted_id
            print(f"[OK] [CREATE_RESULT] Assessment result saved successfully for user {user_id}")
        except Exception as e:
            print(f"[ERROR] [CREATE_RESULT] Database insertion failed for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save result to database. Please try again later."
            )
        
        return {
            "success": True,
            "message": "Result saved successfully",
            "result": {
                "id": str(result.inserted_id),
                "score": result_data.score,
                "total_questions": result_data.total_questions,
                "topic": result_data.topic,
                "difficulty": result_data.difficulty,
                "percentage": percentage,
                "time_taken": result_data.time_taken,
                "date": result_doc["date"].isoformat()
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"[ERROR] [CREATE_RESULT] Unexpected error for user {user_id}: {str(e)}")
        import traceback
        print(f"[ERROR] [CREATE_RESULT] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while saving your result. Please try again later."
        )

@router.get("/results/user/{user_id}")
async def get_user_results(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get all results for a specific user with enhanced data"""
    try:
        print(f"[LIST] [USER_RESULTS] User {current_user_id} requesting results")
        
        # Ensure user can only access their own results
        if user_id != current_user_id:
            print(f"[ERROR] [USER_RESULTS] Access denied: user {current_user_id} trying to access results for {user_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate user_id format
        try:
            user_object_id = ObjectId(user_id)
            print(f"[OK] [USER_RESULTS] Valid user ID format: {user_id}")
        except Exception as e:
            print(f"[ERROR] [USER_RESULTS] Invalid user ID format: {user_id}, error: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid user ID format"
            )
        
        # Get database connection with better error handling
        try:
            db = await get_db()
            print(f"[OK] [USER_RESULTS] Database connection successful")
        except Exception as db_error:
            print(f"[ERROR] [USER_RESULTS] Database connection failed: {str(db_error)}")
            raise HTTPException(
                status_code=503,
                detail="Unable to connect to the database. Please try again later."
            )
        
        # Test database connection
        try:
            await db.command("ping")
            print(f"[OK] [USER_RESULTS] Database ping successful")
        except Exception as ping_error:
            print(f"[ERROR] [USER_RESULTS] Database ping failed: {str(ping_error)}")
            raise HTTPException(
                status_code=503,
                detail="Database connection test failed. Please try again later."
            )
        
        # Get results sorted by date (newest first)
        query = {"user_id": user_object_id}
        print(f"[DEBUG] [USER_RESULTS] Querying results with: {query}")
        
        try:
            results = await db.results.find(query).sort("date", -1).to_list(None)
            print(f"[LIST] [USER_RESULTS] Found {len(results)} assessment results for user {user_id}")
        except Exception as query_error:
            print(f"[ERROR] [USER_RESULTS] Database query failed: {str(query_error)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve assessment data. Please try again later."
            )
        
        # Format results for response with enhanced data and error handling
        try:
            formatted_results = []
            for result in results:
                # Safely get values with defaults
                score = result.get("score", 0)
                total_questions = result.get("total_questions", 0)
                percentage = result.get("percentage", (score / total_questions * 100) if total_questions > 0 else 0)
                
                formatted_result = {
                    "id": str(result["_id"]),
                    "score": score,
                    "total_questions": total_questions,
                    "topic": result.get("topic", "Unknown"),
                    "difficulty": result.get("difficulty", "Unknown"),
                    "percentage": round(percentage, 2),
                    "time_taken": result.get("time_taken"),
                    "date": result.get("date", datetime.utcnow()).isoformat()
                }
                formatted_results.append(formatted_result)
            
            print(f"[OK] [USER_RESULTS] Formatted {len(formatted_results)} results for user {user_id}")
            
        except Exception as format_error:
            print(f"[ERROR] [USER_RESULTS] Error formatting results: {str(format_error)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to format assessment data. Please try again later."
            )
        
        print(f"[OK] [USER_RESULTS] Returning {len(formatted_results)} results to user {user_id}")
        
        return {
            "success": True,
            "results": formatted_results
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"[ERROR] [USER_RESULTS] Unexpected error for user {user_id}: {str(e)}")
        import traceback
        print(f"[ERROR] [USER_RESULTS] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching results. Please try again later."
        )

@router.get("/results/{result_id}")
async def get_result(result_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get a specific result by ID with detailed information"""
    try:
        print(f"[LIST] [RESULT] User {current_user_id} requesting specific result {result_id}")
        
        db = await get_db()
        
        # Get result
        result = await db.results.find_one({"_id": ObjectId(result_id)})
        
        if not result:
            print(f"[ERROR] [RESULT] Result {result_id} not found")
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Ensure user can only access their own results
        if str(result["user_id"]) != current_user_id:
            print(f"[ERROR] [RESULT] Access denied: user {current_user_id} trying to access result {result_id} owned by {result['user_id']}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Calculate percentage if not stored
        percentage = result.get("percentage", (result["score"] / result["total_questions"]) * 100)
        
        print(f"[OK] [RESULT] Returning detailed result {result_id} to user {current_user_id}")
        
        return {
            "success": True,
            "result": {
                "id": str(result["_id"]),
                "user_id": str(result["user_id"]),
                "score": result["score"],
                "total_questions": result["total_questions"],
                "questions": result["questions"],
                "user_answers": result["user_answers"],
                "topic": result["topic"],
                "difficulty": result["difficulty"],
                "percentage": percentage,
                "time_taken": result.get("time_taken"),
                "explanations": result.get("explanations"),
                "correct_answers": result.get("correct_answers", result["score"]),
                "incorrect_answers": result.get("incorrect_answers", result["total_questions"] - result["score"]),
                "date": result["date"].isoformat()
            }
        }
        
    except Exception as e:
        print(f"[ERROR] [RESULT] Error fetching result {result_id} for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch result: {str(e)}"
        )

@router.get("/results/{result_id}/detailed")
async def get_detailed_result(result_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get detailed result with question reviews and explanations"""
    try:
        print(f"[LIST] [RESULT] User {current_user_id} requesting detailed result {result_id}")
        
        db = await get_db()
        
        # Get result
        result = await db.results.find_one({"_id": ObjectId(result_id)})
        
        if not result:
            print(f"[ERROR] [RESULT] Detailed result {result_id} not found")
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Ensure user can only access their own results
        if str(result["user_id"]) != current_user_id:
            print(f"[ERROR] [RESULT] Access denied: user {current_user_id} trying to access detailed result {result_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Calculate metrics
        percentage = result.get("percentage", (result["score"] / result["total_questions"]) * 100)
        correct_answers = result.get("correct_answers", result["score"])
        incorrect_answers = result.get("incorrect_answers", result["total_questions"] - result["score"])
        
        # Create detailed result
        detailed_result = DetailedResult(
            id=str(result["_id"]),
            user_id=str(result["user_id"]),
            score=result["score"],
            total_questions=result["total_questions"],
            questions=result["questions"],
            user_answers=result["user_answers"],
            topic=result["topic"],
            difficulty=result["difficulty"],
            time_taken=result.get("time_taken"),
            explanations=result.get("explanations"),
            date=result["date"],
            percentage=percentage,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers
        )
        
        # Create question reviews
        question_reviews = []
        for i, question in enumerate(result["questions"]):
            user_answer = result["user_answers"][i] if i < len(result["user_answers"]) else ""
            correct_answer = question.get("answer", "")
            is_correct = user_answer == correct_answer
            
            # Get explanation if available
            explanation = None
            if result.get("explanations") and i < len(result["explanations"]):
                explanation = result["explanations"][i].get("explanation", "")
            
            question_review = QuestionReview(
                question_index=i,
                question=question.get("question", ""),
                options=question.get("options", []),
                correct_answer=correct_answer,
                user_answer=user_answer,
                is_correct=is_correct,
                explanation=explanation
            )
            question_reviews.append(question_review)
        
        print(f"[OK] [RESULT] Returning detailed result {result_id} with {len(question_reviews)} question reviews to user {current_user_id}")
        
        return DetailedResultResponse(
            success=True,
            result=detailed_result,
            question_reviews=question_reviews
        )
        
    except Exception as e:
        print(f"[ERROR] [RESULT] Error fetching detailed result {result_id} for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch detailed result: {str(e)}"
        )

@router.get("/results/analytics/{user_id}")
async def get_user_analytics(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get analytics for a user"""
    try:
        print(f"[STATS] [ANALYTICS] User {current_user_id} requesting analytics")
        
        # Ensure user can only access their own analytics
        if user_id != current_user_id:
            print(f"[ERROR] [ANALYTICS] Access denied: user {current_user_id} trying to access analytics for {user_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate user_id format
        try:
            user_object_id = ObjectId(user_id)
            print(f"[OK] [ANALYTICS] Valid user ID format: {user_id}")
        except Exception as e:
            print(f"[ERROR] [ANALYTICS] Invalid user ID format: {user_id}, error: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid user ID format"
            )
        
        # Get database connection with better error handling
        try:
            db = await get_db()
            print(f"[OK] [ANALYTICS] Database connection successful")
        except Exception as db_error:
            print(f"[ERROR] [ANALYTICS] Database connection failed: {str(db_error)}")
            raise HTTPException(
                status_code=503,
                detail="Unable to connect to the database. Please try again later."
            )
        
        # Test database connection
        try:
            await db.command("ping")
            print(f"[OK] [ANALYTICS] Database ping successful")
        except Exception as ping_error:
            print(f"[ERROR] [ANALYTICS] Database ping failed: {str(ping_error)}")
            raise HTTPException(
                status_code=503,
                detail="Database connection test failed. Please try again later."
            )
        
        # Get all results for user
        query = {"user_id": user_object_id}
        print(f"[DEBUG] [ANALYTICS] Querying results with: {query}")
        
        try:
            results = await db.results.find(query).to_list(None)
            print(f"[STATS] [ANALYTICS] Found {len(results)} assessment results for user {user_id}")
        except Exception as query_error:
            print(f"[ERROR] [ANALYTICS] Database query failed: {str(query_error)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve assessment data. Please try again later."
            )
        
        if not results:
            print(f"[STATS] [ANALYTICS] No results found for user {user_id}, returning empty analytics")
            return {
                "success": True,
                "analytics": {
                    "total_assessments": 0,
                    "average_score": 0,
                    "total_questions": 0,
                    "topics": [],
                    "recent_performance": []
                }
            }
        
        # Calculate analytics with error handling
        try:
            total_assessments = len(results)
            total_score = sum(r.get("score", 0) for r in results)
            average_score = total_score / total_assessments if total_assessments > 0 else 0
            total_questions = sum(r.get("total_questions", 0) for r in results)
            
            print(f"[STATS] [ANALYTICS] User {user_id} analytics - {total_assessments} assessments, avg score: {average_score:.1f}, total questions: {total_questions}")
            
            # Get unique topics
            topics = list(set(r.get("topic", "Unknown") for r in results))
            
            # Get recent performance (last 5 assessments)
            recent_results = sorted(results, key=lambda x: x.get("date", datetime.utcnow()), reverse=True)[:5]
            recent_performance = [
                {
                    "score": r.get("score", 0),
                    "total_questions": r.get("total_questions", 0),
                    "topic": r.get("topic", "Unknown"),
                    "difficulty": r.get("difficulty", "Unknown"),
                    "date": r.get("date", datetime.utcnow()).isoformat()
                }
                for r in recent_results
            ]
            
            # Get topic statistics
            topic_stats = {}
            for result in results:
                topic = result.get("topic", "Unknown")
                if topic not in topic_stats:
                    topic_stats[topic] = {"count": 0, "total_score": 0, "total_questions": 0}
                topic_stats[topic]["count"] += 1
                topic_stats[topic]["total_score"] += result.get("score", 0)
                topic_stats[topic]["total_questions"] += result.get("total_questions", 0)
            
            # Calculate average scores for topics
            for topic in topic_stats:
                stats = topic_stats[topic]
                stats["average_score"] = stats["total_score"] / stats["count"] if stats["count"] > 0 else 0
            
            print(f"[STATS] [ANALYTICS] Calculated analytics for {len(topics)} topics for user {user_id}")
            
        except Exception as calc_error:
            print(f"[ERROR] [ANALYTICS] Error calculating analytics: {str(calc_error)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to calculate analytics. Please try again later."
            )
        
        analytics_data = {
            "total_assessments": total_assessments,
            "average_score": round(average_score, 2),
            "total_questions": total_questions,
            "topics": topics,
            "recent_results": recent_performance,
            "topic_stats": topic_stats
        }
        
        print(f"[OK] [ANALYTICS] Returning analytics to user {user_id}")
        
        return {
            "success": True,
            "analytics": analytics_data
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"[ERROR] [ANALYTICS] Unexpected error for user {user_id}: {str(e)}")
        import traceback
        print(f"[ERROR] [ANALYTICS] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching analytics. Please try again later."
        )

@router.get("/results/topic/{topic}")
async def get_results_by_topic(
    topic: str,
    difficulty: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get results filtered by topic and optional difficulty"""
    try:
        print(f"[LIST] [RESULTS] User {current_user_id} requesting results for topic: {topic}" + (f" (difficulty: {difficulty})" if difficulty else ""))
        
        db = await get_db()
        
        # Build query
        query = {
            "user_id": ObjectId(current_user_id),
            "topic": {"$regex": topic, "$options": "i"}
        }
        
        if difficulty:
            query["difficulty"] = difficulty
        
        # Get results
        results = await db.results.find(query).sort("date", -1).to_list(None)
        print(f"[LIST] [RESULTS] Found {len(results)} results for topic '{topic}' for user {current_user_id}")
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": str(result["_id"]),
                "score": result["score"],
                "total_questions": result["total_questions"],
                "topic": result["topic"],
                "difficulty": result["difficulty"],
                "date": result["date"].isoformat()
            })
        
        print(f"[OK] [RESULTS] Returning {len(formatted_results)} topic results to user {current_user_id}")
        
        return {
            "success": True,
            "results": formatted_results
        }
        
    except Exception as e:
        print(f"[ERROR] [RESULTS] Error fetching topic results for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch results: {str(e)}"
        ) 