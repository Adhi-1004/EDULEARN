"""
Database models and schemas for EduLearn AI system
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.edulearn_ai

# Collections
users_collection = db.users
assignments_collection = db.assignments
submissions_collection = db.submissions
grades_collection = db.grades
study_materials_collection = db.study_materials
virtual_labs_collection = db.virtual_labs
discussions_collection = db.discussions
study_groups_collection = db.study_groups
projects_collection = db.projects
internships_collection = db.internships
notes_collection = db.notes
library_books_collection = db.library_books
certificates_collection = db.certificates
calendar_events_collection = db.calendar_events
notifications_collection = db.notifications
analytics_collection = db.analytics
leaderboard_collection = db.leaderboard

class DatabaseModels:
    """Database model operations"""
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        user_data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        })
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return users_collection.find_one({'email': email})
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            return users_collection.find_one({'_id': ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = users_collection.update_one(
                {'_id': ObjectId(user_id)}, 
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def create_assignment(assignment_data: Dict[str, Any]) -> str:
        """Create a new assignment"""
        assignment_data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'active'
        })
        result = assignments_collection.insert_one(assignment_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_assignments_by_student(student_id: str, section: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get assignments for a student"""
        query = {'$or': [
            {'target_students': student_id},
            {'target_sections': section} if section else {},
            {'is_global': True}
        ]}
        assignments = list(assignments_collection.find(query).sort('due_date', 1))
        for assignment in assignments:
            assignment['id'] = str(assignment['_id'])
        return assignments
    
    @staticmethod
    def get_assignments_by_teacher(teacher_id: str) -> List[Dict[str, Any]]:
        """Get assignments created by a teacher"""
        assignments = list(assignments_collection.find({'teacher_id': teacher_id}).sort('created_at', -1))
        for assignment in assignments:
            assignment['id'] = str(assignment['_id'])
        return assignments
    
    @staticmethod
    def create_submission(submission_data: Dict[str, Any]) -> str:
        """Create a new submission"""
        submission_data.update({
            'submitted_at': datetime.utcnow(),
            'status': 'pending_review',
            'ai_feedback': None,
            'teacher_feedback': None,
            'grade': None
        })
        result = submissions_collection.insert_one(submission_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_submissions_by_assignment(assignment_id: str) -> List[Dict[str, Any]]:
        """Get all submissions for an assignment"""
        submissions = list(submissions_collection.find({'assignment_id': assignment_id}).sort('submitted_at', -1))
        for submission in submissions:
            submission['id'] = str(submission['_id'])
        return submissions
    
    @staticmethod
    def get_submissions_by_student(student_id: str) -> List[Dict[str, Any]]:
        """Get all submissions by a student"""
        submissions = list(submissions_collection.find({'student_id': student_id}).sort('submitted_at', -1))
        for submission in submissions:
            submission['id'] = str(submission['_id'])
        return submissions
    
    @staticmethod
    def create_study_material(material_data: Dict[str, Any]) -> str:
        """Create a new study material"""
        material_data.update({
            'uploaded_at': datetime.utcnow(),
            'views': 0,
            'downloads': 0,
            'is_active': True
        })
        result = study_materials_collection.insert_one(material_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_study_materials(subject: Optional[str] = None, type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get study materials with optional filters"""
        query = {'is_active': True}
        if subject:
            query['subject'] = subject
        if type:
            query['type'] = type
        
        materials = list(study_materials_collection.find(query).sort('uploaded_at', -1))
        for material in materials:
            material['id'] = str(material['_id'])
        return materials
    
    @staticmethod
    def create_virtual_lab(lab_data: Dict[str, Any]) -> str:
        """Create a new virtual lab"""
        lab_data.update({
            'created_at': datetime.utcnow(),
            'is_active': True,
            'completion_count': 0
        })
        result = virtual_labs_collection.insert_one(lab_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_virtual_labs(subject: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get virtual labs with optional subject filter"""
        query = {'is_active': True}
        if subject:
            query['subject'] = subject
        
        labs = list(virtual_labs_collection.find(query).sort('created_at', -1))
        for lab in labs:
            lab['id'] = str(lab['_id'])
        return labs
    
    @staticmethod
    def create_discussion(discussion_data: Dict[str, Any]) -> str:
        """Create a new discussion"""
        discussion_data.update({
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'participants': [discussion_data['author_id']],
            'posts_count': 1,
            'is_active': True
        })
        result = discussions_collection.insert_one(discussion_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_discussions(subject: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get discussions with optional subject filter"""
        query = {'is_active': True}
        if subject:
            query['subject'] = subject
        
        discussions = list(discussions_collection.find(query).sort('last_activity', -1))
        for discussion in discussions:
            discussion['id'] = str(discussion['_id'])
        return discussions
    
    @staticmethod
    def create_study_group(group_data: Dict[str, Any]) -> str:
        """Create a new study group"""
        group_data.update({
            'created_at': datetime.utcnow(),
            'members': [group_data['creator_id']],
            'member_count': 1,
            'is_active': True
        })
        result = study_groups_collection.insert_one(group_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_study_groups(subject: Optional[str] = None, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get study groups with optional filters"""
        query = {'is_active': True}
        if subject:
            query['subject'] = subject
        if student_id:
            query['members'] = student_id
        
        groups = list(study_groups_collection.find(query).sort('created_at', -1))
        for group in groups:
            group['id'] = str(group['_id'])
        return groups
    
    @staticmethod
    def create_project(project_data: Dict[str, Any]) -> str:
        """Create a new project"""
        project_data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'progress': 0,
            'status': 'not_started'
        })
        result = projects_collection.insert_one(project_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_projects_by_student(student_id: str) -> List[Dict[str, Any]]:
        """Get projects for a student"""
        projects = list(projects_collection.find({'student_id': student_id}).sort('created_at', -1))
        for project in projects:
            project['id'] = str(project['_id'])
        return projects
    
    @staticmethod
    def create_note(note_data: Dict[str, Any]) -> str:
        """Create a new note"""
        note_data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        })
        result = notes_collection.insert_one(note_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_notes_by_student(student_id: str, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get notes for a student"""
        query = {'student_id': student_id, 'is_active': True}
        if subject:
            query['subject'] = subject
        
        notes = list(notes_collection.find(query).sort('updated_at', -1))
        for note in notes:
            note['id'] = str(note['_id'])
        return notes
    
    @staticmethod
    def create_notification(notification_data: Dict[str, Any]) -> str:
        """Create a new notification"""
        notification_data.update({
            'created_at': datetime.utcnow(),
            'read': False,
            'is_active': True
        })
        result = notifications_collection.insert_one(notification_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_notifications_by_user(user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        query = {'user_id': user_id, 'is_active': True}
        if unread_only:
            query['read'] = False
        
        notifications = list(notifications_collection.find(query).sort('created_at', -1).limit(20))
        for notification in notifications:
            notification['id'] = str(notification['_id'])
        return notifications
    
    @staticmethod
    def mark_notification_read(notification_id: str) -> bool:
        """Mark notification as read"""
        try:
            result = notifications_collection.update_one(
                {'_id': ObjectId(notification_id)},
                {'$set': {'read': True}}
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def get_student_analytics(student_id: str) -> Dict[str, Any]:
        """Get analytics for a student"""
        # Calculate various metrics
        submissions = list(submissions_collection.find({'student_id': student_id}))
        grades = list(grades_collection.find({'student_id': student_id}))
        
        total_submissions = len(submissions)
        graded_submissions = len([s for s in submissions if s.get('grade') is not None])
        average_grade = sum([g['grade'] for g in grades]) / len(grades) if grades else 0
        
        # Performance over time
        monthly_performance = {}
        for grade in grades[-12:]:  # Last 12 grades
            month = grade['date'].strftime('%Y-%m') if isinstance(grade.get('date'), datetime) else 'unknown'
            if month not in monthly_performance:
                monthly_performance[month] = []
            monthly_performance[month].append(grade['grade'])
        
        # Average monthly performance
        monthly_avg = {month: sum(scores)/len(scores) for month, scores in monthly_performance.items()}
        
        return {
            'total_submissions': total_submissions,
            'graded_submissions': graded_submissions,
            'average_grade': round(average_grade, 2),
            'completion_rate': round((graded_submissions / total_submissions * 100) if total_submissions > 0 else 0, 2),
            'monthly_performance': monthly_avg,
            'strengths': [],  # TODO: Implement AI-based analysis
            'weak_areas': [],  # TODO: Implement AI-based analysis
            'recommendations': []  # TODO: Implement AI-based recommendations
        }
    
    @staticmethod
    def get_class_analytics(teacher_id: str, section: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for a class"""
        # Get students in the class
        query = {'role': 'student'}
        if section:
            query['section'] = section
        
        students = list(users_collection.find(query))
        student_ids = [str(s['_id']) for s in students]
        
        # Get submissions and grades for these students
        submissions = list(submissions_collection.find({'student_id': {'$in': student_ids}}))
        grades = list(grades_collection.find({'student_id': {'$in': student_ids}}))
        
        total_students = len(students)
        active_students = len([s for s in students if s.get('last_login') and 
                             (datetime.utcnow() - s['last_login']).days <= 7])
        
        # Grade distribution
        grade_ranges = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for grade in grades:
            score = grade.get('grade', 0)
            if score >= 90:
                grade_ranges['A'] += 1
            elif score >= 80:
                grade_ranges['B'] += 1
            elif score >= 70:
                grade_ranges['C'] += 1
            elif score >= 60:
                grade_ranges['D'] += 1
            else:
                grade_ranges['F'] += 1
        
        average_grade = sum([g['grade'] for g in grades]) / len(grades) if grades else 0
        completion_rate = len([s for s in submissions if s.get('grade') is not None]) / len(submissions) * 100 if submissions else 0
        
        return {
            'total_students': total_students,
            'active_students': active_students,
            'average_grade': round(average_grade, 2),
            'completion_rate': round(completion_rate, 2),
            'grade_distribution': grade_ranges,
            'total_assignments': len(set([s['assignment_id'] for s in submissions])),
            'pending_reviews': len([s for s in submissions if s.get('status') == 'pending_review'])
        }

# Initialize indexes for better performance
def create_indexes():
    """Create database indexes for better performance"""
    # User indexes
    users_collection.create_index('email', unique=True)
    users_collection.create_index('role')
    users_collection.create_index('section')
    
    # Assignment indexes
    assignments_collection.create_index('teacher_id')
    assignments_collection.create_index('due_date')
    assignments_collection.create_index('target_sections')
    
    # Submission indexes
    submissions_collection.create_index('student_id')
    submissions_collection.create_index('assignment_id')
    submissions_collection.create_index('submitted_at')
    
    # Grade indexes
    grades_collection.create_index('student_id')
    grades_collection.create_index('assignment_id')
    grades_collection.create_index('date')
    
    # Notification indexes
    notifications_collection.create_index('user_id')
    notifications_collection.create_index('read')
    notifications_collection.create_index('created_at')
    
    # Leaderboard indexes
    leaderboard_collection.create_index('user_id')
    leaderboard_collection.create_index('subject')
    leaderboard_collection.create_index('difficulty')
    leaderboard_collection.create_index('score')

# Create indexes on import
try:
    create_indexes()
except Exception as e:
    print(f"Index creation warning: {e}")
