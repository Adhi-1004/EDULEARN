from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from llm_api import (
    generate_question,
    generate_question_feedback,
    generate_assugnment_feedback,
    chat,
    generate_personalized_coding_problems,
    evaluate_code_with_ai,
)
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from pdfParsing import parse_PDF
from models import DatabaseModels
import logging
import datetime
import json
import hashlib
import secrets
import os
from functools import wraps

app = Flask(__name__)
cors = CORS(app, origins=['*'])
api = Api(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_request_info(endpoint, method, data=None, files=None):
    """Log detailed request information"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"🔍 API REQUEST DEBUG - {timestamp}")
    print(f"📍 Endpoint: {method} {endpoint}")
    print(f"🌐 Client IP: {request.remote_addr}")
    print(f"👤 User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    
    if data:
        print(f"📦 Request Data: {json.dumps(data, indent=2)}")
    
    if files:
        print(f"📁 Files Received: {list(files.keys())}")
        for filename, file in files.items():
            print(f"   - {filename}: {file.filename} ({file.content_type})")
    
    print(f"{'='*60}\n")

def log_response_info(endpoint, response_data, status_code=200):
    """Log response information"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"📤 API RESPONSE DEBUG - {timestamp}")
    print(f"📍 Endpoint: {endpoint}")
    print(f"📊 Status Code: {status_code}")
    print(f"📄 Response Type: {type(response_data)}")
    
    if isinstance(response_data, dict):
        print(f"📦 Response Data: {json.dumps(response_data, indent=2)}")
    else:
        print(f"📦 Response Data: {response_data}")
    
    print(f"{'='*60}\n")



"""
Bellow function is for Generating Question analysis
"""
getQuestion_post_parse = reqparse.RequestParser()
getQuestion_post_parse.add_argument("Topic", type=str, help='Give the topic', required=True, location=['json','form'])
getQuestion_post_parse.add_argument("Type", type=str, help='Give the Type', required=True, location=['json','form'])
getQuestion_post_parse.add_argument("Quantity", type=int, help='Give the Quantity', required=True, location=['json','form'])
getQuestion_post_parse.add_argument("Subject", type=str, help='Subject (optional)', required=False, location=['json','form'])
getQuestion_post_parse.add_argument("Difficulty", type=str, help='Difficulty (optional)', required=False, location=['json','form'])

#For Generating the questions
class getQuestion(Resource):
    def get(self):
        log_request_info('/getQuestions', 'GET')
        response = {"Reply": "Hosted successfully"}
        log_response_info('/getQuestions', response)
        return response, 200
    
    def post(self):
        print(f"\n🚀 GENERATING QUESTIONS REQUEST")
        payload = request.get_json(silent=True) or {}
        log_request_info('/getQuestions', 'POST', data={
            "Topic": payload.get('Topic') or request.form.get('Topic'),
            "Type": payload.get('Type') or request.form.get('Type'),
            "Quantity": payload.get('Quantity') or request.form.get('Quantity'),
            "Subject": payload.get('Subject'),
            "Difficulty": payload.get('Difficulty'),
        })
        
        try:
            data = getQuestion_post_parse.parse_args()
            print(f"✅ Parsed Arguments: Topic='{data['Topic']}', Type='{data['Type']}', Quantity={data['Quantity']}")
            
            print(f"🤖 Calling Gemini AI for question generation...")
            response = generate_question(
                topic=data["Topic"],
                type=data["Type"],
                questions=data["Quantity"],
                subject=data.get("Subject"),
                difficulty=data.get("Difficulty")
            )
            print(f"✅ Questions generated successfully!")
            
            log_response_info('/getQuestions', response)
            return response, 200
            
        except Exception as e:
            error_msg = f"❌ Error generating questions: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            return {"error": error_msg}, 500
    

api.add_resource(getQuestion,'/getQuestions')




"""
Bellow function is for Assignment Feedback analysis
"""


getAssignmentFeedback_post_parse = reqparse.RequestParser()
getAssignmentFeedback_post_parse.add_argument("Question",type=FileStorage,location='files',required=True,help="PDF file is required")
getAssignmentFeedback_post_parse.add_argument("Answer",type=FileStorage,location='files',required=True,help="PDF file is required")

class getAssignmentFeedback(Resource):
    def post(self):
        print(f"\n📝 ASSIGNMENT FEEDBACK REQUEST")
        log_request_info('/getAssignmentFeedback', 'POST', files=request.files)
        
        try:
            data = getAssignmentFeedback_post_parse.parse_args()
            Answer_pdf_file = data["Answer"]
            Question_pdf_file = data["Question"]
            
            print(f"📄 Processing PDF files:")
            print(f"   - Question PDF: {Question_pdf_file.filename}")
            print(f"   - Answer PDF: {Answer_pdf_file.filename}")
            
            print(f"🔍 Extracting text from PDFs...")
            Answer_extracted_text = parse_PDF(Answer_pdf_file)
            Question_extracted_text = parse_PDF(Question_pdf_file)
            print(f"✅ Text extraction completed!")
            print(f"   - Question text length: {len(Question_extracted_text)} characters")
            print(f"   - Answer text length: {len(Answer_extracted_text)} characters")
            
            print(f"🤖 Calling Gemini AI for assignment feedback...")
            feedback = generate_assugnment_feedback(Question_extracted_text, Answer_extracted_text)
            print(f"✅ Assignment feedback generated successfully!")
            
            log_response_info('/getAssignmentFeedback', feedback)
            return feedback, 200
            
        except Exception as e:
            error_msg = f"❌ Error processing assignment feedback: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            return {"error": error_msg}, 500
    
api.add_resource(getAssignmentFeedback,'/getAssignmentFeedback')








"""
Bellow function is for Quiz Feedback analysis
"""
getQuizFeedback_post_parse = reqparse.RequestParser()

getQuizFeedback_post_parse.add_argument("Questions", type=dict, action='append', location='json', help="Provide list of question objects",required=True)
getQuizFeedback_post_parse.add_argument("Score", type=int, action='append', location='json', help="Provide list of integer scores",required=True)

class getQuizFeedback(Resource):
    def post(self):
        print(f"\n📊 QUIZ FEEDBACK REQUEST")
        log_request_info('/getQuizFeedback', 'POST', data=request.get_json())
        
        try:
            data = getQuizFeedback_post_parse.parse_args()
            print(f"✅ Parsed Quiz Data:")
            print(f"   - Number of questions: {len(data['Questions'])}")
            print(f"   - Number of scores: {len(data['Score'])}")
            print(f"   - Questions: {data['Questions']}")
            print(f"   - Scores: {data['Score']}")
            
            print(f"🤖 Calling Gemini AI for quiz feedback...")
            response = generate_question_feedback(data["Questions"], data["Score"])
            print(f"✅ Quiz feedback generated successfully!")
            
            log_response_info('/getQuizFeedback', response)
            return response, 200
            
        except Exception as e:
            error_msg = f"❌ Error processing quiz feedback: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            return {"error": error_msg}, 500
    
api.add_resource(getQuizFeedback,'/getQuizFeedback')

"""
Bellow function is for ChatBot
"""
ChatBot_post_parse = reqparse.RequestParser()
ChatBot_post_parse.add_argument("Message",help = "Send the messeges",required=True)
class ChatBot(Resource):
    def post(self):
        print(f"\n💬 CHATBOT REQUEST")
        log_request_info('/ChatBot', 'POST', data=request.get_json())
        
        try:
            args = ChatBot_post_parse.parse_args()
            user_message = args["Message"]
            print(f"👤 User Message: '{user_message}'")
            
            print(f"🤖 Calling Gemini AI for chatbot response...")
            reply = chat(user_message)
            print(f"✅ Chatbot response generated!")
            print(f"🤖 AI Reply: '{reply}'")
            
            response = {"reply": reply}
            log_response_info('/ChatBot', response)
            return response, 200
            
        except Exception as e:
            error_msg = f"❌ Error in chatbot: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 500
    
    def get(self):
        log_request_info('/ChatBot', 'GET')
        response = {"Hello": "Hiii"}
        log_response_info('/ChatBot', response)
        return response, 200
    
api.add_resource(ChatBot,'/ChatBot')






"""
New: Coding AI routes (personalized generation and AI evaluation)
"""

coding_gen_post_parse = reqparse.RequestParser()
coding_gen_post_parse.add_argument("user_id", type=str, required=True, location='json')
coding_gen_post_parse.add_argument("topic", type=str, required=True, location='json')
coding_gen_post_parse.add_argument("difficulty", type=str, required=True, location='json')
coding_gen_post_parse.add_argument("count", type=int, required=True, location='json')
coding_gen_post_parse.add_argument("preferred_languages", type=list, required=False, location='json')

class GeneratePersonalizedCoding(Resource):
    def post(self):
        log_request_info('/coding/generate', 'POST', data=request.get_json())
        try:
            args = coding_gen_post_parse.parse_args()
            payload = {
                "user_id": args["user_id"],
                "topic": args["topic"],
                "difficulty": args["difficulty"],
                "count": args["count"],
                "preferred_languages": args.get("preferred_languages") or [],
            }
            result = generate_personalized_coding_problems(payload)
            log_response_info('/coding/generate', result)
            return result, 200
        except Exception as e:
            error_msg = {"error": f"Failed to generate coding problems: {str(e)}"}
            logger.error(error_msg)
            return error_msg, 500


code_eval_post_parse = reqparse.RequestParser()
code_eval_post_parse.add_argument("language", type=str, required=True, location='json')
code_eval_post_parse.add_argument("code", type=str, required=True, location='json')
code_eval_post_parse.add_argument("problem", type=dict, required=True, location='json')
code_eval_post_parse.add_argument("test_cases", type=list, required=True, location='json')

class EvaluateCode(Resource):
    def post(self):
        log_request_info('/coding/evaluate', 'POST', data=request.get_json())
        try:
            args = code_eval_post_parse.parse_args()
            payload = {
                "language": args["language"],
                "code": args["code"],
                "problem": args["problem"],
                "test_cases": args["test_cases"],
            }
            result = evaluate_code_with_ai(payload)
            log_response_info('/coding/evaluate', result)
            return result, 200
        except Exception as e:
            error_msg = {"error": f"Failed to evaluate code: {str(e)}"}
            logger.error(error_msg)
            return error_msg, 500


api.add_resource(GeneratePersonalizedCoding, '/coding/generate')
api.add_resource(EvaluateCode, '/coding/evaluate')

"""
Leaderboard: persist MCQ results and query top scores
"""

import os as _os
import uuid as _uuid

_LEADERBOARD_FILE = _os.path.join(_os.path.dirname(__file__), 'leaderboard.json')

def _read_leaderboard():
    try:
        if not _os.path.exists(_LEADERBOARD_FILE):
            return []
        with open(_LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def _write_leaderboard(items):
    try:
        with open(_LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to write leaderboard: {e}")


leaderboard_get_parse = reqparse.RequestParser()
leaderboard_get_parse.add_argument('subject', type=str, required=False, location='args')
leaderboard_get_parse.add_argument('difficulty', type=str, required=False, location='args')
leaderboard_get_parse.add_argument('limit', type=int, required=False, location='args', default=20)

class Leaderboard(Resource):
    def get(self):
        log_request_info('/leaderboard', 'GET', data=request.args.to_dict())
        items = _read_leaderboard()
        args = leaderboard_get_parse.parse_args()
        subject = (args.get('subject') or '').strip().lower()
        difficulty = (args.get('difficulty') or '').strip().lower()
        if subject:
            items = [i for i in items if (i.get('subject','').lower()==subject)]
        if difficulty:
            items = [i for i in items if (i.get('difficulty','').lower()==difficulty)]
        # Sort by score desc, then by created desc
        items.sort(key=lambda x: (x.get('percentage',0), x.get('created_at','')), reverse=True)
        out = items[: max(1, args.get('limit') or 20)]
        log_response_info('/leaderboard', {"count": len(out)})
        return {"items": out}, 200


save_result_post_parse = reqparse.RequestParser()
save_result_post_parse.add_argument('user_id', type=str, required=True, location='json')
save_result_post_parse.add_argument('user_name', type=str, required=False, location='json')
save_result_post_parse.add_argument('subject', type=str, required=False, location='json')
save_result_post_parse.add_argument('topic', type=str, required=False, location='json')
save_result_post_parse.add_argument('difficulty', type=str, required=False, location='json')
save_result_post_parse.add_argument('score', type=int, required=True, location='json')
save_result_post_parse.add_argument('total', type=int, required=True, location='json')
save_result_post_parse.add_argument('duration_ms', type=int, required=False, location='json')

class SaveMCQResult(Resource):
    def post(self):
        log_request_info('/results/mcq', 'POST', data=request.get_json())
        try:
            args = save_result_post_parse.parse_args()
            items = _read_leaderboard()
            entry = {
                "id": str(_uuid.uuid4()),
                "user_id": args['user_id'],
                "user_name": args.get('user_name') or 'Student',
                "subject": args['subject'],
                "topic": args.get('topic') or '',
                "difficulty": args.get('difficulty') or '',
                "score": int(args['score']),
                "total": int(args['total']),
                "percentage": round((int(args['score'])/max(1,int(args['total'])))*100, 2),
                "duration_ms": args.get('duration_ms') or 0,
                "created_at": datetime.datetime.utcnow().isoformat() + 'Z'
            }
            items.append(entry)
            _write_leaderboard(items)
            log_response_info('/results/mcq', entry)
            return {"saved": True, "entry": entry}, 200
        except Exception as e:
            logger.error(f"Failed to save result: {e}")
            return {"error": str(e)}, 500

# Authentication and utility functions
def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt = hashed[:32]
        pwd_hash = hashed[32:]
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex() == pwd_hash
    except:
        return False

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, skip auth - in production, implement proper JWT
        return f(*args, **kwargs)
    return decorated_function

# Student Dashboard Endpoints
class StudentAssignments(Resource):
    @require_auth
    def get(self):
        try:
            student_id = request.args.get('student_id')
            section = request.args.get('section')
            
            if not student_id:
                return {"error": "student_id required"}, 400
            
            assignments = DatabaseModels.get_assignments_by_student(student_id, section)
            return {"assignments": assignments}, 200
        except Exception as e:
            logger.error(f"Failed to get assignments: {e}")
            return {"error": str(e)}, 500

class StudentSubmissions(Resource):
    @require_auth
    def get(self):
        try:
            student_id = request.args.get('student_id')
            if not student_id:
                return {"error": "student_id required"}, 400
            
            submissions = DatabaseModels.get_submissions_by_student(student_id)
            return {"submissions": submissions}, 200
        except Exception as e:
            logger.error(f"Failed to get submissions: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['student_id', 'assignment_id', 'content']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            submission_id = DatabaseModels.create_submission(data)
            return {"submission_id": submission_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create submission: {e}")
            return {"error": str(e)}, 500

class StudyMaterials(Resource):
    @require_auth
    def get(self):
        try:
            subject = request.args.get('subject')
            material_type = request.args.get('type')
            
            materials = DatabaseModels.get_study_materials(subject, material_type)
            return {"materials": materials}, 200
        except Exception as e:
            logger.error(f"Failed to get study materials: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['title', 'subject', 'type', 'description', 'teacher_id']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            material_id = DatabaseModels.create_study_material(data)
            return {"material_id": material_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create study material: {e}")
            return {"error": str(e)}, 500

class VirtualLabs(Resource):
    @require_auth
    def get(self):
        try:
            subject = request.args.get('subject')
            labs = DatabaseModels.get_virtual_labs(subject)
            return {"labs": labs}, 200
        except Exception as e:
            logger.error(f"Failed to get virtual labs: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['title', 'subject', 'description', 'type', 'difficulty', 'estimated_time']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            lab_id = DatabaseModels.create_virtual_lab(data)
            return {"lab_id": lab_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create virtual lab: {e}")
            return {"error": str(e)}, 500

class Discussions(Resource):
    @require_auth
    def get(self):
        try:
            subject = request.args.get('subject')
            discussions = DatabaseModels.get_discussions(subject)
            return {"discussions": discussions}, 200
        except Exception as e:
            logger.error(f"Failed to get discussions: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['title', 'subject', 'author_id', 'content']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            discussion_id = DatabaseModels.create_discussion(data)
            return {"discussion_id": discussion_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create discussion: {e}")
            return {"error": str(e)}, 500

class StudyGroups(Resource):
    @require_auth
    def get(self):
        try:
            subject = request.args.get('subject')
            student_id = request.args.get('student_id')
            
            groups = DatabaseModels.get_study_groups(subject, student_id)
            return {"groups": groups}, 200
        except Exception as e:
            logger.error(f"Failed to get study groups: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['name', 'subject', 'creator_id', 'description', 'max_members']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            group_id = DatabaseModels.create_study_group(data)
            return {"group_id": group_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create study group: {e}")
            return {"error": str(e)}, 500

class StudentProjects(Resource):
    @require_auth
    def get(self):
        try:
            student_id = request.args.get('student_id')
            if not student_id:
                return {"error": "student_id required"}, 400
            
            projects = DatabaseModels.get_projects_by_student(student_id)
            return {"projects": projects}, 200
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['title', 'description', 'student_id', 'subject']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            project_id = DatabaseModels.create_project(data)
            return {"project_id": project_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            return {"error": str(e)}, 500

class StudentNotes(Resource):
    @require_auth
    def get(self):
        try:
            student_id = request.args.get('student_id')
            subject = request.args.get('subject')
            
            if not student_id:
                return {"error": "student_id required"}, 400
            
            notes = DatabaseModels.get_notes_by_student(student_id, subject)
            return {"notes": notes}, 200
        except Exception as e:
            logger.error(f"Failed to get notes: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['title', 'content', 'student_id', 'subject']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            note_id = DatabaseModels.create_note(data)
            return {"note_id": note_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            return {"error": str(e)}, 500

class StudentNotifications(Resource):
    @require_auth
    def get(self):
        try:
            user_id = request.args.get('user_id')
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            
            if not user_id:
                return {"error": "user_id required"}, 400
            
            notifications = DatabaseModels.get_notifications_by_user(user_id, unread_only)
            return {"notifications": notifications}, 200
        except Exception as e:
            logger.error(f"Failed to get notifications: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['user_id', 'title', 'message', 'type']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            notification_id = DatabaseModels.create_notification(data)
            return {"notification_id": notification_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return {"error": str(e)}, 500

class StudentAnalytics(Resource):
    @require_auth
    def get(self):
        try:
            student_id = request.args.get('student_id')
            if not student_id:
                return {"error": "student_id required"}, 400
            
            analytics = DatabaseModels.get_student_analytics(student_id)
            return {"analytics": analytics}, 200
        except Exception as e:
            logger.error(f"Failed to get student analytics: {e}")
            return {"error": str(e)}, 500

# Teacher Dashboard Endpoints
class TeacherAssignments(Resource):
    @require_auth
    def get(self):
        try:
            teacher_id = request.args.get('teacher_id')
            if not teacher_id:
                return {"error": "teacher_id required"}, 400
            
            assignments = DatabaseModels.get_assignments_by_teacher(teacher_id)
            return {"assignments": assignments}, 200
        except Exception as e:
            logger.error(f"Failed to get teacher assignments: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['title', 'description', 'teacher_id', 'subject', 'due_date']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            assignment_id = DatabaseModels.create_assignment(data)
            return {"assignment_id": assignment_id, "status": "created"}, 201
        except Exception as e:
            logger.error(f"Failed to create assignment: {e}")
            return {"error": str(e)}, 500

class TeacherSubmissions(Resource):
    @require_auth
    def get(self):
        try:
            assignment_id = request.args.get('assignment_id')
            if not assignment_id:
                return {"error": "assignment_id required"}, 400
            
            submissions = DatabaseModels.get_submissions_by_assignment(assignment_id)
            return {"submissions": submissions}, 200
        except Exception as e:
            logger.error(f"Failed to get submissions: {e}")
            return {"error": str(e)}, 500

class ClassAnalytics(Resource):
    @require_auth
    def get(self):
        try:
            teacher_id = request.args.get('teacher_id')
            section = request.args.get('section')
            
            if not teacher_id:
                return {"error": "teacher_id required"}, 400
            
            analytics = DatabaseModels.get_class_analytics(teacher_id, section)
            return {"analytics": analytics}, 200
        except Exception as e:
            logger.error(f"Failed to get class analytics: {e}")
            return {"error": str(e)}, 500

# User Management Endpoints
class UserProfile(Resource):
    @require_auth
    def get(self):
        try:
            user_id = request.args.get('user_id')
            email = request.args.get('email')
            
            if user_id:
                user = DatabaseModels.get_user_by_id(user_id)
            elif email:
                user = DatabaseModels.get_user_by_email(email)
            else:
                return {"error": "user_id or email required"}, 400
            
            if not user:
                return {"error": "User not found"}, 404
            
            # Remove sensitive information
            user.pop('password', None)
            user['id'] = str(user['_id'])
            user.pop('_id', None)
            
            return {"user": user}, 200
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return {"error": str(e)}, 500
    
    @require_auth
    def put(self):
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return {"error": "user_id required"}, 400
            
            # Remove sensitive fields that shouldn't be updated directly
            update_data = {k: v for k, v in data.items() if k not in ['user_id', 'password', '_id']}
            
            success = DatabaseModels.update_user(user_id, update_data)
            if success:
                return {"status": "updated"}, 200
            else:
                return {"error": "Update failed"}, 400
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return {"error": str(e)}, 500

class UserRegistration(Resource):
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['name', 'email', 'password', 'role']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            # Check if user already exists
            existing_user = DatabaseModels.get_user_by_email(data['email'])
            if existing_user:
                return {"error": "User already exists"}, 409
            
            # Hash password
            data['password'] = hash_password(data['password'])
            
            user_id = DatabaseModels.create_user(data)
            return {"user_id": user_id, "status": "registered"}, 201
        except Exception as e:
            logger.error(f"Failed to register user: {e}")
            return {"error": str(e)}, 500

class UserLogin(Resource):
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['email', 'password']
            
            if not all(field in data for field in required_fields):
                return {"error": f"Required fields: {required_fields}"}, 400
            
            user = DatabaseModels.get_user_by_email(data['email'])
            if not user:
                return {"error": "Invalid credentials"}, 401
            
            if not verify_password(data['password'], user['password']):
                return {"error": "Invalid credentials"}, 401
            
            # Update last login
            DatabaseModels.update_user(str(user['_id']), {'last_login': datetime.datetime.utcnow()})
            
            # Remove sensitive information
            user.pop('password', None)
            user['id'] = str(user['_id'])
            user.pop('_id', None)
            
            return {"user": user, "status": "logged_in"}, 200
        except Exception as e:
            logger.error(f"Failed to login user: {e}")
            return {"error": str(e)}, 500

# AI-Powered Endpoints
class AIRecommendations(Resource):
    @require_auth
    def get(self):
        try:
            student_id = request.args.get('student_id')
            if not student_id:
                return {"error": "student_id required"}, 400
            
            # Get student analytics
            analytics = DatabaseModels.get_student_analytics(student_id)
            
            # Generate AI recommendations based on performance
            recommendations = []
            if analytics['average_grade'] < 70:
                recommendations.append({
                    "type": "study_improvement",
                    "title": "Focus on Weak Areas",
                    "description": "Consider reviewing fundamental concepts and seeking additional help.",
                    "priority": "high"
                })
            
            if analytics['completion_rate'] < 80:
                recommendations.append({
                    "type": "time_management",
                    "title": "Improve Assignment Completion",
                    "description": "Create a study schedule to better manage assignment deadlines.",
                    "priority": "medium"
                })
            
            return {"recommendations": recommendations}, 200
        except Exception as e:
            logger.error(f"Failed to get AI recommendations: {e}")
            return {"error": str(e)}, 500

# File Upload Endpoint
class FileUpload(Resource):
    @require_auth
    def post(self):
        try:
            if 'file' not in request.files:
                return {"error": "No file provided"}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {"error": "No file selected"}, 400
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Secure filename and save
            if not file.filename:
                return {"error": "Invalid filename"}, 400
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            return {"filename": filename, "status": "uploaded"}, 200
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return {"error": str(e)}, 500

# Register all endpoints
api.add_resource(Leaderboard, '/leaderboard')
api.add_resource(SaveMCQResult, '/results/mcq')

# Student endpoints
api.add_resource(StudentAssignments, '/student/assignments')
api.add_resource(StudentSubmissions, '/student/submissions')
api.add_resource(StudyMaterials, '/materials')
api.add_resource(VirtualLabs, '/labs')
api.add_resource(Discussions, '/discussions')
api.add_resource(StudyGroups, '/groups')
api.add_resource(StudentProjects, '/student/projects')
api.add_resource(StudentNotes, '/student/notes')
api.add_resource(StudentNotifications, '/notifications')
api.add_resource(StudentAnalytics, '/student/analytics')

# Teacher endpoints
api.add_resource(TeacherAssignments, '/teacher/assignments')
api.add_resource(TeacherSubmissions, '/teacher/submissions')
api.add_resource(ClassAnalytics, '/teacher/analytics')

# User management endpoints
api.add_resource(UserProfile, '/user/profile')
api.add_resource(UserRegistration, '/auth/register')
api.add_resource(UserLogin, '/auth/login')

# AI and utility endpoints
api.add_resource(AIRecommendations, '/ai/recommendations')
api.add_resource(FileUpload, '/upload')

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"🚀 EDULEARNAI BACKEND SERVER STARTING")
    print(f"⏰ Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Server will run on: http://0.0.0.0:5003")
    print(f"📝 Debug logs will be saved to: api_debug.log")
    print(f"🔍 All API requests will be logged with detailed information")
    print(f"{'='*60}\n")
    
    logger.info("EduLearnAI Backend Server Started")
    app.run(host="0.0.0.0", port=5003, debug=True)
