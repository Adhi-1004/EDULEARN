import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from prompts import (
    prompt_for_coding,
    prompt_for_mcq,
    prompt_for_text_question,
    feedback_prompt,
    personalized_coding_prompt,
    code_evaluation_prompt,
)
import random
import time

# Simple question tracking to prevent repetition
recent_questions = {}
MAX_RECENT_QUESTIONS = 50  # Keep track of last 50 questions per topic

def _add_to_recent_questions(topic: str, questions: list):
    """Add questions to recent tracking to prevent repetition"""
    if topic not in recent_questions:
        recent_questions[topic] = []
    
    # Add new questions
    for q in questions:
        question_text = q.get('Question', '').lower().strip()
        if question_text:
            recent_questions[topic].append({
                'text': question_text,
                'timestamp': time.time()
            })
    
    # Keep only recent questions (last 50)
    if len(recent_questions[topic]) > MAX_RECENT_QUESTIONS:
        recent_questions[topic] = recent_questions[topic][-MAX_RECENT_QUESTIONS:]

def _is_question_recent(topic: str, question_text: str) -> bool:
    """Check if a question was recently generated for this topic"""
    if topic not in recent_questions:
        return False
    
    question_lower = question_text.lower().strip()
    for recent_q in recent_questions[topic]:
        if recent_q['text'] == question_lower:
            return True
    return False


# Load .env from the Backend directory explicitly so local secrets work
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
# Attempt to load an adjacent .env file; ignore if missing
try:
    load_dotenv(ENV_PATH, override=False)
except Exception:
    pass

# Configure Gemini AI
api_key = os.getenv("GEMINI_API_KEY") or ""
if not api_key:
    # Fall back to hard-coded value provided by the user only if nothing else is set.
    # This avoids requiring system-level env changes.
    api_key = "AIzaSyCeT9KMPDDZwHFabO_57mx12SM27pDurh0"
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables")
    model = None

def chat(content):
    print(f"🤖 [GEMINI] Starting chat request...")
    system_prompt = "Just go along with what the user is saying, encourage about studies and give reply in short message format, act like you know about the user and blabber something regarding what they are asking about their academics"
    
    try:
        if not model:
            return "I'm sorry, but the AI service is not configured. Please set up your GEMINI_API_KEY in the .env file."
        
        response = model.generate_content(
            f"{system_prompt}\n\nUser: {content}",
            generation_config=genai.types.GenerationConfig(
                temperature=1.0,
                max_output_tokens=1024,
                top_p=1.0
            )
        )
        print(f"✅ [GEMINI] Chat response generated successfully")
        return response.text
    except Exception as e:
        print(f"❌ [GEMINI] Error in chat: {str(e)}")
        raise e



def callgemini(user_prompt, system_prompt):
    print(f"🤖 [GEMINI] Starting structured request...")
    full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nPlease respond in valid JSON format."
    
    try:
        if not model:
            # Return mock data for testing
            if "MCQ" in user_prompt:
                return json.dumps({
                    "Questions": [
                        {
                            "Question": "What is the primary function of an operating system?",
                            "Options": [
                                "To provide a user interface",
                                "To manage hardware resources and provide services for applications",
                                "To run applications",
                                "To store data"
                            ],
                            "Answer": 1
                        },
                        {
                            "Question": "Which of the following is NOT a type of operating system?",
                            "Options": [
                                "Batch operating system",
                                "Time-sharing operating system",
                                "Distributed operating system",
                                "Web operating system"
                            ],
                            "Answer": 3
                        },
                        {
                            "Question": "What is the main purpose of process scheduling?",
                            "Options": [
                                "To allocate memory to processes",
                                "To manage file systems",
                                "To maximize CPU utilization and minimize response time",
                                "To handle user input"
                            ],
                            "Answer": 2
                        },
                        {
                            "Question": "Which scheduling algorithm is considered the simplest?",
                            "Options": [
                                "Round Robin",
                                "First Come First Serve (FCFS)",
                                "Shortest Job First (SJF)",
                                "Priority Scheduling"
                            ],
                            "Answer": 1
                        },
                        {
                            "Question": "What is virtual memory?",
                            "Options": [
                                "A type of RAM",
                                "A technique that allows the execution of processes that may not be completely in memory",
                                "A backup storage system",
                                "A type of cache memory"
                            ],
                            "Answer": 1
                        }
                    ]
                })
            else:
                return json.dumps({"error": "Mock data not available for this type"})
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=1910,
                top_p=1.0
            )
        )
        print(f"✅ [GEMINI] Structured response generated successfully")
        return response.text
    except Exception as e:
        print(f"❌ [GEMINI] Error in structured request: {str(e)}")
        # Fallback: return an empty string so caller can handle mock generation
        return ""


