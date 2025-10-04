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

from ..db import get_db
from ..schemas import QuestionCreate, QuestionResponse
from ..models import QuestionModel
from .endpoints.auth import get_current_user_id

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

def get_fallback_questions(topic: str, difficulty: str, count: int) -> List[dict]:
    """Generate fallback questions when AI is not available"""
    fallback_questions = {
        "python": {
            "easy": [
                {
                    "question": "What is the time complexity of accessing an element in a Python list by index?",
                    "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
                    "correct_answer": "O(1)",
                    "explanation": "Python lists are implemented as dynamic arrays, allowing constant-time O(1) access to elements by index."
                },
                {
                    "question": "Which Python data structure is most efficient for implementing a LIFO (Last In, First Out) stack?",
                    "options": ["list", "deque", "set", "tuple"],
                    "correct_answer": "deque",
                    "explanation": "collections.deque is optimized for append and pop operations at both ends, making it ideal for stack operations."
                },
                {
                    "question": "What is the output of the following code: print([x**2 for x in range(5) if x % 2 == 0])?",
                    "options": ["[0, 4, 16]", "[1, 9]", "[0, 1, 4, 9, 16]", "[0, 2, 4]"],
                    "correct_answer": "[0, 4, 16]",
                    "explanation": "The list comprehension squares even numbers (0, 2, 4) from range(5), resulting in [0, 4, 16]."
                }
            ],
            "medium": [
                {
                    "question": "What is the output of the following code: def func(x, *args, **kwargs): return len(args) + len(kwargs); print(func(1, 2, 3, a=4, b=5))?",
                    "options": ["5", "4", "3", "Error"],
                    "correct_answer": "5",
                    "explanation": "The function receives 2 positional arguments (2, 3) and 2 keyword arguments (a=4, b=5), so len(args) + len(kwargs) = 2 + 2 = 4."
                },
                {
                    "question": "Which Python feature allows for multiple inheritance and method resolution order (MRO)?",
                    "options": ["Duck typing", "C3 linearization", "Method overloading", "Function decorators"],
                    "correct_answer": "C3 linearization",
                    "explanation": "C3 linearization is the algorithm Python uses to determine the method resolution order in multiple inheritance scenarios."
                },
                {
                    "question": "What is the time complexity of the following code: result = [x for x in range(n) if x % 2 == 0]?",
                    "options": ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
                    "correct_answer": "O(n)",
                    "explanation": "The list comprehension iterates through n elements once, making it O(n) time complexity."
                }
            ],
            "hard": [
                {
                    "question": "What is the output of the following metaclass code: class Meta(type): def __new__(cls, name, bases, dct): dct['_count'] = 0; return super().__new__(cls, name, bases, dct); class A(metaclass=Meta): pass; print(A._count)?",
                    "options": ["0", "1", "AttributeError", "TypeError"],
                    "correct_answer": "0",
                    "explanation": "The metaclass adds a _count attribute with value 0 to the class, which is accessible as a class attribute."
                },
                {
                    "question": "Which Python optimization technique is used in the following code: @lru_cache(maxsize=128); def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)?",
                    "options": ["Memoization", "Tail recursion", "Loop unrolling", "Vectorization"],
                    "correct_answer": "Memoization",
                    "explanation": "The @lru_cache decorator implements memoization, storing previously computed results to avoid redundant calculations."
                },
                {
                    "question": "What is the time complexity of the following algorithm: def binary_search(arr, target): left, right = 0, len(arr)-1; while left <= right: mid = (left + right) // 2; if arr[mid] == target: return mid; elif arr[mid] < target: left = mid + 1; else: right = mid - 1; return -1?",
                    "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
                    "correct_answer": "O(log n)",
                    "explanation": "Binary search eliminates half of the search space in each iteration, resulting in O(log n) time complexity."
                }
            ]
        },
        "javascript": {
            "easy": [
                {
                    "question": "What is the output of the following code: console.log(typeof function() {});?",
                    "options": ["function", "object", "undefined", "string"],
                    "correct_answer": "function",
                    "explanation": "Functions in JavaScript are first-class objects, but typeof specifically returns 'function' for function objects."
                },
                {
                    "question": "Which JavaScript feature allows for asynchronous programming without blocking the main thread?",
                    "options": ["Promises", "Callbacks", "Event loops", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": "JavaScript uses callbacks, promises, and the event loop to handle asynchronous operations without blocking execution."
                },
                {
                    "question": "What is the result of the following code: const arr = [1, 2, 3]; arr[10] = 10; console.log(arr.length);?",
                    "options": ["3", "4", "11", "10"],
                    "correct_answer": "11",
                    "explanation": "Setting arr[10] = 10 creates a sparse array with length 11, filling indices 3-9 with empty slots."
                }
            ],
            "medium": [
                {
                    "question": "What is the output of the following code: const obj = { a: 1, b: 2 }; const { a, ...rest } = obj; console.log(rest);?",
                    "options": ["{ b: 2 }", "{ a: 1 }", "undefined", "Error"],
                    "correct_answer": "{ b: 2 }",
                    "explanation": "Destructuring assignment extracts 'a' and collects the remaining properties in 'rest', which contains { b: 2 }."
                },
                {
                    "question": "Which JavaScript pattern is demonstrated here: const createCounter = () => { let count = 0; return () => ++count; };?",
                    "options": ["Factory pattern", "Closure pattern", "Module pattern", "Singleton pattern"],
                    "correct_answer": "Closure pattern",
                    "explanation": "The function returns another function that has access to the outer function's variables, creating a closure."
                },
                {
                    "question": "What is the time complexity of the following code: const result = arr.filter(x => x > 0).map(x => x * 2);?",
                    "options": ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
                    "correct_answer": "O(n)",
                    "explanation": "Both filter and map operations iterate through the array once, resulting in O(n) time complexity."
                }
            ],
            "hard": [
                {
                    "question": "What is the output of the following code: async function test() { console.log(1); await Promise.resolve(); console.log(2); } test(); console.log(3);?",
                    "options": ["1, 2, 3", "1, 3, 2", "3, 1, 2", "Error"],
                    "correct_answer": "1, 3, 2",
                    "explanation": "The async function starts executing (1), then yields control at await, allowing the synchronous code (3) to run before resuming (2)."
                },
                {
                    "question": "Which JavaScript concept is demonstrated by this code: const curry = fn => (...args) => args.length >= fn.length ? fn(...args) : (...more) => curry(fn)(...args, ...more);?",
                    "options": ["Memoization", "Currying", "Throttling", "Debouncing"],
                    "correct_answer": "Currying",
                    "explanation": "This is a currying function that transforms a multi-argument function into a sequence of single-argument functions."
                },
                {
                    "question": "What is the output of the following code: const arr = [1, 2, 3]; arr.forEach((item, index) => { if (index === 1) arr.splice(index, 1); }); console.log(arr);?",
                    "options": ["[1, 2, 3]", "[1, 3]", "[1, 2]", "Error"],
                    "correct_answer": "[1, 3]",
                    "explanation": "Modifying the array during iteration with splice removes the element at index 1, resulting in [1, 3]."
                }
            ]
        },
        "science": {
            "easy": [
                {
                    "question": "What is the molecular geometry of methane (CH4)?",
                    "options": ["Tetrahedral", "Trigonal planar", "Linear", "Bent"],
                    "correct_answer": "Tetrahedral",
                    "explanation": "Methane has a tetrahedral geometry due to sp³ hybridization of the carbon atom and the repulsion between four bonding pairs."
                },
                {
                    "question": "Which law states that energy cannot be created or destroyed, only transformed?",
                    "options": ["Newton's First Law", "Law of Conservation of Energy", "Boyle's Law", "Ohm's Law"],
                    "correct_answer": "Law of Conservation of Energy",
                    "explanation": "The Law of Conservation of Energy (First Law of Thermodynamics) states that energy is conserved in isolated systems."
                },
                {
                    "question": "What is the pH of a neutral solution at 25°C?",
                    "options": ["6", "7", "8", "14"],
                    "correct_answer": "7",
                    "explanation": "At 25°C, a neutral solution has equal concentrations of H⁺ and OH⁻ ions, resulting in pH = 7."
                }
            ],
            "medium": [
                {
                    "question": "What is the relationship between frequency and wavelength in electromagnetic radiation?",
                    "options": ["Directly proportional", "Inversely proportional", "Exponentially related", "No relationship"],
                    "correct_answer": "Inversely proportional",
                    "explanation": "According to the equation c = λν, frequency and wavelength are inversely proportional, where c is the speed of light."
                },
                {
                    "question": "Which process is responsible for the production of ATP in mitochondria?",
                    "options": ["Glycolysis", "Electron transport chain", "Krebs cycle", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": "Cellular respiration involves glycolysis, the Krebs cycle, and the electron transport chain, all contributing to ATP production."
                },
                {
                    "question": "What is the difference between an element and a compound?",
                    "options": ["Elements are pure substances, compounds are mixtures", "Elements contain one type of atom, compounds contain multiple types", "No difference", "Elements are smaller than compounds"],
                    "correct_answer": "Elements contain one type of atom, compounds contain multiple types",
                    "explanation": "Elements consist of atoms with the same atomic number, while compounds are composed of two or more different elements chemically bonded."
                }
            ],
            "hard": [
                {
                    "question": "What is the significance of the Heisenberg Uncertainty Principle?",
                    "options": ["It limits measurement precision", "It explains quantum entanglement", "It describes wave-particle duality", "It proves relativity"],
                    "correct_answer": "It limits measurement precision",
                    "explanation": "The Heisenberg Uncertainty Principle states that the more precisely we know a particle's position, the less precisely we can know its momentum, and vice versa."
                },
                {
                    "question": "Which thermodynamic process occurs at constant temperature?",
                    "options": ["Adiabatic", "Isobaric", "Isothermal", "Isochoric"],
                    "correct_answer": "Isothermal",
                    "explanation": "An isothermal process occurs at constant temperature, where the system exchanges heat with its surroundings to maintain thermal equilibrium."
                },
                {
                    "question": "What is the mechanism of action of competitive enzyme inhibition?",
                    "options": ["Binds to allosteric site", "Changes enzyme shape", "Competes with substrate for active site", "Destroys the enzyme"],
                    "correct_answer": "Competes with substrate for active site",
                    "explanation": "Competitive inhibitors structurally resemble the substrate and compete for binding to the enzyme's active site, reducing enzyme activity."
                }
            ]
        },
        "mathematics": {
            "easy": [
                {
                    "question": "What is the limit of (x² - 4)/(x - 2) as x approaches 2?",
                    "options": ["0", "4", "∞", "Undefined"],
                    "correct_answer": "4",
                    "explanation": "Using L'Hôpital's rule or factoring: lim(x→2) (x²-4)/(x-2) = lim(x→2) (x+2) = 4."
                },
                {
                    "question": "What is the determinant of the matrix [[3, 1], [2, 4]]?",
                    "options": ["10", "14", "12", "8"],
                    "correct_answer": "10",
                    "explanation": "For a 2×2 matrix [[a,b],[c,d]], the determinant is ad-bc = (3)(4)-(1)(2) = 12-2 = 10."
                },
                {
                    "question": "What is the derivative of sin(x) with respect to x?",
                    "options": ["cos(x)", "-cos(x)", "sin(x)", "-sin(x)"],
                    "correct_answer": "cos(x)",
                    "explanation": "The derivative of sin(x) is cos(x) by the standard differentiation rule for trigonometric functions."
                }
            ],
            "medium": [
                {
                    "question": "What is the value of the integral ∫₀^π sin(x) dx?",
                    "options": ["0", "1", "2", "π"],
                    "correct_answer": "2",
                    "explanation": "∫₀^π sin(x) dx = [-cos(x)]₀^π = -cos(π) - (-cos(0)) = -(-1) - (-1) = 1 + 1 = 2."
                },
                {
                    "question": "What is the eigenvalue of the matrix [[2, 0], [0, 3]]?",
                    "options": ["2 and 3", "5", "6", "1"],
                    "correct_answer": "2 and 3",
                    "explanation": "For a diagonal matrix, the eigenvalues are the diagonal elements: 2 and 3."
                },
                {
                    "question": "What is the Taylor series expansion of e^x around x = 0?",
                    "options": ["1 + x + x²/2! + x³/3! + ...", "x + x²/2 + x³/3 + ...", "1 - x + x²/2! - x³/3! + ...", "x - x²/2 + x³/3 - ..."],
                    "correct_answer": "1 + x + x²/2! + x³/3! + ...",
                    "explanation": "The Taylor series for e^x is Σ(n=0 to ∞) x^n/n! = 1 + x + x²/2! + x³/3! + ..."
                }
            ],
            "hard": [
                {
                    "question": "What is the solution to the differential equation dy/dx = y with initial condition y(0) = 1?",
                    "options": ["y = e^x", "y = e^(-x)", "y = x + 1", "y = x"],
                    "correct_answer": "y = e^x",
                    "explanation": "The general solution is y = Ce^x. With y(0) = 1, we get C = 1, so y = e^x."
                },
                {
                    "question": "What is the value of the complex number i^i?",
                    "options": ["1", "i", "e^(-π/2)", "π/2"],
                    "correct_answer": "e^(-π/2)",
                    "explanation": "Using Euler's formula: i^i = e^(i·ln(i)) = e^(i·iπ/2) = e^(-π/2) ≈ 0.2079."
                },
                {
                    "question": "What is the rank of the matrix [[1, 2, 3], [0, 1, 2], [0, 0, 0]]?",
                    "options": ["0", "1", "2", "3"],
                    "correct_answer": "2",
                    "explanation": "The rank is the number of linearly independent rows. The first two rows are independent, but the third row is all zeros, so rank = 2."
                }
            ]
        }
    }
    
    # Get questions for the topic and difficulty
    topic_questions = fallback_questions.get(topic.lower(), {})
    
    # If topic not found, try to find a similar topic or use a general approach
    if not topic_questions:
        # Try to find a similar topic or use a general category
        similar_topics = {
            "programming": "python",
            "coding": "python", 
            "computer science": "python",
            "cs": "python",
            "software": "python",
            "web": "javascript",
            "frontend": "javascript",
            "backend": "python",
            "data science": "python",
            "ai": "python",
            "machine learning": "python",
            "ml": "python",
            "physics": "science",
            "chemistry": "science",
            "biology": "science",
            "math": "mathematics",
            "calculus": "mathematics",
            "algebra": "mathematics",
            "statistics": "mathematics"
        }
        
        # Check for similar topics
        for key, value in similar_topics.items():
            if key in topic.lower():
                topic_questions = fallback_questions.get(value, {})
                break
        
        # If still no match, use python as default
        if not topic_questions:
            topic_questions = fallback_questions.get("python", {})
    
    difficulty_questions = topic_questions.get(difficulty.lower(), topic_questions.get("easy", []))
    
    # Return the requested number of questions (repeat if necessary)
    result = []
    for i in range(count):
        if difficulty_questions:
            result.append(difficulty_questions[i % len(difficulty_questions)])
        else:
            # Generate dynamic fallback questions based on the topic
            result.append(generate_dynamic_question(topic, difficulty, i+1))
    
    return result

def generate_dynamic_question(topic: str, difficulty: str, question_num: int) -> dict:
    """Generate a dynamic question for any topic"""
    
    # Define question templates based on topic categories
    programming_topics = ["programming", "coding", "computer science", "cs", "software", "web", "frontend", "backend", "data science", "ai", "machine learning", "ml", "python", "javascript", "java", "c++", "react", "node", "sql", "database"]
    science_topics = ["science", "physics", "chemistry", "biology", "medicine", "engineering", "environmental", "geology", "astronomy"]
    math_topics = ["math", "mathematics", "calculus", "algebra", "statistics", "geometry", "trigonometry", "linear algebra", "discrete"]
    
    # Determine the category
    topic_lower = topic.lower()
    if any(prog_topic in topic_lower for prog_topic in programming_topics):
        category = "programming"
    elif any(sci_topic in topic_lower for sci_topic in science_topics):
        category = "science"
    elif any(math_topic in topic_lower for math_topic in math_topics):
        category = "mathematics"
    else:
        category = "general"
    
    # Generate questions based on category and difficulty
    if category == "programming":
        if difficulty.lower() == "easy":
            questions = [
                {
                    "question": f"What is the time complexity of searching in a hash table for {topic}?",
                    "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                    "correct_answer": "O(1)",
                    "explanation": f"Hash tables provide average O(1) lookup time, making them efficient for {topic} applications."
                },
                {
                    "question": f"Which data structure is most suitable for implementing a LIFO stack in {topic}?",
                    "options": ["Array", "Linked List", "Queue", "Tree"],
                    "correct_answer": "Linked List",
                    "explanation": f"Linked lists allow efficient insertion and deletion at the top, making them ideal for stack operations in {topic}."
                },
                {
                    "question": f"What is the primary advantage of using recursion in {topic} programming?",
                    "options": ["Faster execution", "Simpler code for complex problems", "Less memory usage", "Better error handling"],
                    "correct_answer": "Simpler code for complex problems",
                    "explanation": f"Recursion simplifies the implementation of complex algorithms in {topic}, making code more readable and maintainable."
                }
            ]
        elif difficulty.lower() == "medium":
            questions = [
                {
                    "question": f"Which design pattern is most appropriate for creating objects in {topic} without specifying their exact classes?",
                    "options": ["Singleton", "Factory", "Observer", "Strategy"],
                    "correct_answer": "Factory",
                    "explanation": f"The Factory pattern encapsulates object creation logic, providing flexibility in {topic} applications."
                },
                {
                    "question": f"What is the time complexity of the following {topic} algorithm: for each element, search in the rest of the array?",
                    "options": ["O(n)", "O(n log n)", "O(n²)", "O(2ⁿ)"],
                    "correct_answer": "O(n²)",
                    "explanation": f"This nested loop approach in {topic} results in O(n²) time complexity due to the double iteration."
                },
                {
                    "question": f"Which principle is violated when a {topic} class has multiple responsibilities?",
                    "options": ["DRY", "SOLID", "KISS", "YAGNI"],
                    "correct_answer": "SOLID",
                    "explanation": f"Single Responsibility Principle (part of SOLID) states that a class should have only one reason to change in {topic} design."
                }
            ]
        else:  # hard
            questions = [
                {
                    "question": f"Which algorithm paradigm is most efficient for solving optimization problems in {topic}?",
                    "options": ["Greedy", "Dynamic Programming", "Backtracking", "Brute Force"],
                    "correct_answer": "Dynamic Programming",
                    "explanation": f"Dynamic Programming breaks down complex {topic} problems into overlapping subproblems, avoiding redundant calculations."
                },
                {
                    "question": f"What is the space complexity of a recursive implementation of binary search in {topic}?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                    "correct_answer": "O(log n)",
                    "explanation": f"Recursive binary search in {topic} uses O(log n) space due to the call stack depth being proportional to log n."
                },
                {
                    "question": f"Which concurrency model is most suitable for I/O-intensive {topic} applications?",
                    "options": ["Multi-threading", "Multi-processing", "Async/Await", "Event-driven"],
                    "correct_answer": "Async/Await",
                    "explanation": f"Async/await in {topic} allows non-blocking I/O operations, making it ideal for handling multiple concurrent requests efficiently."
                }
            ]
    
    elif category == "science":
        if difficulty.lower() == "easy":
            questions = [
                {
                    "question": f"What is the fundamental principle underlying {topic}?",
                    "options": ["Conservation of energy", "Law of conservation of mass", "Scientific method", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": f"These fundamental principles form the foundation of {topic} and guide scientific understanding."
                },
                {
                    "question": f"Which experimental approach is most reliable in {topic} research?",
                    "options": ["Single observation", "Controlled experiments", "Anecdotal evidence", "Intuition"],
                    "correct_answer": "Controlled experiments",
                    "explanation": f"Controlled experiments in {topic} eliminate confounding variables and provide reliable, reproducible results."
                }
            ]
        elif difficulty.lower() == "medium":
            questions = [
                {
                    "question": f"What is the relationship between theory and practice in {topic}?",
                    "options": ["Theory guides practice", "Practice validates theory", "Both are interdependent", "They are unrelated"],
                    "correct_answer": "Both are interdependent",
                    "explanation": f"In {topic}, theoretical understanding guides practical applications, while practical results validate and refine theoretical models."
                }
            ]
        else:  # hard
            questions = [
                {
                    "question": f"Which advanced concept is crucial for understanding complex phenomena in {topic}?",
                    "options": ["Basic principles", "Mathematical modeling", "Empirical observation", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": f"Advanced {topic} requires integration of fundamental principles, mathematical rigor, and empirical validation."
                }
            ]
    
    elif category == "mathematics":
        if difficulty.lower() == "easy":
            questions = [
                {
                    "question": f"What is the fundamental concept underlying {topic}?",
                    "options": ["Logical reasoning", "Pattern recognition", "Abstract thinking", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": f"{topic} requires logical reasoning, pattern recognition, and abstract thinking to solve complex problems."
                }
            ]
        elif difficulty.lower() == "medium":
            questions = [
                {
                    "question": f"Which approach is most effective for solving complex problems in {topic}?",
                    "options": ["Memorization", "Understanding principles", "Practice", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": f"Mastering {topic} requires understanding fundamental principles, regular practice, and building a strong foundation."
                }
            ]
        else:  # hard
            questions = [
                {
                    "question": f"What is the highest level of understanding required for advanced {topic}?",
                    "options": ["Computational", "Conceptual", "Creative", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": f"Advanced {topic} requires computational fluency, deep conceptual understanding, and creative problem-solving abilities."
                }
            ]
    
    else:  # general
        questions = [
            {
                "question": f"What is the most important aspect of learning {topic}?",
                "options": ["Memorization", "Understanding concepts", "Practice", "All of the above"],
                "correct_answer": "All of the above",
                "explanation": f"Effective learning of {topic} requires understanding fundamental concepts, regular practice, and building knowledge systematically."
            }
        ]
    
    # Return the appropriate question based on question number
    return questions[question_num % len(questions)]

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
    print(f"[AI] User {user_id} requesting {count} {difficulty} questions for topic: {topic}")
    
    try:
        if not model:
            print("[WARNING] Gemini API key not configured, using fallback questions")
            fallback_questions = get_fallback_questions(topic, difficulty, count)
            print(f"[FALLBACK] Using fallback questions: {len(fallback_questions)} questions")
            return fallback_questions
        
        print(f"[AI] Generating questions via Gemini AI for user {user_id}")
        
        # Create prompt for Gemini
        prompt = f"""
Generate {count} multiple-choice questions for the topic '{topic}' with a difficulty of '{difficulty}'.

IMPORTANT REQUIREMENTS:
1. Return ONLY a valid JSON object with this exact structure:
{{
  "questions": [
    {{
      "question": "Your question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Clear explanation of why this answer is correct"
    }}
  ]
}}

2. Each question must have exactly 4 options (A, B, C, D)
3. The correct_answer must match exactly one of the options
4. Include detailed explanations for each answer
5. Make questions relevant to the topic and appropriate for the difficulty level
6. Ensure questions are original and educational
7. DO NOT include any text outside the JSON object
8. DO NOT use markdown formatting or code blocks

Generate {count} questions now:
"""
        
        # Generate questions using Gemini
        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            # Clean the response text
            response_text = response.text.strip()
            print(f"[DEBUG] Raw Gemini response: {response_text[:200]}...")
            
            # Remove markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Clean up any remaining formatting
            response_text = response_text.strip()
            
            # Parse JSON
            payload = json.loads(response_text)
            
            # Extract questions array
            questions = payload.get("questions") if isinstance(payload, dict) else None
            if questions is None:
                # Fallback: accept top-level list
                if isinstance(payload, list):
                    questions = payload
                else:
                    raise ValueError("Response does not contain 'questions' array")
            
            # Validate questions structure
            if not isinstance(questions, list) or len(questions) == 0:
                raise ValueError("No valid questions found in response")
            
            # Validate each question
            for i, q in enumerate(questions):
                if not isinstance(q, dict):
                    raise ValueError(f"Question {i+1} is not a valid object")
                if "question" not in q:
                    raise ValueError(f"Question {i+1} missing 'question' field")
                if "options" not in q or not isinstance(q["options"], list) or len(q["options"]) != 4:
                    raise ValueError(f"Question {i+1} must have exactly 4 options")
                if "correct_answer" not in q:
                    raise ValueError(f"Question {i+1} missing 'correct_answer' field")
                if q["correct_answer"] not in q["options"]:
                    raise ValueError(f"Question {i+1} correct_answer must match one of the options")
            
            print(f"[AI] Generated {len(questions)} valid questions from Gemini AI")
            
            # Store questions in database
            await add_questions_to_db(topic, difficulty, questions)
            
            # Format questions for frontend
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    "question": q["question"],
                    "options": q["options"],
                    "answer": q["correct_answer"],
                    "explanation": q.get("explanation", "No explanation provided")
                })
            
            print(f"[OK] Successfully generated and stored {len(formatted_questions)} questions for user {user_id}")
            return formatted_questions
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parsing error: {str(e)}")
            print(f"[DEBUG] Raw response: {response_text}")
            # Try to provide fallback questions
            fallback_questions = get_fallback_questions(topic, difficulty, count)
            print(f"[RETRY] Using fallback questions: {len(fallback_questions)} questions")
            return fallback_questions
        except Exception as e:
            print(f"[ERROR] Error processing Gemini response: {str(e)}")
            # Try to provide fallback questions
            fallback_questions = get_fallback_questions(topic, difficulty, count)
            print(f"[RETRY] Using fallback questions: {len(fallback_questions)} questions")
            return fallback_questions
            
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