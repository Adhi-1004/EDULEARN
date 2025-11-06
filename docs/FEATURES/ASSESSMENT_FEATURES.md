# 📝 Assessment System Features

## Table of Contents
1. [Overview](#overview)
2. [Assessment Creation (Teacher)](#assessment-creation-teacher)
3. [Manual Question Addition](#manual-question-addition)
4. [AI-Generated Assessments](#ai-generated-assessments)
5. [Coding Assessments](#coding-assessments)
6. [Assessment Publishing & Assignment](#assessment-publishing--assignment)
7. [Student Assessment Taking](#student-assessment-taking)
8. [Assessment Submission & Grading](#assessment-submission--grading)
9. [Results & Leaderboards](#results--leaderboards)
10. [Topic Configuration](#topic-configuration)

---

## Overview

The EDULEARN Assessment System is a comprehensive platform for creating, managing, and evaluating student knowledge through multiple assessment types.

### Assessment Types

```
┌─────────────────────────────────────────────────────────┐
│                  ASSESSMENT TYPES                       │
└─────────────────────────────────────────────────────────┘

1. MANUAL ASSESSMENTS
   - Teacher creates questions manually
   - Full control over content
   - Custom difficulty levels
   
2. AI-GENERATED ASSESSMENTS
   - Powered by Google Gemini AI
   - Automatic question generation
   - Topic-based customization
   - Configurable difficulty and count
   
3. CODING ASSESSMENTS
   - Algorithm and problem-solving
   - Multiple programming languages
   - Automated test case evaluation
   - Judge0 API integration
```

### Key Features

- ✅ Multiple question types (MCQ, Coding)
- 🤖 AI-powered question generation
- ⏱️ Time-limited assessments
- 🎯 Difficulty levels (Easy, Medium, Hard)
- 📊 Real-time grading
- 🏆 Leaderboards
- 🔄 Multiple attempts support
- 📧 Automated notifications
- 🎨 Batch assignment
- 📈 Performance analytics

---

## Assessment Creation (Teacher)

### Feature Overview
Teachers can create assessments with various configurations, either manually adding questions or using AI generation.

### 1. Create Assessment Flow

#### Process Diagram
```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Teacher    │       │   Frontend   │       │   Backend    │       │   Database   │
│   Dashboard  │       │   Component  │       │   API        │       │   MongoDB    │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │                      │
       │ 1. Click "Create    │                      │                      │
       │    Assessment"       │                      │                      │
       ├─────────────────────▶│                      │                      │
       │                      │                      │                      │
       │ 2. Fill Form:        │                      │                      │
       │    - Title           │                      │                      │
       │    - Subject         │                      │                      │
       │    - Difficulty      │                      │                      │
       │    - Time Limit      │                      │                      │
       │    - Max Attempts    │                      │                      │
       │    - Type (manual/AI)│                      │                      │
       │    - Description     │                      │                      │
       │                      │                      │                      │
       │ 3. Submit Form       │                      │                      │
       ├─────────────────────▶│                      │                      │
       │                      │                      │                      │
       │                      │ 4. POST /assessments/│                      │
       │                      │    {assessment_data} │                      │
       │                      ├─────────────────────▶│                      │
       │                      │                      │                      │
       │                      │                      │ 5. Validate JWT     │
       │                      │                      │    (require_teacher)│
       │                      │                      ├──────┐              │
       │                      │                      │      │              │
       │                      │                      │◀─────┘              │
       │                      │                      │                      │
       │                      │                      │ 6. Create Assessment│
       │                      │                      │    Document         │
       │                      │                      │    {title, subject, │
       │                      │                      │     difficulty,     │
       │                      │                      │     created_by,     │
       │                      │                      │     status: draft}  │
       │                      │                      │                      │
       │                      │                      │ 7. Insert into DB   │
       │                      │                      ├─────────────────────▶│
       │                      │                      │                      │
       │                      │                      │ 8. Assessment ID     │
       │                      │                      │◀─────────────────────┤
       │                      │                      │                      │
       │                      │ 9. If type="ai":     │                      │
       │                      │    Generate Questions│                      │
       │                      │    (Gemini AI)       │                      │
       │                      │    [See AI Generation│                      │
       │                      │     section]          │                      │
       │                      │                      │                      │
       │                      │ 10. Response         │                      │
       │                      │     {assessment_id}  │                      │
       │                      │◀─────────────────────┤                      │
       │                      │                      │                      │
       │ 11. Redirect to      │                      │                      │
       │     Edit/Add Questions│                     │                      │
       │◀─────────────────────┤                      │                      │
       │                      │                      │                      │
       ▼                      ▼                      ▼                      ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/teacher/CreateAssessment.tsx` - Assessment creation form
- `frontend/src/api/assessmentService.ts` - Assessment API service
  - Function: `createAssessment(data: AssessmentCreate)`
- `frontend/src/components/AssessmentForm.tsx` - Reusable form component

**Backend:**
- `backend/app/api/assessments/core.py` - Core assessment operations
  - Endpoint: `POST /api/assessments/`
  - Function: `create_assessment(assessment_data, user)`
- `backend/app/schemas/schemas.py` - Pydantic models
  - Model: `AssessmentCreate`
  - Model: `AssessmentResponse`
- `backend/app/dependencies.py` - Authentication dependencies
  - Function: `require_teacher()`

**Database:**
- Collection: `assessments`

#### Request/Response Flow

**1. Frontend Assessment Creation**
```typescript
// File: frontend/src/api/assessmentService.ts
export const createAssessment = async (assessmentData: AssessmentCreate) => {
  const response = await api.post('/assessments/', assessmentData);
  return response.data;
};

// File: frontend/src/pages/teacher/CreateAssessment.tsx
const CreateAssessment: React.FC = () => {
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    difficulty: 'medium',
    description: '',
    time_limit: 60,
    max_attempts: 1,
    type: 'manual',
    batches: []
  });
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const assessment = await assessmentService.createAssessment(formData);
      toast.success('Assessment created successfully!');
      
      // Redirect to edit page to add questions
      navigate(`/teacher/assessment/${assessment.id}/edit`);
    } catch (error) {
      toast.error('Failed to create assessment');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Assessment Title"
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
      />
      
      <select
        value={formData.difficulty}
        onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
      >
        <option value="easy">Easy</option>
        <option value="medium">Medium</option>
        <option value="hard">Hard</option>
      </select>
      
      <input
        type="number"
        placeholder="Time Limit (minutes)"
        value={formData.time_limit}
        onChange={(e) => setFormData({...formData, time_limit: +e.target.value})}
      />
      
      <select
        value={formData.type}
        onChange={(e) => setFormData({...formData, type: e.target.value})}
      >
        <option value="manual">Manual Questions</option>
        <option value="ai">AI-Generated</option>
        <option value="coding">Coding Assessment</option>
      </select>
      
      <button type="submit">Create Assessment</button>
    </form>
  );
};
```

**2. Backend Assessment Creation**
```python
# File: backend/app/api/assessments/core.py
from fastapi import APIRouter, Depends, HTTPException
from ...dependencies import require_teacher
from ...schemas.schemas import AssessmentCreate, AssessmentResponse

router = APIRouter(prefix="/assessments", tags=["assessments"])

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment_data: AssessmentCreate,
    user: UserModel = Depends(require_teacher)
):
    """Create a new assessment - Teacher/Admin only"""
    try:
        db = await get_db()
        
        # Create assessment document
        assessment_doc = {
            "title": assessment_data.title,
            "subject": assessment_data.subject,
            "difficulty": assessment_data.difficulty,
            "description": assessment_data.description,
            "time_limit": assessment_data.time_limit,  # in minutes
            "max_attempts": assessment_data.max_attempts,
            "type": assessment_data.type,  # manual, ai, or coding
            "created_by": str(user.id),
            "created_at": datetime.utcnow(),
            "status": "draft",  # draft, active, published, archived
            "question_count": 0,
            "questions": [],
            "assigned_batches": assessment_data.batches or [],
            "is_active": False
        }
        
        # Insert into database
        result = await db.assessments.insert_one(assessment_doc)
        assessment_id = str(result.inserted_id)
        
        # If AI-generated, trigger question generation
        if assessment_data.type == "ai":
            await generate_ai_questions(
                db,
                assessment_id,
                assessment_data.subject,
                assessment_data.difficulty,
                10  # default count
            )
        
        return AssessmentResponse(
            id=assessment_id,
            title=assessment_data.title,
            subject=assessment_data.subject,
            difficulty=assessment_data.difficulty,
            description=assessment_data.description,
            time_limit=assessment_data.time_limit,
            max_attempts=assessment_data.max_attempts,
            question_count=0,
            created_by=str(user.id),
            created_at=assessment_doc["created_at"].isoformat(),
            status="draft",
            type=assessment_data.type,
            is_active=False,
            total_questions=0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Request Body:**
```json
{
  "title": "Python Basics Assessment",
  "subject": "Python Programming",
  "difficulty": "medium",
  "description": "Test your knowledge of Python fundamentals",
  "time_limit": 45,
  "max_attempts": 2,
  "type": "manual",
  "batches": ["batch-id-1", "batch-id-2"]
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Python Basics Assessment",
  "subject": "Python Programming",
  "difficulty": "medium",
  "description": "Test your knowledge of Python fundamentals",
  "time_limit": 45,
  "max_attempts": 2,
  "question_count": 0,
  "created_by": "teacher-id-123",
  "created_at": "2025-10-26T10:30:00Z",
  "status": "draft",
  "type": "manual",
  "is_active": false,
  "total_questions": 0
}
```

**Database Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "title": "Python Basics Assessment",
  "subject": "Python Programming",
  "difficulty": "medium",
  "description": "Test your knowledge of Python fundamentals",
  "time_limit": 45,
  "max_attempts": 2,
  "type": "manual",
  "created_by": "teacher-id-123",
  "created_at": ISODate("2025-10-26T10:30:00Z"),
  "status": "draft",
  "question_count": 0,
  "questions": [],
  "assigned_batches": ["batch-id-1", "batch-id-2"],
  "is_active": false
}
```

---

## Manual Question Addition

### Feature Overview
Teachers can manually add MCQ questions to assessments with multiple options and correct answers.

### Add Question Flow

#### Process Diagram
```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Teacher    │       │   Frontend   │       │   Backend    │       │   Database   │
│   (Edit      │       │   Component  │       │   API        │       │   MongoDB    │
│   Assessment)│       │              │       │              │       │              │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │                      │
       │ 1. View Assessment   │                      │                      │
       │    Edit Page         │                      │                      │
       │                      │                      │                      │
       │ 2. Click "Add        │                      │                      │
       │    Question"         │                      │                      │
       ├─────────────────────▶│                      │                      │
       │                      │                      │                      │
       │ 3. Fill Question     │                      │                      │
       │    Form:             │                      │                      │
       │    - Question text   │                      │                      │
       │    - Option 1-4      │                      │                      │
       │    - Correct answer  │                      │                      │
       │    - Explanation     │                      │                      │
       │    - Points          │                      │                      │
       │                      │                      │                      │
       │ 4. Submit Question   │                      │                      │
       ├─────────────────────▶│                      │                      │
       │                      │                      │                      │
       │                      │ 5. POST /assessments/│                      │
       │                      │    {id}/questions    │                      │
       │                      │    {question_data}   │                      │
       │                      ├─────────────────────▶│                      │
       │                      │                      │                      │
       │                      │                      │ 6. Validate Teacher │
       │                      │                      │    Authorization    │
       │                      │                      ├──────┐              │
       │                      │                      │      │              │
       │                      │                      │◀─────┘              │
       │                      │                      │                      │
       │                      │                      │ 7. Validate Question│
       │                      │                      │    Data (4 options, │
       │                      │                      │    valid answer idx)│
       │                      │                      │                      │
       │                      │                      │ 8. Get Assessment   │
       │                      │                      ├─────────────────────▶│
       │                      │                      │                      │
       │                      │                      │ 9. Assessment Doc    │
       │                      │                      │◀─────────────────────┤
       │                      │                      │                      │
       │                      │                      │ 10. Add Question to  │
       │                      │                      │     Questions Array  │
       │                      │                      │     Update count     │
       │                      │                      ├─────────────────────▶│
       │                      │                      │                      │
       │                      │                      │ 11. Update Result    │
       │                      │                      │◀─────────────────────┤
       │                      │                      │                      │
       │                      │ 12. Response         │                      │
       │                      │     {question_added} │                      │
       │                      │◀─────────────────────┤                      │
       │                      │                      │                      │
       │ 13. Update UI        │                      │                      │
       │     Show Question in │                      │                      │
       │     List             │                      │                      │
       │◀─────────────────────┤                      │                      │
       │                      │                      │                      │
       ▼                      ▼                      ▼                      ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/teacher/EditAssessment.tsx` - Assessment editing page
- `frontend/src/components/QuestionBuilder.tsx` - Question form component
- `frontend/src/api/assessmentService.ts`
  - Function: `addQuestion(assessmentId, questionData)`

**Backend:**
- `backend/app/api/assessments/core.py`
  - Endpoint: `POST /api/assessments/{assessment_id}/questions`
  - Function: `add_question(assessment_id, question_data, user)`

#### Implementation

**1. Frontend Question Builder**
```typescript
// File: frontend/src/components/QuestionBuilder.tsx
interface QuestionBuilderProps {
  assessmentId: string;
  onQuestionAdded: () => void;
}

const QuestionBuilder: React.FC<QuestionBuilderProps> = ({
  assessmentId,
  onQuestionAdded
}) => {
  const [questionData, setQuestionData] = useState({
    question: '',
    options: ['', '', '', ''],
    correct_answer: 0,
    explanation: '',
    points: 10
  });
  
  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...questionData.options];
    newOptions[index] = value;
    setQuestionData({...questionData, options: newOptions});
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all options are filled
    if (questionData.options.some(opt => !opt.trim())) {
      toast.error('All options must be filled');
      return;
    }
    
    try {
      await assessmentService.addQuestion(assessmentId, questionData);
      toast.success('Question added successfully!');
      
      // Reset form
      setQuestionData({
        question: '',
        options: ['', '', '', ''],
        correct_answer: 0,
        explanation: '',
        points: 10
      });
      
      onQuestionAdded();
    } catch (error) {
      toast.error('Failed to add question');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="question-builder">
      <h3>Add Question</h3>
      
      <textarea
        placeholder="Enter your question..."
        value={questionData.question}
        onChange={(e) => setQuestionData({...questionData, question: e.target.value})}
        required
      />
      
      <div className="options">
        {questionData.options.map((option, index) => (
          <div key={index} className="option-input">
            <input
              type="radio"
              name="correct_answer"
              checked={questionData.correct_answer === index}
              onChange={() => setQuestionData({...questionData, correct_answer: index})}
            />
            <input
              type="text"
              placeholder={`Option ${index + 1}`}
              value={option}
              onChange={(e) => handleOptionChange(index, e.target.value)}
              required
            />
          </div>
        ))}
      </div>
      
      <textarea
        placeholder="Explanation (optional)"
        value={questionData.explanation}
        onChange={(e) => setQuestionData({...questionData, explanation: e.target.value})}
      />
      
      <input
        type="number"
        placeholder="Points"
        value={questionData.points}
        onChange={(e) => setQuestionData({...questionData, points: +e.target.value})}
        min="1"
      />
      
      <button type="submit">Add Question</button>
    </form>
  );
};
```

**2. Backend Question Addition**
```python
# File: backend/app/api/assessments/core.py
@router.post("/{assessment_id}/questions")
async def add_question(
    assessment_id: str,
    question_data: QuestionCreate,
    user: UserModel = Depends(require_teacher)
):
    """Add a question to an assessment"""
    try:
        db = await get_db()
        
        # Validate assessment exists and belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id),
            "created_by": str(user.id)
        })
        
        if not assessment:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found or unauthorized"
            )
        
        # Validate question data
        if len(question_data.options) < 2:
            raise HTTPException(
                status_code=400,
                detail="Question must have at least 2 options"
            )
        
        if question_data.correct_answer >= len(question_data.options):
            raise HTTPException(
                status_code=400,
                detail="Invalid correct answer index"
            )
        
        # Create question document
        question_doc = {
            "id": str(uuid4()),
            "question": question_data.question,
            "options": question_data.options,
            "correct_answer": question_data.correct_answer,
            "explanation": question_data.explanation or "",
            "points": question_data.points or 10,
            "created_at": datetime.utcnow()
        }
        
        # Add question to assessment
        result = await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {
                "$push": {"questions": question_doc},
                "$inc": {"question_count": 1}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to add question"
            )
        
        return {
            "message": "Question added successfully",
            "question_id": question_doc["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Request Body:**
```json
{
  "question": "What is the correct way to create a list in Python?",
  "options": [
    "list = []",
    "list = {}",
    "list = ()",
    "list = <>"
  ],
  "correct_answer": 0,
  "explanation": "Square brackets [] are used to create lists in Python. {} creates a dictionary, () creates a tuple.",
  "points": 10
}
```

**Response:**
```json
{
  "message": "Question added successfully",
  "question_id": "q-550e8400-e29b-41d4-a716-446655440000"
}
```

---

## AI-Generated Assessments

### Feature Overview
Leverages Google Gemini AI to automatically generate high-quality MCQ questions based on topic, difficulty, and count specifications.

### AI Generation Flow

#### Process Diagram
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Teacher    │    │   Frontend   │    │   Backend    │    │ Gemini AI API│    │   Database   │
│              │    │              │    │              │    │              │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │                   │
       │ 1. Set Topic      │                   │                   │                   │
       │    Config         │                   │                   │                   │
       ├──────────────────▶│                   │                   │                   │
       │                   │                   │                   │                   │
       │ 2. POST /topic    │                   │                   │                   │
       │    {topic,        │                   │                   │                   │
       │     count,        │                   │                   │                   │
       │     difficulty}   │                   │                   │                   │
       │                   ├──────────────────▶│                   │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 3. Store Config   │                   │
       │                   │                   ├──────────────────────────────────────▶│
       │                   │                   │                   │                   │
       │ 4. Create AI      │                   │                   │                   │
       │    Assessment     │                   │                   │                   │
       ├──────────────────▶│                   │                   │                   │
       │                   │                   │                   │                   │
       │                   │ 5. POST /assessments/                 │                   │
       │                   │    {type: "ai"}   │                   │                   │
       │                   ├──────────────────▶│                   │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 6. Create Draft   │                   │
       │                   │                   │    Assessment     │                   │
       │                   │                   ├──────────────────────────────────────▶│
       │                   │                   │                   │                   │
       │                   │                   │ 7. Get Topic Config                   │
       │                   │                   ├──────────────────────────────────────▶│
       │                   │                   │                   │                   │
       │                   │                   │ 8. Config Data    │                   │
       │                   │                   │◀──────────────────────────────────────┤
       │                   │                   │                   │                   │
       │                   │                   │ 9. Prepare Prompt │                   │
       │                   │                   │    for Gemini     │                   │
       │                   │                   ├──────┐            │                   │
       │                   │                   │      │            │                   │
       │                   │                   │◀─────┘            │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 10. Request Questions                 │
       │                   │                   ├──────────────────▶│                   │
       │                   │                   │                   │                   │
       │                   │                   │                   │ 11. Generate      │
       │                   │                   │                   │     Questions     │
       │                   │                   │                   │     (Gemini AI)   │
       │                   │                   │                   ├──────┐            │
       │                   │                   │                   │      │            │
       │                   │                   │                   │◀─────┘            │
       │                   │                   │                   │                   │
       │                   │                   │ 12. Generated Questions               │
       │                   │                   │     [{q, options, ans}...]            │
       │                   │                   │◀──────────────────┤                   │
       │                   │                   │                   │                   │
       │                   │                   │ 13. Parse & Validate                  │
       │                   │                   │     Questions     │                   │
       │                   │                   ├──────┐            │                   │
       │                   │                   │      │            │                   │
       │                   │                   │◀─────┘            │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 14. Update Assessment                 │
       │                   │                   │     with Questions│                   │
       │                   │                   │     Set status:   │                   │
       │                   │                   │     "published"   │                   │
       │                   │                   ├──────────────────────────────────────▶│
       │                   │                   │                   │                   │
       │                   │                   │ 15. Send Notifications                │
       │                   │                   │     to Students   │                   │
       │                   │                   ├──────────────────────────────────────▶│
       │                   │                   │                   │                   │
       │                   │ 16. Response      │                   │                   │
       │                   │     {assessment_id,                   │                   │
       │                   │      questions}    │                   │                   │
       │                   │◀──────────────────┤                   │                   │
       │                   │                   │                   │                   │
       │ 17. Show Success  │                   │                   │                   │
       │     "Assessment   │                   │                   │                   │
       │     Published!"   │                   │                   │                   │
       │◀──────────────────┤                   │                   │                   │
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/teacher/TopicSelection.tsx` - Topic configuration
- `frontend/src/api/assessmentService.ts`
  - Function: `setAssessmentConfig(config)`
  - Function: `generateAIQuestions(assessmentId, config)`

**Backend:**
- `backend/app/api/topics.py` - Topic configuration endpoints
  - Endpoint: `POST /api/topic`
- `backend/app/api/assessments/core.py` - Assessment creation with AI
- `backend/app/services/gemini_coding_service.py` - Gemini AI integration
  - Function: `generate_mcq_questions(topic, difficulty, count)`
- `backend/app/config.py` - Gemini API key configuration

#### Implementation

**1. Topic Configuration**
```typescript
// File: frontend/src/pages/teacher/TopicSelection.tsx
const TopicSelection: React.FC = () => {
  const [config, setConfig] = useState({
    topic: '',
    qnCount: 10,
    difficulty: 'medium'
  });
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await assessmentService.setAssessmentConfig(config);
      toast.success('Topic configuration saved!');
      navigate('/teacher/create-assessment?type=ai');
    } catch (error) {
      toast.error('Failed to save configuration');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter topic (e.g., Python Basics)"
        value={config.topic}
        onChange={(e) => setConfig({...config, topic: e.target.value})}
        required
      />
      
      <input
        type="number"
        min="5"
        max="50"
        value={config.qnCount}
        onChange={(e) => setConfig({...config, qnCount: +e.target.value})}
      />
      
      <select
        value={config.difficulty}
        onChange={(e) => setConfig({...config, difficulty: e.target.value})}
      >
        <option value="easy">Easy</option>
        <option value="medium">Medium</option>
        <option value="hard">Hard</option>
      </select>
      
      <button type="submit">Generate Assessment</button>
    </form>
  );
};
```

**2. Backend AI Question Generation**
```python
# File: backend/app/services/gemini_coding_service.py
import google.generativeai as genai
import json

class GeminiCodingService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_mcq_questions(
        self,
        topic: str,
        difficulty: str,
        count: int = 10
    ) -> List[Dict]:
        """Generate MCQ questions using Gemini AI"""
        
        # Construct prompt
        prompt = f"""
        Generate {count} multiple-choice questions about {topic}.
        Difficulty level: {difficulty}
        
        Requirements:
        - Each question should have exactly 4 options
        - Only one option should be correct
        - Include a brief explanation for each answer
        - Questions should be practical and test understanding
        - Vary question types (conceptual, application, analysis)
        
        Return the response in the following JSON format:
        {{
          "questions": [
            {{
              "question": "Question text here?",
              "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
              "correct_answer": 0,
              "explanation": "Explanation of why this is correct"
            }}
          ]
        }}
        
        Ensure the JSON is valid and parseable.
        """
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Parse response
            response_text = response.text
            
            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            data = json.loads(response_text)
            questions = data.get("questions", [])
            
            # Validate and format questions
            formatted_questions = []
            for q in questions:
                if all(key in q for key in ["question", "options", "correct_answer"]):
                    formatted_questions.append({
                        "id": str(uuid4()),
                        "question": q["question"],
                        "options": q["options"],
                        "correct_answer": q["correct_answer"],
                        "explanation": q.get("explanation", ""),
                        "points": 10,
                        "created_at": datetime.utcnow()
                    })
            
            return formatted_questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate questions: {str(e)}"
            )
```

**3. Assessment Creation with AI**
```python
# File: backend/app/api/assessments/core.py
@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment_data: AssessmentCreate,
    user: UserModel = Depends(require_teacher)
):
    """Create assessment with AI generation if type is 'ai'"""
    db = await get_db()
    
    # Create base assessment
    assessment_doc = {
        "title": assessment_data.title,
        "subject": assessment_data.subject,
        "difficulty": assessment_data.difficulty,
        "created_by": str(user.id),
        "created_at": datetime.utcnow(),
        "status": "draft",
        "type": assessment_data.type,
        "questions": [],
        "question_count": 0,
        "assigned_batches": assessment_data.batches or [],
        "is_active": False
    }
    
    result = await db.assessments.insert_one(assessment_doc)
    assessment_id = str(result.inserted_id)
    
    # Generate questions if AI type
    if assessment_data.type == "ai":
        # Get topic configuration
        topic_config = await db.topic_configs.find_one({
            "user_id": str(user.id)
        })
        
        if not topic_config:
            # Use defaults
            topic = assessment_data.subject
            count = 10
            difficulty = assessment_data.difficulty
        else:
            topic = topic_config.get("topic", assessment_data.subject)
            count = topic_config.get("qnCount", 10)
            difficulty = topic_config.get("difficulty", assessment_data.difficulty)
        
        # Generate questions
        gemini_service = GeminiCodingService()
        questions = await gemini_service.generate_mcq_questions(
            topic=topic,
            difficulty=difficulty,
            count=count
        )
        
        # Update assessment with generated questions
        await db.assessments.update_one(
            {"_id": result.inserted_id},
            {
                "$set": {
                    "questions": questions,
                    "question_count": len(questions),
                    "is_active": True,
                    "status": "published"
                }
            }
        )
        
        # Send notifications to students in assigned batches
        await send_assessment_notifications(
            db,
            assessment_id,
            assessment_data.batches,
            assessment_data.title
        )
    
    return AssessmentResponse(...)
```

**AI-Generated Question Example:**
```json
{
  "question": "Which of the following is the correct way to define a function in Python?",
  "options": [
    "def myFunction():",
    "function myFunction():",
    "func myFunction():",
    "define myFunction():"
  ],
  "correct_answer": 0,
  "explanation": "In Python, functions are defined using the 'def' keyword followed by the function name and parentheses with a colon at the end."
}
```

---

## Coding Assessments

### Feature Overview
Create programming challenges with automated test case evaluation using Judge0 API.

### Coding Assessment Flow

#### Process Diagram
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Teacher    │    │   Frontend   │    │   Backend    │    │   Database   │
│              │    │              │    │              │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       │ 1. Create Coding  │                   │                   │
       │    Assessment     │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │ 2. Fill Form:     │                   │                   │
       │    - Problem Title│                   │                   │
       │    - Description  │                   │                   │
       │    - Constraints  │                   │                   │
       │    - Examples     │                   │                   │
       │    - Test Cases   │                   │                   │
       │    - Hidden Tests │                   │                   │
       │                   │                   │                   │
       │ 3. Submit         │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ 4. POST /assessments/                 │
       │                   │    {id}/coding-   │                   │
       │                   │    questions      │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 5. Validate       │
       │                   │                   │    Test Cases     │
       │                   │                   ├──────┐            │
       │                   │                   │      │            │
       │                   │                   │◀─────┘            │
       │                   │                   │                   │
       │                   │                   │ 6. Store Question │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │ 7. Response       │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 8. Confirmation   │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/teacher/CreateCodingAssessment.tsx`
- `frontend/src/components/CodingQuestionBuilder.tsx`
- `frontend/src/api/assessmentService.ts`
  - Function: `addCodingQuestion(assessmentId, questionData)`

**Backend:**
- `backend/app/api/assessments/core.py`
  - Endpoint: `POST /api/assessments/{id}/coding-questions`
- `backend/app/schemas/schemas.py`
  - Model: `CodingQuestionCreate`

#### Coding Question Structure

```typescript
interface CodingQuestion {
  title: string;
  description: string;
  problem_statement: string;
  constraints: string[];
  examples: Array<{
    input: string;
    output: string;
    explanation?: string;
  }>;
  test_cases: Array<{
    input: string;
    expected_output: string;
  }>;
  hidden_test_cases: Array<{
    input: string;
    expected_output: string;
  }>;
  expected_complexity: {
    time: string;  // e.g., "O(n)"
    space: string;  // e.g., "O(1)"
  };
  hints: string[];
  points: number;
  time_limit: number;  // seconds
  memory_limit: number;  // MB
}
```

---

## Assessment Publishing & Assignment

### Feature Overview
Teachers publish assessments and assign them to specific batches of students.

### Publishing Flow

#### Process Diagram
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Teacher    │    │   Frontend   │    │   Backend    │    │   Database   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       │ 1. Review Draft   │                   │                   │
       │    Assessment     │                   │                   │
       │                   │                   │                   │
       │ 2. Click "Publish"│                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ 3. POST /assessments/                 │
       │                   │    {id}/publish   │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 4. Validate:      │
       │                   │                   │    - Has questions│
       │                   │                   │    - Teacher owns │
       │                   │                   ├──────┐            │
       │                   │                   │      │            │
       │                   │                   │◀─────┘            │
       │                   │                   │                   │
       │                   │                   │ 5. Update Status  │
       │                   │                   │    status:        │
       │                   │                   │    "published"    │
       │                   │                   │    is_active: true│
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 6. Get Students   │
       │                   │                   │    in Batches     │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 7. Student List   │
       │                   │                   │◀──────────────────┤
       │                   │                   │                   │
       │                   │                   │ 8. Create         │
       │                   │                   │    Notifications  │
       │                   │                   │    for Each       │
       │                   │                   │    Student        │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │ 9. Response       │                   │
       │                   │    {published}    │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 10. Show Success  │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
```

#### Implementation

```python
# File: backend/app/api/assessments/core.py
@router.post("/{assessment_id}/publish")
async def publish_assessment(
    assessment_id: str,
    user: UserModel = Depends(require_teacher)
):
    """Publish an assessment to make it available to students"""
    db = await get_db()
    
    # Get assessment
    assessment = await db.assessments.find_one({
        "_id": ObjectId(assessment_id),
        "created_by": str(user.id)
    })
    
    if not assessment:
        raise HTTPException(404, "Assessment not found")
    
    # Validate has questions
    if assessment.get("question_count", 0) == 0:
        raise HTTPException(
            400,
            "Cannot publish assessment without questions"
        )
    
    # Update status
    await db.assessments.update_one(
        {"_id": ObjectId(assessment_id)},
        {
            "$set": {
                "status": "published",
                "is_active": True,
                "published_at": datetime.utcnow()
            }
        }
    )
    
    # Send notifications
    await send_assessment_notifications(
        db,
        assessment_id,
        assessment.get("assigned_batches", []),
        assessment["title"]
    )
    
    return {"message": "Assessment published successfully"}

@router.post("/{assessment_id}/assign-batches")
async def assign_to_batches(
    assessment_id: str,
    batch_ids: List[str],
    user: UserModel = Depends(require_teacher)
):
    """Assign assessment to specific batches"""
    db = await get_db()
    
    # Validate assessment
    assessment = await db.assessments.find_one({
        "_id": ObjectId(assessment_id),
        "created_by": str(user.id)
    })
    
    if not assessment:
        raise HTTPException(404, "Assessment not found")
    
    # Validate batches belong to teacher
    batches = await db.batches.find({
        "_id": {"$in": [ObjectId(bid) for bid in batch_ids]},
        "teacher_id": str(user.id)
    }).to_list(length=None)
    
    if len(batches) != len(batch_ids):
        raise HTTPException(400, "Invalid batch IDs")
    
    # Update assessment
    await db.assessments.update_one(
        {"_id": ObjectId(assessment_id)},
        {"$set": {"assigned_batches": batch_ids}}
    )
    
    # Send notifications if published
    if assessment.get("status") == "published":
        await send_assessment_notifications(
            db,
            assessment_id,
            batch_ids,
            assessment["title"]
        )
    
    return {"message": f"Assessment assigned to {len(batch_ids)} batches"}
```

---

## Student Assessment Taking

### Feature Overview
Students can view available assessments assigned to their batch and take them within the specified time limit.

### Student Takes Assessment Flow

#### Process Diagram
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Student    │    │   Frontend   │    │   Backend    │    │   Database   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       │ 1. View Available │                   │                   │
       │    Assessments    │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ 2. GET /assessments/                  │
       │                   │    student/available                  │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 3. Get Student's  │
       │                   │                   │    Batch ID       │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 4. Find Assessments│
       │                   │                   │    assigned to    │
       │                   │                   │    batch &        │
       │                   │                   │    status=published│
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 5. Check          │
       │                   │                   │    Submissions    │
       │                   │                   │    (filter taken) │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │ 6. Available      │                   │
       │                   │    Assessments    │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 7. Display List   │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       │ 8. Click "Start"  │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ 9. GET /assessments/                  │
       │                   │    {id}/details   │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 10. Get Questions │
       │                   │                   │     (no correct   │
       │                   │                   │      answers)     │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │ 11. Questions     │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 12. Display       │                   │                   │
       │     Assessment    │                   │                   │
       │     UI with Timer │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       │ 13. Answer        │                   │                   │
       │     Questions     │                   │                   │
       │                   │                   │                   │
       │ 14. Submit        │                   │                   │
       │     Answers       │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ 15. POST /assessments/                │
       │                   │     {id}/submit   │                   │
       │                   │     {answers[],   │                   │
       │                   │      time_taken}  │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ [See Grading Flow]│
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/student/AvailableAssessments.tsx` - List of assessments
- `frontend/src/pages/student/TakeAssessment.tsx` - Assessment taking interface
- `frontend/src/components/AssessmentTimer.tsx` - Countdown timer
- `frontend/src/api/assessmentService.ts`
  - Function: `getAvailableAssessments()`
  - Function: `getAssessmentDetails(assessmentId)`
  - Function: `submitAssessment(assessmentId, submission)`

**Backend:**
- `backend/app/api/assessments/submissions.py`
  - Endpoint: `GET /api/assessments/student/available`
  - Endpoint: `GET /api/assessments/{id}/details`
  - Function: `get_available_assessments(user)`
  - Function: `get_assessment_details(assessment_id, user)`

#### Implementation

**1. Get Available Assessments**
```python
# File: backend/app/api/assessments/submissions.py
@router.get("/student/available", response_model=List[AssessmentSubmissionResponse])
async def get_available_assessments(user: UserModel = Depends(get_current_user)):
    """Get assessments available to current student"""
    db = await get_db()
    
    # Verify student role
    if user.role != "student":
        raise HTTPException(403, "Only students can access this endpoint")
    
    # Get student's batch
    student = await db.users.find_one({"_id": ObjectId(user.id)})
    if not student or not student.get("batch_id"):
        return []
    
    student_batch_id = str(student["batch_id"])
    
    # Get assessments assigned to batch
    assessments = await db.assessments.find({
        "assigned_batches": student_batch_id,
        "status": {"$in": ["published", "active"]},
        "is_active": True
    }).to_list(length=None)
    
    # Get student's submissions
    submissions = await db.assessment_submissions.find({
        "student_id": user.id
    }).to_list(length=None)
    
    submitted_ids = {str(s["assessment_id"]) for s in submissions}
    
    # Filter out already submitted assessments
    available = []
    for assessment in assessments:
        assessment_id = str(assessment["_id"])
        
        if assessment_id in submitted_ids:
            continue
        
        available.append(AssessmentSubmissionResponse(
            id=assessment_id,
            title=assessment["title"],
            subject=assessment["subject"],
            difficulty=assessment["difficulty"],
            description=assessment.get("description"),
            time_limit=assessment["time_limit"],
            max_attempts=assessment["max_attempts"],
            question_count=assessment["question_count"],
            type=assessment["type"],
            status="available"
        ))
    
    return available
```

**2. Get Assessment Details (Without Answers)**
```python
@router.get("/{assessment_id}/details")
async def get_assessment_details(
    assessment_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Get assessment details with questions (no correct answers)"""
    db = await get_db()
    
    assessment = await db.assessments.find_one({
        "_id": ObjectId(assessment_id),
        "status": {"$in": ["published", "active"]},
        "is_active": True
    })
    
    if not assessment:
        raise HTTPException(404, "Assessment not found")
    
    # Remove correct answers from questions
    questions = []
    for q in assessment.get("questions", []):
        questions.append({
            "id": q.get("id"),
            "question": q["question"],
            "options": q["options"],
            "points": q.get("points", 10)
            # correct_answer is NOT included
        })
    
    return {
        "id": str(assessment["_id"]),
        "title": assessment["title"],
        "subject": assessment["subject"],
        "description": assessment.get("description"),
        "time_limit": assessment["time_limit"],
        "questions": questions,
        "total_questions": len(questions)
    }
```

**3. Assessment Taking UI**
```typescript
// File: frontend/src/pages/student/TakeAssessment.tsx
const TakeAssessment: React.FC = () => {
  const { assessmentId } = useParams();
  const [assessment, setAssessment] = useState<any>(null);
  const [answers, setAnswers] = useState<number[]>([]);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [startTime] = useState<number>(Date.now());
  
  useEffect(() => {
    loadAssessment();
  }, [assessmentId]);
  
  useEffect(() => {
    if (timeRemaining <= 0 && assessment) {
      handleAutoSubmit();
    }
  }, [timeRemaining]);
  
  const loadAssessment = async () => {
    const data = await assessmentService.getAssessmentDetails(assessmentId);
    setAssessment(data);
    setTimeRemaining(data.time_limit * 60); // Convert to seconds
    setAnswers(new Array(data.questions.length).fill(-1));
  };
  
  const handleAnswerChange = (questionIndex: number, optionIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = optionIndex;
    setAnswers(newAnswers);
  };
  
  const handleSubmit = async () => {
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);
    
    try {
      const result = await assessmentService.submitAssessment(assessmentId, {
        answers,
        time_taken: timeTaken
      });
      
      toast.success('Assessment submitted successfully!');
      navigate(`/student/results/${result.id}`);
    } catch (error) {
      toast.error('Failed to submit assessment');
    }
  };
  
  const handleAutoSubmit = () => {
    toast.warning('Time expired! Auto-submitting...');
    handleSubmit();
  };
  
  if (!assessment) return <LoadingSpinner />;
  
  return (
    <div className="assessment-container">
      <div className="assessment-header">
        <h1>{assessment.title}</h1>
        <AssessmentTimer
          timeRemaining={timeRemaining}
          onTimerUpdate={setTimeRemaining}
        />
      </div>
      
      <div className="questions">
        {assessment.questions.map((q, index) => (
          <div key={q.id} className="question-card">
            <h3>Question {index + 1}</h3>
            <p>{q.question}</p>
            
            <div className="options">
              {q.options.map((option, optIndex) => (
                <label key={optIndex}>
                  <input
                    type="radio"
                    name={`question-${index}`}
                    checked={answers[index] === optIndex}
                    onChange={() => handleAnswerChange(index, optIndex)}
                  />
                  {option}
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <button onClick={handleSubmit} className="submit-btn">
        Submit Assessment
      </button>
    </div>
  );
};
```

---

## Assessment Submission & Grading

### Feature Overview
Automatic grading of student submissions with instant score calculation and feedback.

### Submission & Grading Flow

#### Process Diagram
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Student    │    │   Frontend   │    │   Backend    │    │   Database   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       │ Submit Answers    │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ POST /assessments/│                   │
       │                   │ {id}/submit       │                   │
       │                   │ {answers[],       │                   │
       │                   │  time_taken}      │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 1. Validate Student│
       │                   │                   │    & Assessment   │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 2. Check Not      │
       │                   │                   │    Already        │
       │                   │                   │    Submitted      │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 3. Get Assessment │
       │                   │                   │    with Answers   │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 4. Calculate Score│
       │                   │                   │    For each Q:    │
       │                   │                   │    if correct:    │
       │                   │                   │      score += pts │
       │                   │                   ├──────┐            │
       │                   │                   │      │            │
       │                   │                   │◀─────┘            │
       │                   │                   │                   │
       │                   │                   │ 5. Create Result  │
       │                   │                   │    Document       │
       │                   │                   │    {student_id,   │
       │                   │                   │     assessment_id,│
       │                   │                   │     score,        │
       │                   │                   │     answers,      │
       │                   │                   │     correct_answers}│
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 6. Update User    │
       │                   │                   │    Stats/XP       │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 7. Create         │
       │                   │                   │    Notification   │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 8. Check for      │
       │                   │                   │    Badges/        │
       │                   │                   │    Achievements   │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │ 9. Response       │                   │
       │                   │    {result_id,    │                   │
       │                   │     score,        │                   │
       │                   │     percentage}   │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 10. Show Results  │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
```

#### Implementation

**1. Submit Assessment**
```python
# File: backend/app/api/assessments/submissions.py
@router.post("/{assessment_id}/submit", response_model=AssessmentResult)
async def submit_assessment(
    assessment_id: str,
    submission: AssessmentSubmission,
    user: UserModel = Depends(get_current_user)
):
    """Submit assessment answers and calculate score"""
    db = await get_db()
    
    # Get assessment with correct answers
    assessment = await db.assessments.find_one({
        "_id": ObjectId(assessment_id)
    })
    
    if not assessment:
        raise HTTPException(404, "Assessment not found")
    
    # Check if already submitted
    existing = await db.assessment_submissions.find_one({
        "student_id": user.id,
        "assessment_id": assessment_id
    })
    
    if existing:
        raise HTTPException(400, "Assessment already submitted")
    
    # Calculate score
    questions = assessment["questions"]
    total_score = 0
    max_score = sum(q.get("points", 10) for q in questions)
    correct_count = 0
    
    answer_details = []
    for i, question in enumerate(questions):
        user_answer = submission.answers[i] if i < len(submission.answers) else -1
        correct_answer = question["correct_answer"]
        is_correct = user_answer == correct_answer
        
        if is_correct:
            points = question.get("points", 10)
            total_score += points
            correct_count += 1
        
        answer_details.append({
            "question_id": question["id"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "points_earned": points if is_correct else 0
        })
    
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    
    # Create result document
    result_doc = {
        "_id": str(uuid4()),
        "assessment_id": assessment_id,
        "student_id": user.id,
        "student_name": user.name,
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "time_taken": submission.time_taken,
        "answers": answer_details,
        "submitted_at": datetime.utcnow()
    }
    
    await db.assessment_submissions.insert_one(result_doc)
    
    # Update user stats
    await update_user_gamification(
        db,
        user.id,
        {
            "xp_earned": calculate_xp(percentage),
            "assessments_completed": 1
        }
    )
    
    # Create completion notification
    await create_notification(
        db,
        user.id,
        f"Assessment Complete: {assessment['title']}",
        f"You scored {percentage:.1f}%",
        "assessment"
    )
    
    # Check for achievements
    await check_and_award_badges(db, user.id, percentage, correct_count)
    
    return AssessmentResult(
        id=result_doc["_id"],
        assessment_id=assessment_id,
        student_id=user.id,
        student_name=user.name,
        score=total_score,
        max_score=max_score,
        percentage=percentage,
        correct_count=correct_count,
        total_questions=len(questions),
        time_taken=submission.time_taken,
        submitted_at=result_doc["submitted_at"].isoformat()
    )
```

**2. XP Calculation**
```python
def calculate_xp(percentage: float) -> int:
    """Calculate XP based on score percentage"""
    base_xp = 100
    
    if percentage >= 90:
        return base_xp + 50  # Perfect performance bonus
    elif percentage >= 75:
        return base_xp + 25
    elif percentage >= 50:
        return base_xp
    else:
        return base_xp // 2  # Partial credit
```

---

## Results & Leaderboards

### Feature Overview
Students can view detailed results with question-by-question analysis, and teachers can view leaderboards for each assessment.

### View Results Flow

```python
# File: backend/app/api/results.py
@router.get("/{result_id}/detailed")
async def get_detailed_result(
    result_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Get detailed result with question review"""
    db = await get_db()
    
    result = await db.assessment_submissions.find_one({
        "_id": result_id
    })
    
    if not result:
        raise HTTPException(404, "Result not found")
    
    # Verify user owns this result or is teacher/admin
    if result["student_id"] != user.id and user.role not in ["teacher", "admin"]:
        raise HTTPException(403, "Unauthorized")
    
    # Get assessment details
    assessment = await db.assessments.find_one({
        "_id": ObjectId(result["assessment_id"])
    })
    
    # Build detailed response
    questions_review = []
    for answer in result["answers"]:
        question = next(
            (q for q in assessment["questions"] if q["id"] == answer["question_id"]),
            None
        )
        
        if question:
            questions_review.append({
                "question": question["question"],
                "options": question["options"],
                "user_answer": answer["user_answer"],
                "correct_answer": answer["correct_answer"],
                "is_correct": answer["is_correct"],
                "explanation": question.get("explanation", ""),
                "points_earned": answer["points_earned"]
            })
    
    return {
        "result_id": result_id,
        "assessment_title": assessment["title"],
        "score": result["score"],
        "max_score": result["max_score"],
        "percentage": result["percentage"],
        "correct_count": result["correct_count"],
        "total_questions": result["total_questions"],
        "time_taken": result["time_taken"],
        "submitted_at": result["submitted_at"],
        "questions_review": questions_review
    }
```

### Leaderboard

```python
# File: backend/app/api/assessments/submissions.py
@router.get("/{assessment_id}/leaderboard", response_model=AssessmentLeaderboard)
async def get_leaderboard(
    assessment_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Get leaderboard for an assessment"""
    db = await get_db()
    
    # Get all submissions for this assessment
    submissions = await db.assessment_submissions.find({
        "assessment_id": assessment_id
    }).sort("score", -1).limit(100).to_list(length=100)
    
    leaderboard = []
    for i, submission in enumerate(submissions):
        leaderboard.append(LeaderboardEntry(
            rank=i + 1,
            student_id=submission["student_id"],
            student_name=submission["student_name"],
            score=submission["score"],
            max_score=submission["max_score"],
            percentage=submission["percentage"],
            time_taken=submission["time_taken"],
            submitted_at=submission["submitted_at"].isoformat()
        ))
    
    return AssessmentLeaderboard(
        assessment_id=assessment_id,
        total_submissions=len(leaderboard),
        leaderboard=leaderboard
    )
```

---

## Topic Configuration

### Feature Overview
Students and teachers can configure topic preferences for AI-generated assessments.

```python
# File: backend/app/api/topics.py
@router.post("/")
async def save_topic_config(
    config: TopicConfig,
    user: UserModel = Depends(get_current_user)
):
    """Save topic configuration for assessment generation"""
    db = await get_db()
    
    config_doc = {
        "user_id": user.id,
        "topic": config.topic,
        "qnCount": config.qnCount,
        "difficulty": config.difficulty,
        "updated_at": datetime.utcnow()
    }
    
    # Upsert configuration
    await db.topic_configs.update_one(
        {"user_id": user.id},
        {"$set": config_doc},
        upsert=True
    )
    
    return {"message": "Topic configuration saved"}

@router.get("/")
async def get_topic_config(user: UserModel = Depends(get_current_user)):
    """Get saved topic configuration"""
    db = await get_db()
    
    config = await db.topic_configs.find_one({"user_id": user.id})
    
    if not config:
        return {
            "topic": "",
            "qnCount": 10,
            "difficulty": "medium"
        }
    
    return {
        "topic": config["topic"],
        "qnCount": config["qnCount"],
        "difficulty": config["difficulty"]
    }
```

---

## Summary

### Assessment System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   ASSESSMENT SYSTEM                        │
└────────────────────────────────────────────────────────────┘

Teacher Workflow:
  1. Configure Topics (optional)
  2. Create Assessment (Manual/AI/Coding)
  3. Add/Generate Questions
  4. Publish Assessment
  5. Assign to Batches
  6. Monitor Submissions
  7. View Analytics

Student Workflow:
  1. Receive Notification
  2. View Available Assessments
  3. Start Assessment
  4. Answer Questions (timed)
  5. Submit Answers
  6. View Results
  7. Review Answers
  8. Check Leaderboard

Automated Processes:
  - AI Question Generation (Gemini)
  - Automatic Grading
  - XP/Badge Awards
  - Notifications
  - Analytics Updates
```

### Key Database Collections

1. **assessments** - Assessment metadata and questions
2. **assessment_submissions** - Student submissions and scores
3. **topic_configs** - User topic preferences
4. **notifications** - Assessment notifications
5. **user_stats** - Gamification data

### API Endpoints Summary

| Endpoint | Method | Purpose | Role |
|----------|--------|---------|------|
| `/assessments/` | POST | Create assessment | Teacher |
| `/assessments/` | GET | List assessments | Teacher |
| `/assessments/{id}/questions` | POST | Add question | Teacher |
| `/assessments/{id}/publish` | POST | Publish assessment | Teacher |
| `/assessments/{id}/assign-batches` | POST | Assign to batches | Teacher |
| `/assessments/student/available` | GET | Get available | Student |
| `/assessments/{id}/details` | GET | Get questions | Student |
| `/assessments/{id}/submit` | POST | Submit answers | Student |
| `/assessments/{id}/leaderboard` | GET | View leaderboard | All |
| `/results/{id}/detailed` | GET | Detailed results | Student |
| `/topic` | POST | Save config | All |
| `/topic` | GET | Get config | All |

---

**[Back to Features Overview](./FEATURES_OVERVIEW.md)** | **[Next: Student Features →](./STUDENT_FEATURES.md)**