def _generate_mcq_fallback(topic: str, count: int, difficulty: str = "medium") -> dict:
    """Generate diverse MCQ questions as fallback when AI is unavailable"""
    random.seed()
    result = {"Questions": []}
    
    # Topic-specific question templates for better variety
    topic_templates = {
        "science": [
            "Which of the following is a fundamental principle in {topic}?",
            "What is the primary function of {topic} in natural systems?",
            "How does {topic} contribute to our understanding of the world?",
            "Which statement best describes the role of {topic}?",
            "What is a key characteristic of {topic}?",
            "Which concept is most closely related to {topic}?",
            "What is the main purpose of studying {topic}?",
            "Which of the following represents {topic} correctly?",
            "How is {topic} applied in practical situations?",
            "What distinguishes {topic} from other related concepts?",
            "What is the significance of {topic} in modern research?",
            "Which aspect of {topic} is most important for beginners?",
            "How does {topic} relate to everyday phenomena?",
            "What makes {topic} unique in its field?",
            "Which principle underlies the study of {topic}?"
        ],
        "math": [
            "What is the fundamental concept in {topic}?",
            "Which formula is used to calculate {topic}?",
            "What is the primary application of {topic}?",
            "Which method is most effective for solving {topic} problems?",
            "What is the relationship between {topic} and other mathematical concepts?",
            "Which principle underlies {topic}?",
            "How is {topic} used in real-world calculations?",
            "What is the key difference in {topic} approaches?",
            "Which technique is essential for understanding {topic}?",
            "What makes {topic} important in mathematics?",
            "What is the core theory behind {topic}?",
            "Which approach is most practical for {topic}?",
            "How does {topic} connect to other mathematical fields?",
            "What is the historical significance of {topic}?",
            "Which aspect of {topic} is most challenging?"
        ],
        "technology": [
            "What is the core technology behind {topic}?",
            "Which component is essential for {topic} to function?",
            "How does {topic} improve system performance?",
            "What is the primary advantage of {topic}?",
            "Which feature distinguishes {topic} from alternatives?",
            "What is the main purpose of {topic} in computing?",
            "How is {topic} implemented in modern systems?",
            "Which principle guides the development of {topic}?",
            "What makes {topic} relevant in today's technology?",
            "Which aspect of {topic} is most critical for success?",
            "What is the future potential of {topic}?",
            "How does {topic} enhance user experience?",
            "Which innovation makes {topic} possible?",
            "What is the scalability of {topic}?",
            "How does {topic} integrate with existing systems?"
        ],
        "general": [
            "Which of the following best describes {topic}?",
            "What is the main concept behind {topic}?",
            "How is {topic} typically applied?",
            "Which statement accurately represents {topic}?",
            "What is the primary goal of {topic}?",
            "Which characteristic defines {topic}?",
            "What makes {topic} important?",
            "Which approach is most effective for {topic}?",
            "What is the key principle of {topic}?",
            "How does {topic} contribute to its field?",
            "What is the scope of {topic}?",
            "Which aspect of {topic} is most valuable?",
            "How does {topic} evolve over time?",
            "What is the impact of {topic} on society?",
            "Which perspective best explains {topic}?"
        ]
    }
    
    # Determine topic category
    topic_lower = topic.lower()
    if any(word in topic_lower for word in ["science", "physics", "chemistry", "biology", "geology"]):
        category = "science"
    elif any(word in topic_lower for word in ["math", "algebra", "calculus", "geometry", "statistics"]):
        category = "math"
    elif any(word in topic_lower for word in ["computer", "programming", "software", "technology", "coding"]):
        category = "technology"
    else:
        category = "general"
    
    templates = topic_templates[category]
    
    # Difficulty-based answer complexity
    difficulty_answers = {
        "very_easy": ["basic", "simple", "fundamental", "essential"],
        "easy": ["important", "common", "standard", "typical"],
        "medium": ["advanced", "complex", "sophisticated", "comprehensive"],
        "hard": ["specialized", "technical", "expert", "professional"],
        "very_hard": ["cutting-edge", "innovative", "revolutionary", "breakthrough"]
    }
    
    answer_words = difficulty_answers.get(difficulty, difficulty_answers["medium"])
    
    # Generate unique questions
    used_templates = set()
    attempts = 0
    max_attempts = count * 3  # Allow some retries for variety
    
    for i in range(max(1, int(count))):
        # Ensure template variety and avoid recent questions
        available_templates = [t for t in templates if t not in used_templates]
        if not available_templates:
            used_templates.clear()  # Reset if all used
            available_templates = templates
        
        template = random.choice(available_templates)
        used_templates.add(template)
        
        qtext = template.format(topic=topic)
        
        # Check if this question was recently generated
        if _is_question_recent(topic, qtext):
            attempts += 1
            if attempts > max_attempts:
                # If too many attempts, use a different template
                template = random.choice(templates)
                qtext = template.format(topic=topic)
            continue
        
        correct = random.randint(0, 3)
        
        # Generate more realistic options
        correct_answer = f"A {random.choice(answer_words)} aspect of {topic}"
        wrong_answers = [
            f"A related but different concept to {topic}",
            f"An outdated approach to {topic}",
            f"A common misconception about {topic}",
            f"An alternative method in {topic}",
            f"A secondary feature of {topic}",
            f"A preliminary step in {topic}",
            f"A supporting element of {topic}",
            f"A variation of {topic} methodology"
        ]
        
        # Shuffle wrong answers and select 3
        random.shuffle(wrong_answers)
        options = wrong_answers[:3]
        options.insert(correct, correct_answer)
        
        # Generate detailed explanation
        explanations = [
            f"The correct answer identifies a {random.choice(answer_words)} aspect of {topic}, which is essential for understanding this concept.",
            f"This option correctly represents the core principle of {topic}, distinguishing it from related but different concepts.",
            f"The answer highlights the fundamental characteristic of {topic} that makes it important in its field.",
            f"This choice accurately describes the primary function of {topic} in practical applications."
        ]
        
        result["Questions"].append({
            "Question": qtext,
            "Options": options,
            "Answer": correct,
            "tags": [topic.lower(), difficulty, category],
            "explanation": random.choice(explanations)
        })
    
    return result


def generate_question(topic, type, questions, subject=None, difficulty=None):
    # Build a richer user prompt including optional subject and difficulty
    user_prompt = (
        "user given topic = {topic}; NUMBER OF QUESTIONS = {questions}"
    ).format(topic=topic, questions=questions)
    if subject:
        user_prompt += "; subject = {subject}".format(subject=subject)
    if difficulty:
        user_prompt += "; difficulty = {difficulty}".format(difficulty=difficulty)
    
    # Ensure difficulty is a string with default
    difficulty_str = str(difficulty) if difficulty else "medium"
    
    if type=="MCQ":
        answer = callgemini(user_prompt, prompt_for_mcq)
        if not answer:
            # Quota or other error – fallback with difficulty
            result = _generate_mcq_fallback(topic, questions, difficulty_str)
        else:
            try:
                result = json.loads(answer) if isinstance(answer, str) and answer.strip() else {}
                if not result:
                    result = _generate_mcq_fallback(topic, questions, difficulty_str)
            except json.JSONDecodeError:
                result = _generate_mcq_fallback(topic, questions, difficulty_str)
        
        # Track generated questions to prevent repetition
        if result and "Questions" in result:
            _add_to_recent_questions(topic, result["Questions"])
        
        return result
    elif type=='TEXT':
        answer = callgemini(user_prompt, prompt_for_text_question)
    else:
        answer = callgemini(user_prompt, prompt_for_coding)
    
    parsed = json.loads(answer) if isinstance(answer, str) and answer.strip() else {}
    return parsed



"""
Generating prompt for question analysis
"""





def generate_question_feedback(questions,score):
    user_prompt = "" + "\n\n" + json.dumps({"responses": questions,"scores": score}, indent=2)
    answer = callgemini(user_prompt,feedback_prompt)
    parsed = json.loads(answer)
    return parsed



assignment_feedback_system_prompt = """
Role:
You are an academic evaluator.

Input Format:
The user will provide:
•⁠  ⁠An assignment question (what was asked).
•⁠  ⁠A full assignment answer (student's entire submission as a single string).

Output Format (Strictly respond in this JSON format):
{
  "score_summary": "<e.g., Good effort. Score: 7 out of 10>",
  "what_was_good": "<Brief highlights of strengths in the answer>",
  "what_was_missing_or_wrong": "<Brief areas that need improvement>",
  "suggestions": [
    "<Tip 1>",
    "<Tip 2>"
  ]
}

Rules:
•⁠  ⁠Evaluate the entire assignment holistically (do NOT evaluate question-by-question).
•⁠  ⁠Be concise, constructive, and positive.
•⁠  ⁠Avoid repeating the student’s exact words.
•⁠  ⁠Do NOT include any text outside the JSON object.
"""





def generate_assugnment_feedback(question,answer):
    user_prompt = """
Assignment Question:
{assignment_question}

Assignment Answer:
\"\"\"
{assignment_answer}
\"\"\"
""".format(assignment_answer = answer,assignment_question = question)
    
    answer = callgemini(user_prompt,assignment_feedback_system_prompt)
    parsed = json.loads(answer)
    return parsed


# New helpers for personalized coding problems and AI evaluation
def generate_personalized_coding_problems(payload: dict):
    """payload expects: { user_id, topic, difficulty, count, preferred_languages? }
    Returns parsed JSON from Gemini.
    """
    user_prompt = json.dumps(payload, ensure_ascii=False)
    answer = callgemini(user_prompt, personalized_coding_prompt)
    parsed = json.loads(answer)
    return parsed


def evaluate_code_with_ai(payload: dict):
    """payload expects: { language, code, problem, test_cases }
    Returns parsed JSON from Gemini.
    """
    user_prompt = json.dumps(payload, ensure_ascii=False)
    answer = callgemini(user_prompt, code_evaluation_prompt)
    parsed = json.loads(answer)
    return parsed
    

    


    
# print(generate_question("OS"))
# generate_question("os")
