from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from ..db import get_db
from ..schemas.schemas import (
    AssessmentCreate, AssessmentResponse, QuestionCreate, QuestionResponse,
    CodingQuestionCreate, CodingQuestionResponse, CodingSubmission, CodingSubmissionResponse,
    AssessmentSubmission, AssessmentResult, LeaderboardEntry, AssessmentLeaderboard,
    StudentNotification, UserResponse, AssessmentSubmissionResponse, StudentAssessment
)
from ..dependencies import require_teacher, require_admin, require_teacher_or_admin, require_student
from ..dependencies import get_current_user
from ..models.models import UserModel
from .notifications import create_assessment_completion_notification
import os

router = APIRouter(tags=["assessments"])
security = HTTPBearer()

async def update_user_progress(db, user_id: str, score: int, percentage: float, total_questions: int):
    """Update user's gamification progress after completing an assessment"""
    try:
        # Get current user data
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            return
        
        # Calculate XP based on score and questions
        base_xp = 10  # Base XP for completing assessment
        score_xp = int(percentage * 0.5)  # XP based on percentage (0-50 XP)
        question_xp = total_questions * 2  # 2 XP per question
        total_xp = base_xp + score_xp + question_xp
        
        # Calculate new level (every 100 XP = 1 level)
        current_xp = user_doc.get("xp", 0)
        new_xp = current_xp + total_xp
        new_level = (new_xp // 100) + 1
        
        # Update streak (simplified - just increment if assessment completed)
        current_streak = user_doc.get("streak", 0)
        new_streak = current_streak + 1
        
        # Update longest streak
        current_longest_streak = user_doc.get("longest_streak", 0)
        new_longest_streak = max(current_longest_streak, new_streak)
        
        # Check for badges
        badges = user_doc.get("badges", [])
        new_badges = []
        
        # First assessment badge
        if "first_assessment" not in badges:
            new_badges.append("first_assessment")
        
        # High score badge (90%+)
        if percentage >= 90 and "high_scorer" not in badges:
            new_badges.append("high_scorer")
        
        # Streak badges
        if new_streak >= 5 and "consistent_learner" not in badges:
            new_badges.append("consistent_learner")
        
        # Level up badge
        old_level = (current_xp // 100) + 1
        if new_level > old_level and "level_up" not in badges:
            new_badges.append("level_up")
        
        # Update user document
        update_data = {
            "xp": new_xp,
            "level": new_level,
            "streak": new_streak,
            "longest_streak": new_longest_streak,
            "last_activity": datetime.utcnow(),
            "completed_assessments": user_doc.get("completed_assessments", 0) + 1,
            "total_questions_answered": user_doc.get("total_questions_answered", 0) + total_questions,
            "average_score": calculate_average_score(user_doc, percentage)
        }
        
        # Add new badges
        if new_badges:
            update_data["badges"] = badges + new_badges
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        print(f"[SUCCESS] [GAMIFICATION] Updated user {user_id}: +{total_xp} XP, Level {new_level}, Streak {new_streak}")
        if new_badges:
            print(f"[SUCCESS] [GAMIFICATION] New badges earned: {new_badges}")
            
    except Exception as e:
        print(f"[ERROR] [GAMIFICATION] Failed to update user progress: {str(e)}")

def calculate_average_score(user_doc: dict, new_percentage: float) -> float:
    """Calculate new average score"""
    current_avg = user_doc.get("average_score", 0)
    completed_count = user_doc.get("completed_assessments", 0)
    
    if completed_count == 0:
        return new_percentage
    else:
        # Weighted average
        return ((current_avg * completed_count) + new_percentage) / (completed_count + 1)

def generate_mcq_question(topic: str, difficulty: str, question_num: int):
    """Generate a realistic MCQ question based on topic and difficulty"""
    
    # Topic-specific question templates with more questions to avoid repetition
    topic_questions = {
        "array": [
            {
                "question": "What is the time complexity of finding an element in an unsorted array?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                "correct": 2,
                "explanation": "In an unsorted array, we need to check each element sequentially until we find the target, which takes O(n) time in the worst case."
            },
            {
                "question": "Which data structure is best for implementing a dynamic array?",
                "options": ["Linked List", "Hash Table", "Stack", "Vector/ArrayList"],
                "correct": 3,
                "explanation": "Vector or ArrayList provides dynamic resizing and random access, making it ideal for dynamic arrays."
            },
            {
                "question": "What is the space complexity of merging two sorted arrays?",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
                "correct": 1,
                "explanation": "Merging two sorted arrays requires additional space to store the merged result, which is O(n) where n is the total number of elements."
            },
            {
                "question": "What is the time complexity of binary search on a sorted array?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                "correct": 1,
                "explanation": "Binary search eliminates half of the search space in each iteration, resulting in O(log n) time complexity."
            },
            {
                "question": "Which operation has O(1) time complexity in an array?",
                "options": ["Search", "Insertion at end", "Deletion", "Sorting"],
                "correct": 1,
                "explanation": "Insertion at the end of an array (if space is available) takes O(1) time as it only requires updating the last index."
            },
            {
                "question": "What is the worst-case time complexity of insertion sort?",
                "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
                "correct": 2,
                "explanation": "Insertion sort has O(n²) worst-case time complexity when the array is in reverse order."
            },
            {
                "question": "Which algorithm is used to find the kth largest element in an array?",
                "options": ["Quick Sort", "Quick Select", "Merge Sort", "Heap Sort"],
                "correct": 1,
                "explanation": "Quick Select is an efficient algorithm to find the kth largest element with average O(n) time complexity."
            },
            {
                "question": "What is the space complexity of in-place sorting algorithms?",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
                "correct": 0,
                "explanation": "In-place sorting algorithms use only a constant amount of extra space, resulting in O(1) space complexity."
            }
        ],
        "string": [
            {
                "question": "What is the time complexity of string concatenation in Python?",
                "options": ["O(1)", "O(n)", "O(n²)", "O(log n)"],
                "correct": 1,
                "explanation": "String concatenation in Python creates a new string object, requiring O(n) time where n is the length of the resulting string."
            },
            {
                "question": "Which algorithm is most efficient for finding the longest common subsequence?",
                "options": ["Brute Force", "Dynamic Programming", "Greedy", "Divide and Conquer"],
                "correct": 1,
                "explanation": "Dynamic Programming solves LCS in O(mn) time, which is much more efficient than brute force O(2^n)."
            },
            {
                "question": "What is the time complexity of string comparison?",
                "options": ["O(1)", "O(n)", "O(n log n)", "O(n²)"],
                "correct": 1,
                "explanation": "String comparison requires checking each character, resulting in O(n) time complexity where n is the length of the shorter string."
            },
            {
                "question": "Which data structure is best for string pattern matching?",
                "options": ["Array", "Trie", "Hash Table", "Stack"],
                "correct": 1,
                "explanation": "Trie (prefix tree) is optimized for string operations and pattern matching, providing efficient prefix-based searches."
            },
            {
                "question": "What is the space complexity of the KMP algorithm?",
                "options": ["O(1)", "O(n)", "O(m)", "O(n + m)"],
                "correct": 3,
                "explanation": "KMP algorithm uses O(m) space for the failure function and O(n) for the text, resulting in O(n + m) total space complexity."
            },
            {
                "question": "Which algorithm is used for string compression?",
                "options": ["Quick Sort", "Huffman Coding", "Merge Sort", "Binary Search"],
                "correct": 1,
                "explanation": "Huffman Coding is a lossless data compression algorithm that uses variable-length codes for different characters."
            }
        ],
        "tree": [
            {
                "question": "What is the height of a balanced binary tree with n nodes?",
                "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
                "correct": 1,
                "explanation": "A balanced binary tree has height O(log n) because each level roughly doubles the number of nodes."
            },
            {
                "question": "Which traversal visits nodes in sorted order for a BST?",
                "options": ["Preorder", "Inorder", "Postorder", "Level order"],
                "correct": 1,
                "explanation": "Inorder traversal of a BST visits nodes in ascending order due to the BST property."
            },
            {
                "question": "What is the maximum number of nodes in a binary tree of height h?",
                "options": ["2^h", "2^h - 1", "2^(h+1) - 1", "h^2"],
                "correct": 2,
                "explanation": "A complete binary tree of height h has at most 2^(h+1) - 1 nodes."
            },
            {
                "question": "Which tree property ensures O(log n) search time?",
                "options": ["Complete", "Balanced", "Full", "Perfect"],
                "correct": 1,
                "explanation": "A balanced tree ensures that the height is O(log n), which guarantees O(log n) search time."
            },
            {
                "question": "What is the time complexity of inserting into a BST?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                "correct": 1,
                "explanation": "In a balanced BST, insertion takes O(log n) time as we traverse down the tree."
            },
            {
                "question": "Which data structure is used to implement a heap?",
                "options": ["Linked List", "Array", "Stack", "Queue"],
                "correct": 1,
                "explanation": "Heaps are typically implemented using arrays, where parent-child relationships are maintained through index calculations."
            }
        ],
        "graph": [
            {
                "question": "What is the time complexity of BFS on a graph with V vertices and E edges?",
                "options": ["O(V)", "O(E)", "O(V + E)", "O(V * E)"],
                "correct": 2,
                "explanation": "BFS visits each vertex once and each edge once, resulting in O(V + E) time complexity."
            },
            {
                "question": "Which algorithm finds the shortest path in a weighted graph with negative edges?",
                "options": ["Dijkstra", "Bellman-Ford", "Floyd-Warshall", "BFS"],
                "correct": 1,
                "explanation": "Bellman-Ford can handle negative edge weights, unlike Dijkstra's algorithm."
            },
            {
                "question": "What is the space complexity of DFS using recursion?",
                "options": ["O(1)", "O(V)", "O(E)", "O(V + E)"],
                "correct": 1,
                "explanation": "DFS recursion uses O(V) space for the call stack in the worst case (linear graph)."
            },
            {
                "question": "Which algorithm finds all shortest paths between all pairs of vertices?",
                "options": ["Dijkstra", "Bellman-Ford", "Floyd-Warshall", "BFS"],
                "correct": 2,
                "explanation": "Floyd-Warshall algorithm finds shortest paths between all pairs of vertices in O(V³) time."
            },
            {
                "question": "What is the time complexity of finding cycles in a directed graph using DFS?",
                "options": ["O(V)", "O(E)", "O(V + E)", "O(V * E)"],
                "correct": 2,
                "explanation": "Cycle detection using DFS visits each vertex and edge once, resulting in O(V + E) time complexity."
            },
            {
                "question": "Which data structure is most efficient for representing a sparse graph?",
                "options": ["Adjacency Matrix", "Adjacency List", "Edge List", "Hash Table"],
                "correct": 1,
                "explanation": "Adjacency List is more space-efficient for sparse graphs as it only stores existing edges."
            }
        ],
        "sorting": [
            {
                "question": "Which sorting algorithm has the best average-case time complexity?",
                "options": ["Bubble Sort", "Quick Sort", "Selection Sort", "Insertion Sort"],
                "correct": 1,
                "explanation": "Quick Sort has O(n log n) average-case time complexity, which is optimal for comparison-based sorting."
            },
            {
                "question": "What is the space complexity of Merge Sort?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                "correct": 2,
                "explanation": "Merge Sort requires O(n) additional space to store the merged arrays during the sorting process."
            },
            {
                "question": "Which sorting algorithm is stable?",
                "options": ["Quick Sort", "Heap Sort", "Merge Sort", "Selection Sort"],
                "correct": 2,
                "explanation": "Merge Sort is stable because it preserves the relative order of equal elements during the merge process."
            },
            {
                "question": "What is the worst-case time complexity of Quick Sort?",
                "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
                "correct": 2,
                "explanation": "Quick Sort has O(n²) worst-case time complexity when the pivot is always the smallest or largest element."
            },
            {
                "question": "Which sorting algorithm is in-place?",
                "options": ["Merge Sort", "Quick Sort", "Counting Sort", "Radix Sort"],
                "correct": 1,
                "explanation": "Quick Sort is in-place as it sorts the array by swapping elements within the same array."
            },
            {
                "question": "What is the time complexity of Heap Sort?",
                "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
                "correct": 1,
                "explanation": "Heap Sort has O(n log n) time complexity for both average and worst cases."
            }
        ]
    }
    
    # Get questions for the topic, or use a default set
    questions = topic_questions.get(topic.lower(), topic_questions["array"])
    
    # Use a combination of question number, topic, and timestamp to ensure variety
    import random
    from datetime import datetime
    random.seed(hash(f"{topic}_{question_num}_{datetime.utcnow().timestamp()}"))
    
    # Ensure we don't repeat questions by tracking used indices
    if not hasattr(generate_mcq_question, '_used_indices'):
        generate_mcq_question._used_indices = set()
    
    available_indices = [i for i in range(len(questions)) if i not in generate_mcq_question._used_indices]
    if not available_indices:
        # Reset if all questions used
        generate_mcq_question._used_indices.clear()
        available_indices = list(range(len(questions)))
    
    selected_idx = random.choice(available_indices)
    generate_mcq_question._used_indices.add(selected_idx)
    selected_question = questions[selected_idx]
    
    return {
        "type": "mcq",
        "question": selected_question["question"],
        "options": selected_question["options"],
        "correct_answer": selected_question["correct"],
        "explanation": selected_question["explanation"],
        "points": 1,
        "created_at": datetime.utcnow()
    }

def generate_coding_question(topic: str, difficulty: str, question_num: int):
    """Generate a realistic coding question based on topic and difficulty"""
    
    # Topic-specific coding problems
    topic_problems = {
        "array": [
            {
                "title": "Two Sum",
                "description": "Find two numbers in an array that add up to a target value.",
                "problem_statement": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nYou can return the answer in any order.",
                "constraints": [
                    "2 <= nums.length <= 10^4",
                    "-10^9 <= nums[i] <= 10^9",
                    "-10^9 <= target <= 10^9",
                    "Only one valid answer exists."
                ],
                "examples": [
                    {
                        "input": "nums = [2,7,11,15], target = 9",
                        "output": "[0,1]",
                        "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                    }
                ],
                "test_cases": [
                    {"input": "[2,7,11,15]\n9", "expected_output": "[0,1]", "is_hidden": False},
                    {"input": "[3,2,4]\n6", "expected_output": "[1,2]", "is_hidden": False},
                    {"input": "[3,3]\n6", "expected_output": "[0,1]", "is_hidden": True}
                ],
                "hints": [
                    "Use a hash map to store numbers and their indices",
                    "For each number, check if target - number exists in the map"
                ]
            },
            {
                "title": "Maximum Subarray",
                "description": "Find the contiguous subarray with maximum sum.",
                "problem_statement": "Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.\n\nA subarray is a contiguous part of an array.",
                "constraints": [
                    "1 <= nums.length <= 10^5",
                    "-10^4 <= nums[i] <= 10^4"
                ],
                "examples": [
                    {
                        "input": "nums = [-2,1,-3,4,-1,2,1,-5,4]",
                        "output": "6",
                        "explanation": "The subarray [4,-1,2,1] has the largest sum 6."
                    }
                ],
                "test_cases": [
                    {"input": "[-2,1,-3,4,-1,2,1,-5,4]", "expected_output": "6", "is_hidden": False},
                    {"input": "[1]", "expected_output": "1", "is_hidden": False},
                    {"input": "[5,4,-1,7,8]", "expected_output": "23", "is_hidden": True}
                ],
                "hints": [
                    "Use Kadane's algorithm",
                    "Keep track of the maximum sum ending at each position"
                ]
            },
            {
                "title": "Rotate Array",
                "description": "Rotate an array to the right by k steps.",
                "problem_statement": "Given an integer array nums, rotate the array to the right by k steps, where k is non-negative.",
                "constraints": [
                    "1 <= nums.length <= 10^5",
                    "-2^31 <= nums[i] <= 2^31 - 1",
                    "0 <= k <= 10^5"
                ],
                "examples": [
                    {
                        "input": "nums = [1,2,3,4,5,6,7], k = 3",
                        "output": "[5,6,7,1,2,3,4]",
                        "explanation": "rotate 1 steps to the right: [7,1,2,3,4,5,6]\nrotate 2 steps to the right: [6,7,1,2,3,4,5]\nrotate 3 steps to the right: [5,6,7,1,2,3,4]"
                    }
                ],
                "test_cases": [
                    {"input": "[1,2,3,4,5,6,7]\n3", "expected_output": "[5,6,7,1,2,3,4]", "is_hidden": False},
                    {"input": "[-1,-100,3,99]\n2", "expected_output": "[3,99,-1,-100]", "is_hidden": False},
                    {"input": "[1,2]\n3", "expected_output": "[2,1]", "is_hidden": True}
                ],
                "hints": [
                    "Reverse the entire array, then reverse the first k elements, then reverse the remaining elements",
                    "Use the fact that rotating by k is equivalent to rotating by k % n"
                ]
            },
            {
                "title": "Product of Array Except Self",
                "description": "Return an array where each element is the product of all other elements.",
                "problem_statement": "Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].\n\nThe product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.\n\nYou must write an algorithm that runs in O(n) time and without using the division operator.",
                "constraints": [
                    "2 <= nums.length <= 10^5",
                    "-30 <= nums[i] <= 30",
                    "The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer."
                ],
                "examples": [
                    {
                        "input": "nums = [1,2,3,4]",
                        "output": "[24,12,8,6]",
                        "explanation": "For index 0: 2*3*4 = 24\nFor index 1: 1*3*4 = 12\nFor index 2: 1*2*4 = 8\nFor index 3: 1*2*3 = 6"
                    }
                ],
                "test_cases": [
                    {"input": "[1,2,3,4]", "expected_output": "[24,12,8,6]", "is_hidden": False},
                    {"input": "[-1,1,0,-3,3]", "expected_output": "[0,0,9,0,0]", "is_hidden": False},
                    {"input": "[2,3,4,5]", "expected_output": "[60,40,30,24]", "is_hidden": True}
                ],
                "hints": [
                    "Use two passes: first pass to calculate left products, second pass to calculate right products",
                    "The result at index i is left[i] * right[i]"
                ]
            }
        ],
        "string": [
            {
                "title": "Valid Parentheses",
                "description": "Check if a string has valid parentheses.",
                "problem_statement": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.",
                "constraints": [
                    "1 <= s.length <= 10^4",
                    "s consists of parentheses only '()[]{}'."
                ],
                "examples": [
                    {
                        "input": "s = \"()\"",
                        "output": "true",
                        "explanation": "The string has valid parentheses."
                    }
                ],
                "test_cases": [
                    {"input": "\"()\"", "expected_output": "true", "is_hidden": False},
                    {"input": "\"()[]{}\"", "expected_output": "true", "is_hidden": False},
                    {"input": "\"(]\"", "expected_output": "false", "is_hidden": True}
                ],
                "hints": [
                    "Use a stack to keep track of opening brackets",
                    "When you see a closing bracket, check if it matches the top of the stack"
                ]
            },
            {
                "title": "Longest Substring Without Repeating Characters",
                "description": "Find the length of the longest substring without repeating characters.",
                "problem_statement": "Given a string s, find the length of the longest substring without repeating characters.",
                "constraints": [
                    "0 <= s.length <= 5 * 10^4",
                    "s consists of English letters, digits, symbols and spaces."
                ],
                "examples": [
                    {
                        "input": "s = \"abcabcbb\"",
                        "output": "3",
                        "explanation": "The answer is \"abc\", with the length of 3."
                    }
                ],
                "test_cases": [
                    {"input": "\"abcabcbb\"", "expected_output": "3", "is_hidden": False},
                    {"input": "\"bbbbb\"", "expected_output": "1", "is_hidden": False},
                    {"input": "\"pwwkew\"", "expected_output": "3", "is_hidden": True}
                ],
                "hints": [
                    "Use sliding window technique with two pointers",
                    "Keep track of characters in the current window using a set or hash map"
                ]
            },
            {
                "title": "Longest Palindromic Substring",
                "description": "Find the longest palindromic substring in a string.",
                "problem_statement": "Given a string s, return the longest palindromic substring in s.",
                "constraints": [
                    "1 <= s.length <= 1000",
                    "s consist of only digits and English letters."
                ],
                "examples": [
                    {
                        "input": "s = \"babad\"",
                        "output": "\"bab\"",
                        "explanation": "\"aba\" is also a valid answer."
                    }
                ],
                "test_cases": [
                    {"input": "\"babad\"", "expected_output": "\"bab\"", "is_hidden": False},
                    {"input": "\"cbbd\"", "expected_output": "\"bb\"", "is_hidden": False},
                    {"input": "\"a\"", "expected_output": "\"a\"", "is_hidden": True}
                ],
                "hints": [
                    "Expand around centers - check both odd and even length palindromes",
                    "For each center, expand outward while characters match"
                ]
            }
        ],
        "tree": [
            {
                "title": "Maximum Depth of Binary Tree",
                "description": "Find the maximum depth of a binary tree.",
                "problem_statement": "Given the root of a binary tree, return its maximum depth.\n\nA binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.",
                "constraints": [
                    "The number of nodes in the tree is in the range [0, 10^4].",
                    "-100 <= Node.val <= 100"
                ],
                "examples": [
                    {
                        "input": "root = [3,9,20,null,null,15,7]",
                        "output": "3",
                        "explanation": "The tree has a maximum depth of 3."
                    }
                ],
                "test_cases": [
                    {"input": "[3,9,20,null,null,15,7]", "expected_output": "3", "is_hidden": False},
                    {"input": "[1,null,2]", "expected_output": "2", "is_hidden": False},
                    {"input": "[]", "expected_output": "0", "is_hidden": True}
                ],
                "hints": [
                    "Use recursion to traverse the tree",
                    "Return 1 + max depth of left and right subtrees"
                ]
            },
            {
                "title": "Binary Tree Inorder Traversal",
                "description": "Return the inorder traversal of a binary tree.",
                "problem_statement": "Given the root of a binary tree, return the inorder traversal of its nodes' values.",
                "constraints": [
                    "The number of nodes in the tree is in the range [0, 100].",
                    "-100 <= Node.val <= 100"
                ],
                "examples": [
                    {
                        "input": "root = [1,null,2,3]",
                        "output": "[1,3,2]",
                        "explanation": "Inorder traversal: left -> root -> right"
                    }
                ],
                "test_cases": [
                    {"input": "[1,null,2,3]", "expected_output": "[1,3,2]", "is_hidden": False},
                    {"input": "[]", "expected_output": "[]", "is_hidden": False},
                    {"input": "[1]", "expected_output": "[1]", "is_hidden": True}
                ],
                "hints": [
                    "Use recursion: visit left subtree, then root, then right subtree",
                    "For iterative solution, use a stack to simulate recursion"
                ]
            },
            {
                "title": "Symmetric Tree",
                "description": "Check if a binary tree is symmetric.",
                "problem_statement": "Given the root of a binary tree, check whether it is a mirror of itself (i.e., symmetric around its center).",
                "constraints": [
                    "The number of nodes in the tree is in the range [1, 1000].",
                    "-100 <= Node.val <= 100"
                ],
                "examples": [
                    {
                        "input": "root = [1,2,2,3,4,4,3]",
                        "output": "true",
                        "explanation": "The tree is symmetric around its center."
                    }
                ],
                "test_cases": [
                    {"input": "[1,2,2,3,4,4,3]", "expected_output": "true", "is_hidden": False},
                    {"input": "[1,2,2,null,3,null,3]", "expected_output": "false", "is_hidden": False},
                    {"input": "[1]", "expected_output": "true", "is_hidden": True}
                ],
                "hints": [
                    "Compare left and right subtrees recursively",
                    "Two trees are symmetric if their left and right children are symmetric"
                ]
            }
        ]
    }
    
    # Get problems for the topic, or use array problems as default
    problems = topic_problems.get(topic.lower(), topic_problems["array"])
    
    # Use a combination of question number and topic to ensure variety
    import random
    random.seed(hash(f"{topic}_coding_{question_num}"))
    selected_problem = random.choice(problems)
    
    return {
        "type": "coding",
        "title": selected_problem["title"],
        "description": selected_problem["description"],
        "problem_statement": selected_problem["problem_statement"],
        "constraints": selected_problem["constraints"],
        "examples": selected_problem["examples"],
        "test_cases": selected_problem["test_cases"],
        "hints": selected_problem["hints"],
        "points": 10,
        "time_limit": 30,
        "memory_limit": 128,
        "created_at": datetime.utcnow()
    }

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# Assessment Management Endpoints

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(assessment_data: AssessmentCreate, user: UserModel = Depends(require_teacher)):
    """Create a new assessment - Teacher/Admin only"""
    try:
        db = await get_db()
        
        assessment_doc = {
            "title": assessment_data.title,
            "subject": assessment_data.subject,
            "difficulty": assessment_data.difficulty,
            "description": assessment_data.description,
            "time_limit": assessment_data.time_limit,
            "max_attempts": assessment_data.max_attempts,
            "type": assessment_data.type,
            "created_by": str(user.id),
            "created_at": datetime.utcnow(),
            "status": "draft",
            "question_count": len(assessment_data.questions),
            "questions": assessment_data.questions,
            "assigned_batches": assessment_data.batches,
            "is_active": False
        }
        
        result = await db.assessments.insert_one(assessment_doc)
        assessment_id = str(result.inserted_id)
        
        # Generate questions if assessment type is AI-generated
        if assessment_data.type == "ai" and len(assessment_data.questions) == 0:
            try:
                from app.services.gemini_coding_service import GeminiCodingService
                gemini_service = GeminiCodingService()
                
                # Generate questions based on topic and difficulty
                generated_questions = await gemini_service.generate_mcq_questions(
                    topic=assessment_data.subject,
                    difficulty=assessment_data.difficulty,
                    count=10  # Default count, can be made configurable
                )
                
                # Update assessment with generated questions
                await db.assessments.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {
                        "questions": generated_questions,
                        "question_count": len(generated_questions),
                        "is_active": True,
                        "status": "active"
                    }}
                )
                
                # Send notifications to students in selected batches
                await send_assessment_notifications(db, assessment_id, assessment_data.batches, assessment_data.title)
                
            except Exception as e:
                print(f"❌ [ASSESSMENT] Error generating questions: {str(e)}")
                # Continue with empty questions if generation fails
        
        return AssessmentResponse(
            id=assessment_id,
            title=assessment_data.title,
            subject=assessment_data.subject,
            difficulty=assessment_data.difficulty,
            description=assessment_data.description,
            time_limit=assessment_data.time_limit,
            max_attempts=assessment_data.max_attempts,
            question_count=len(assessment_data.questions),
            created_by=str(user.id),
            created_at=assessment_doc["created_at"].isoformat(),
            status="active" if assessment_data.type == "ai" else "draft",
            type=assessment_doc["type"],
            is_active=True if assessment_data.type == "ai" else False,
            total_questions=len(assessment_data.questions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AssessmentResponse])
async def get_teacher_assessments(user: UserModel = Depends(get_current_user)):
    """Get all assessments created by the current teacher across sources (manual and teacher-created)."""
    try:
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can view assessments")
        
        # Regular (manual) assessments authored by teacher
        manual_list = await db.assessments.find({"created_by": str(user.id)}).to_list(length=None)

        # Teacher-created (AI/generated) assessments
        teacher_list = []
        try:
            teacher_list = await db.teacher_assessments.find({"teacher_id": user.id}).to_list(length=None)
        except Exception:
            teacher_list = []

        combined: List[AssessmentResponse] = []

        for a in manual_list:
            combined.append(AssessmentResponse(
                id=str(a.get("_id")),
                title=a.get("title", a.get("subject", "Untitled Assessment")),
                subject=a.get("subject"),
                difficulty=a.get("difficulty", "medium"),
                description=a.get("description"),
                time_limit=a.get("time_limit"),
                max_attempts=a.get("max_attempts", 1),
                question_count=a.get("question_count", len(a.get("questions", []))),
                created_by=str(a.get("created_by")),
                created_at=(a.get("created_at") or datetime.utcnow()).isoformat(),
                status=a.get("status", "draft"),
                type=a.get("type", "mcq"),
                is_active=a.get("is_active", False),
                total_questions=a.get("question_count", len(a.get("questions", [])))
            ))

        for a in teacher_list:
            combined.append(AssessmentResponse(
                id=str(a.get("_id")),
                title=a.get("title", a.get("topic", "Untitled Assessment")),
                subject=a.get("topic", a.get("subject")),
                difficulty=a.get("difficulty", "medium"),
                description=f"Teacher-created assessment on {a.get('topic', a.get('subject', 'General'))}",
                time_limit=30,
                max_attempts=1,
                question_count=a.get("question_count", len(a.get("questions", []))),
                created_by=str(a.get("teacher_id", user.id)),
                created_at=(a.get("created_at") or datetime.utcnow()).isoformat(),
                status=a.get("status", "published"),
                type=a.get("type", "teacher"),
                is_active=a.get("is_active", True),
                total_questions=a.get("question_count", len(a.get("questions", [])))
            ))

        # Sort newest first
        combined.sort(key=lambda x: x.created_at or "", reverse=True)
        return combined
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/class-performance")
async def get_class_performance_overview(user: UserModel = Depends(require_teacher)):
    """Get class performance overview for all students - Teacher only"""
    try:
        db = await get_db()
        
        # Get all students
        students = await db.users.find({"role": "student"}).to_list(length=None)
        
        class_performance = []
        total_students = len(students)
        
        for student in students:
            student_id = str(student["_id"])
            
            # Get student's assessment results
            all_results = []
            
            # Regular assessments
            regular_submissions = await db.assessment_submissions.find({"student_id": student_id}).to_list(length=None)
            for submission in regular_submissions:
                assessment = await db.assessments.find_one({"_id": ObjectId(submission["assessment_id"])})
                if assessment:
                    all_results.append({
                        "score": submission.get("score", 0),
                        "total": submission.get("total_questions", 0),
                        "percentage": submission.get("percentage", 0),
                        "subject": assessment.get("subject", ""),
                        "submitted_at": submission.get("submitted_at")
                    })
            
            # Teacher assessments
            teacher_submissions = await db.teacher_assessment_results.find({"student_id": student_id}).to_list(length=None)
            for submission in teacher_submissions:
                assessment_id = submission.get("assessment_id")
                assessment = None
                if assessment_id:
                    try:
                        assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
                    except Exception:
                        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
                
                if assessment:
                    all_results.append({
                        "score": submission.get("score", 0),
                        "total": submission.get("total_questions", 0),
                        "percentage": submission.get("percentage", 0),
                        "subject": assessment.get("topic", assessment.get("subject", "")),
                        "submitted_at": submission.get("submitted_at")
                    })
            
            # AI assessments
            ai_results = await db.results.find({"user_id": student_id}).to_list(length=None)
            for result in ai_results:
                all_results.append({
                    "score": result.get("score", 0),
                    "total": result.get("total_questions", 0),
                    "percentage": (result.get("score", 0) / result.get("total_questions", 1)) * 100,
                    "subject": result.get("topic", ""),
                    "submitted_at": result.get("submitted_at")
                })
            
            # Calculate performance metrics
            total_assessments = len(all_results)
            if total_assessments > 0:
                average_score = sum([r["percentage"] for r in all_results]) / total_assessments
                recent_scores = [r["percentage"] for r in sorted(all_results, key=lambda x: x.get("submitted_at", datetime.min), reverse=True)[:5]]
                recent_average = sum(recent_scores) / len(recent_scores) if recent_scores else 0
                
                # Subject breakdown
                subjects = {}
                for result in all_results:
                    subject = result.get("subject", "Unknown")
                    if subject not in subjects:
                        subjects[subject] = []
                    subjects[subject].append(result["percentage"])
                
                subject_averages = {}
                for subject, scores in subjects.items():
                    subject_averages[subject] = sum(scores) / len(scores)
                
                class_performance.append({
                    "student_id": student_id,
                    "student_name": student.get("name") or student.get("username", ""),
                    "student_email": student.get("email", ""),
                    "batch": student.get("batch_name", ""),
                    "batch_id": student.get("batch_id", ""),
                    "total_assessments": total_assessments,
                    "average_score": round(average_score, 2),
                    "recent_average": round(recent_average, 2),
                    "subject_averages": subject_averages,
                    "last_activity": max([r.get("submitted_at", datetime.min) for r in all_results]) if all_results else None,
                    "performance_trend": "improving" if recent_average > average_score else "declining" if recent_average < average_score else "stable"
                })
        
        # Sort by average score (highest first)
        class_performance.sort(key=lambda x: x["average_score"], reverse=True)
        
        # Calculate class statistics
        if class_performance:
            class_average = sum([s["average_score"] for s in class_performance]) / len(class_performance)
            top_performers = class_performance[:3]
            struggling_students = [s for s in class_performance if s["average_score"] < 60]
        else:
            class_average = 0
            top_performers = []
            struggling_students = []
        
        return {
            "success": True,
            "class_statistics": {
                "total_students": total_students,
                "class_average": round(class_average, 2),
                "top_performers": top_performers,
                "struggling_students": struggling_students,
                "students_with_recent_activity": len([s for s in class_performance if s.get("last_activity") and (datetime.utcnow() - s["last_activity"]).days <= 7])
            },
            "student_performance": class_performance
        }
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching class performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/student-results/{student_id}")
async def get_student_detailed_results(
    student_id: str, 
    user: UserModel = Depends(require_teacher)
):
    """Get detailed results for a specific student across all assessments - Teacher only"""
    try:
        db = await get_db()
        
        # Get student info
        student = None
        try:
            if ObjectId.is_valid(student_id):
                student = await db.users.find_one({"_id": ObjectId(student_id)})
        except Exception:
            pass
        if not student:
            student = await db.users.find_one({"_id": student_id})
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get all assessment results for this student
        all_results = []
        
        # 1. Regular assessment submissions
        regular_submissions = await db.assessment_submissions.find({"student_id": student_id}).sort("submitted_at", -1).to_list(length=None)
        for submission in regular_submissions:
            assessment = await db.assessments.find_one({"_id": ObjectId(submission["assessment_id"])})
            if assessment:
                all_results.append({
                    "result_id": str(submission["_id"]),
                    "assessment_id": str(submission["assessment_id"]),
                    "assessment_title": assessment.get("title", "Assessment"),
                    "assessment_type": "regular",
                    "subject": assessment.get("subject", ""),
                    "difficulty": assessment.get("difficulty", "medium"),
                    "score": submission.get("score", 0),
                    "total_questions": submission.get("total_questions", 0),
                    "percentage": submission.get("percentage", 0),
                    "time_taken": submission.get("time_taken", 0),
                    "submitted_at": submission.get("submitted_at"),
                    "questions": submission.get("questions", []),
                    "user_answers": submission.get("answers", []),
                    "is_completed": True
                })
        
        # 2. Teacher assessment results
        teacher_submissions = await db.teacher_assessment_results.find({"student_id": student_id}).sort("submitted_at", -1).to_list(length=None)
        for submission in teacher_submissions:
            assessment_id = submission.get("assessment_id")
            assessment = None
            if assessment_id:
                try:
                    assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
                except Exception:
                    # Also try string _id form for seed/test data
                    assessment = await db.teacher_assessments.find_one({"_id": assessment_id}) or await db.assessments.find_one({"_id": ObjectId(assessment_id)})
                if not assessment:
                    # Final fallback: string lookup in regular assessments
                    assessment = await db.assessments.find_one({"_id": assessment_id})
            
            if assessment:
                all_results.append({
                    "result_id": str(submission["_id"]),
                    "assessment_id": str(assessment_id),
                    "assessment_title": assessment.get("title", "Assessment"),
                    "assessment_type": "teacher_assigned",
                    "subject": assessment.get("topic", assessment.get("subject", "")),
                    "difficulty": assessment.get("difficulty", "medium"),
                    "score": submission.get("score", 0),
                    "total_questions": submission.get("total_questions", 0),
                    "percentage": submission.get("percentage", 0),
                    "time_taken": submission.get("time_taken", 0),
                    "submitted_at": submission.get("submitted_at"),
                    "questions": submission.get("questions", []),
                    "user_answers": submission.get("user_answers", []),
                    "is_completed": True
                })
        
        # 3. AI-generated assessment results
        ai_results = await db.results.find({"user_id": student_id}).sort("submitted_at", -1).to_list(length=None)
        for result in ai_results:
            all_results.append({
                "result_id": str(result["_id"]),
                "assessment_id": "ai_generated",
                "assessment_title": result.get("test_name", "AI Assessment"),
                "assessment_type": "ai_generated",
                "subject": result.get("topic", ""),
                "difficulty": result.get("difficulty", "medium"),
                "score": result.get("score", 0),
                "total_questions": result.get("total_questions", 0),
                "percentage": (result.get("score", 0) / result.get("total_questions", 1)) * 100,
                "time_taken": result.get("time_spent", 0),
                "submitted_at": result.get("submitted_at"),
                "questions": result.get("questions", []),
                "user_answers": result.get("user_answers", []),
                "is_completed": True
            })
        
        # 4. Coding assessment results
        coding_results = await db.coding_solutions.find({"student_id": student_id}).sort("submitted_at", -1).to_list(length=None)
        for result in coding_results:
            problem = await db.coding_problems.find_one({"_id": ObjectId(result["problem_id"])})
            if problem:
                all_results.append({
                    "result_id": str(result["_id"]),
                    "assessment_id": str(result["problem_id"]),
                    "assessment_title": problem.get("title", "Coding Problem"),
                    "assessment_type": "coding",
                    "subject": "Programming",
                    "difficulty": problem.get("difficulty", "medium"),
                    "score": result.get("score", 0),
                    "total_questions": 1,  # Coding problems are typically single problems
                    "percentage": (result.get("score", 0) / result.get("max_score", 1)) * 100,
                    "time_taken": result.get("execution_time", 0),
                    "submitted_at": result.get("submitted_at"),
                    "code": result.get("code", ""),
                    "language": result.get("language", ""),
                    "test_results": result.get("test_results", []),
                    "is_completed": True
                })
        
        # Sort by submission date (most recent first)
        all_results.sort(key=lambda x: x.get("submitted_at", datetime.min), reverse=True)
        
        # Calculate performance insights
        total_assessments = len(all_results)
        completed_assessments = len([r for r in all_results if r.get("is_completed", False)])
        average_score = sum([r.get("percentage", 0) for r in all_results]) / total_assessments if total_assessments > 0 else 0
        
        # Subject-wise performance
        subject_performance = {}
        for result in all_results:
            subject = result.get("subject", "Unknown")
            if subject not in subject_performance:
                subject_performance[subject] = {"total": 0, "scores": [], "count": 0}
            subject_performance[subject]["count"] += 1
            subject_performance[subject]["scores"].append(result.get("percentage", 0))
            subject_performance[subject]["total"] += result.get("percentage", 0)
        
        # Calculate averages for each subject
        for subject in subject_performance:
            subject_performance[subject]["average"] = subject_performance[subject]["total"] / subject_performance[subject]["count"]
        
        return {
            "success": True,
            "student": {
                "id": str(student["_id"]),
                "name": student.get("name") or student.get("username", ""),
                "email": student.get("email", ""),
                "batch": student.get("batch_name", ""),
                "batch_id": student.get("batch_id", "")
            },
            "results": all_results,
            "performance_insights": {
                "total_assessments": total_assessments,
                "completed_assessments": completed_assessments,
                "average_score": round(average_score, 2),
                "subject_performance": subject_performance,
                "recent_activity": all_results[:5]  # Last 5 assessments
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching student results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/assessment-analytics/{assessment_id}")
async def get_assessment_analytics(
    assessment_id: str, 
    user: UserModel = Depends(require_teacher)
):
    """Get detailed analytics for a specific assessment - Teacher only"""
    try:
        db = await get_db()
        
        # Get assessment details
        assessment = None
        try:
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        except Exception:
            pass
        
        if not assessment:
            assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get all submissions for this assessment
        all_submissions = []
        
        # Regular assessment submissions
        regular_submissions = await db.assessment_submissions.find({"assessment_id": assessment_id}).to_list(length=None)
        for submission in regular_submissions:
            student = await db.users.find_one({"_id": ObjectId(submission["student_id"])})
            if student:
                all_submissions.append({
                    "student_id": str(submission["student_id"]),
                    "student_name": student.get("name") or student.get("username", ""),
                    "student_email": student.get("email", ""),
                    "batch": student.get("batch_name", ""),
                    "score": submission.get("score", 0),
                    "total_questions": submission.get("total_questions", 0),
                    "percentage": submission.get("percentage", 0),
                    "time_taken": submission.get("time_taken", 0),
                    "submitted_at": submission.get("submitted_at"),
                    "answers": submission.get("answers", []),
                    "questions": submission.get("questions", [])
                })
        
        # Teacher assessment results
        teacher_submissions = await db.teacher_assessment_results.find({"assessment_id": assessment_id}).to_list(length=None)
        for submission in teacher_submissions:
            student = await db.users.find_one({"_id": ObjectId(submission["student_id"])})
            if student:
                all_submissions.append({
                    "student_id": str(submission["student_id"]),
                    "student_name": student.get("name") or student.get("username", ""),
                    "student_email": student.get("email", ""),
                    "batch": student.get("batch_name", ""),
                    "score": submission.get("score", 0),
                    "total_questions": submission.get("total_questions", 0),
                    "percentage": submission.get("percentage", 0),
                    "time_taken": submission.get("time_taken", 0),
                    "submitted_at": submission.get("submitted_at"),
                    "answers": submission.get("user_answers", []),
                    "questions": submission.get("questions", [])
                })
        
        if not all_submissions:
            return {
                "success": True,
                "assessment": {
                    "id": str(assessment["_id"]),
                    "title": assessment.get("title", "Assessment"),
                    "subject": assessment.get("topic", assessment.get("subject", "")),
                    "difficulty": assessment.get("difficulty", "medium"),
                    "total_questions": len(assessment.get("questions", []))
                },
                "analytics": {
                    "total_submissions": 0,
                    "average_score": 0,
                    "completion_rate": 0,
                    "question_analysis": [],
                    "batch_performance": {},
                    "time_analysis": {}
                },
                "submissions": []
            }
        
        # Calculate analytics
        total_submissions = len(all_submissions)
        average_score = sum([s["percentage"] for s in all_submissions]) / total_submissions
        
        # Question-wise analysis
        questions = assessment.get("questions", [])
        question_analysis = []
        for i, question in enumerate(questions):
            correct_count = 0
            total_attempts = 0
            
            for submission in all_submissions:
                if i < len(submission.get("answers", [])):
                    total_attempts += 1
                    user_answer = submission["answers"][i]
                    correct_answer = question.get("answer", "")
                    correct_answer_index = question.get("correct_answer", -1)
                    
                    # Handle different answer formats
                    if isinstance(correct_answer_index, int) and 0 <= correct_answer_index < len(question.get("options", [])):
                        correct_answer = question["options"][correct_answer_index]
                    
                    if user_answer == correct_answer:
                        correct_count += 1
            
            accuracy = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
            question_analysis.append({
                "question_index": i,
                "question_text": question.get("question", ""),
                "correct_answer": correct_answer,
                "total_attempts": total_attempts,
                "correct_attempts": correct_count,
                "accuracy": round(accuracy, 2),
                "difficulty_level": "easy" if accuracy >= 80 else "medium" if accuracy >= 60 else "hard"
            })
        
        # Batch-wise performance
        batch_performance = {}
        for submission in all_submissions:
            batch = submission.get("batch", "No Batch")
            if batch not in batch_performance:
                batch_performance[batch] = {"scores": [], "count": 0}
            batch_performance[batch]["scores"].append(submission["percentage"])
            batch_performance[batch]["count"] += 1
        
        for batch in batch_performance:
            scores = batch_performance[batch]["scores"]
            batch_performance[batch]["average"] = sum(scores) / len(scores)
            batch_performance[batch]["highest"] = max(scores)
            batch_performance[batch]["lowest"] = min(scores)
        
        # Time analysis
        time_taken = [s["time_taken"] for s in all_submissions if s["time_taken"] > 0]
        time_analysis = {}
        if time_taken:
            time_analysis = {
                "average_time": sum(time_taken) / len(time_taken),
                "fastest_completion": min(time_taken),
                "slowest_completion": max(time_taken),
                "median_time": sorted(time_taken)[len(time_taken) // 2]
            }
        
        return {
            "success": True,
            "assessment": {
                "id": str(assessment["_id"]),
                "title": assessment.get("title", "Assessment"),
                "subject": assessment.get("topic", assessment.get("subject", "")),
                "difficulty": assessment.get("difficulty", "medium"),
                "total_questions": len(questions),
                "time_limit": assessment.get("time_limit", 30)
            },
            "analytics": {
                "total_submissions": total_submissions,
                "average_score": round(average_score, 2),
                "completion_rate": 100,  # All submissions are completed
                "question_analysis": question_analysis,
                "batch_performance": batch_performance,
                "time_analysis": time_analysis,
                "score_distribution": {
                    "excellent": len([s for s in all_submissions if s["percentage"] >= 90]),
                    "good": len([s for s in all_submissions if 80 <= s["percentage"] < 90]),
                    "average": len([s for s in all_submissions if 60 <= s["percentage"] < 80]),
                    "poor": len([s for s in all_submissions if s["percentage"] < 60])
                }
            },
            "submissions": all_submissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching assessment analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/questions", response_model=QuestionResponse)
async def add_question_to_assessment(
    assessment_id: str, 
    question_data: QuestionCreate, 
    user: UserModel = Depends(require_teacher)
):
    """Add a question to an assessment"""
    try:
        db = await get_db()
        
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Check if assessment exists and belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id), 
            "created_by": str(user.id)
        })
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Create question document
        question_doc = {
            "question": question_data.question,
            "options": question_data.options,
            "correct_answer": question_data.correct_answer,
            "explanation": question_data.explanation,
            "points": question_data.points,
            "created_at": datetime.utcnow()
        }
        
        # Add question to assessment
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$push": {"questions": question_doc}}
        )
        
        # Update question count
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$inc": {"question_count": 1}}
        )
        
        return QuestionResponse(
            id=str(len(assessment.get("questions", [])) + 1),
            question=question_data.question,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            points=question_data.points
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/coding-questions", response_model=CodingQuestionResponse)
async def add_coding_question_to_assessment(
    assessment_id: str, 
    question_data: CodingQuestionCreate, 
    user: UserModel = Depends(get_current_user)
):
    """Add a coding question to an assessment"""
    try:
        print(f"[DEBUG] [BACKEND] Received coding question data: {question_data}")
        print(f"[DEBUG] [BACKEND] Assessment ID: {assessment_id}")
        print(f"[DEBUG] [BACKEND] User: {user}")
        
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can add coding questions")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if assessment.get("created_by") != str(user.id):
            raise HTTPException(status_code=403, detail="You can only add questions to your own assessments")
        
        coding_question_doc = {
            "type": "coding",
            "title": question_data.title,
            "description": question_data.description,
            "problem_statement": question_data.problem_statement,
            "constraints": question_data.constraints,
            "examples": question_data.examples,
            "test_cases": question_data.test_cases,
            "hidden_test_cases": question_data.hidden_test_cases,
            "expected_complexity": question_data.expected_complexity,
            "hints": question_data.hints,
            "points": question_data.points,
            "time_limit": question_data.time_limit,
            "memory_limit": question_data.memory_limit,
            "created_at": datetime.utcnow()
        }
        
        # Add coding question to assessment
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$push": {"questions": coding_question_doc}}
        )
        
        # Update question count
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$inc": {"question_count": 1}}
        )
        
        return CodingQuestionResponse(
            id=str(len(assessment.get("questions", [])) + 1),
            title=question_data.title,
            description=question_data.description,
            problem_statement=question_data.problem_statement,
            constraints=question_data.constraints,
            examples=question_data.examples,
            hints=question_data.hints,
            points=question_data.points,
            time_limit=question_data.time_limit,
            memory_limit=question_data.memory_limit,
            test_cases=question_data.test_cases
        )
    except Exception as e:
        print(f"[ERROR] [BACKEND] Error in add_coding_question_to_assessment: {e}")
        print(f"[ERROR] [BACKEND] Error type: {type(e)}")
        if hasattr(e, 'errors'):
            print(f"[ERROR] [BACKEND] Validation errors: {e.errors()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/ai-generate-questions")
async def ai_generate_questions(
    assessment_id: str,
    generation_data: dict,
    user: UserModel = Depends(get_current_user)
):
    """Generate questions using AI for an assessment"""
    try:
        print(f"[AI] [AI GENERATION] Received request for assessment {assessment_id}")
        print(f"[AI] [AI GENERATION] Generation data: {generation_data}")
        
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can generate AI questions")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if assessment.get("created_by") != str(user.id):
            raise HTTPException(status_code=403, detail="You can only generate questions for your own assessments")
        
        question_type = generation_data.get("question_type", "mcq")
        topic = generation_data.get("topic", "")
        difficulty = generation_data.get("difficulty", "medium")
        question_count = generation_data.get("question_count", 10)
        title = generation_data.get("title", "")
        
        print(f"[AI] [AI GENERATION] Generating {question_count} {question_type} questions for topic: {topic}")
        
        generated_questions = []
        
        if question_type == "mcq" or question_type == "both":
            # Generate MCQ questions
            mcq_count = question_count if question_type == "mcq" else question_count // 2
            for i in range(mcq_count):
                # Generate topic-specific MCQ questions
                mcq_question = generate_mcq_question(topic, difficulty, i+1)
                generated_questions.append(mcq_question)
        
        if question_type == "coding" or question_type == "both":
            # Generate coding questions
            coding_count = question_count if question_type == "coding" else question_count - (question_count // 2)
            for i in range(coding_count):
                # Generate topic-specific coding questions
                coding_question = generate_coding_question(topic, difficulty, i+1)
                generated_questions.append(coding_question)
        
        # Add all generated questions to the assessment
        if generated_questions:
            await db.assessments.update_one(
                {"_id": ObjectId(assessment_id)},
                {"$push": {"questions": {"$each": generated_questions}}}
            )
            
            # Update question count
            await db.assessments.update_one(
                {"_id": ObjectId(assessment_id)},
                {"$inc": {"question_count": len(generated_questions)}}
            )
        
        print(f"[AI] [AI GENERATION] Successfully generated {len(generated_questions)} questions")
        
        return {
            "success": True,
            "generated_count": len(generated_questions),
            "question_type": question_type,
            "message": f"Successfully generated {len(generated_questions)} {question_type} questions"
        }
        
    except Exception as e:
        print(f"[ERROR] [AI GENERATION] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/publish")
async def publish_assessment(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Publish an assessment and assign to batches"""
    try:
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can publish assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Check if assessment exists and belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id), 
            "created_by": str(user.id)
        })
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if len(assessment.get("questions", [])) == 0:
            raise HTTPException(status_code=400, detail="Assessment must have at least one question")
        
        # Update assessment status to active so it appears in upcoming endpoints
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$set": {"status": "active", "is_active": True, "published_at": datetime.utcnow()}}
        )
        
        # Get assigned batches
        assigned_batches = assessment.get("assigned_batches", [])
        
        # Create notifications for students in assigned batches
        for batch_id in assigned_batches:
            # Get students in this batch
            batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
            if batch:
                student_ids = batch.get("student_ids", [])
                
                # Create notifications for each student
                notifications = []
                for student_id in student_ids:
                    # Prefer subject if topic is not present
                    subject_or_topic = assessment.get("subject") or assessment.get("topic", "Assessment")
                    notification = {
                        "student_id": student_id,
                        "type": "assessment_assigned",
                        "title": f"New Assessment: {assessment.get('title', 'Untitled')}",
                        "message": f"A new {assessment.get('difficulty', 'medium')} assessment on {subject_or_topic} has been assigned to you.",
                        "assessment_id": assessment_id,
                        "created_at": datetime.utcnow(),
                        "is_read": False
                    }
                    notifications.append(notification)
                
                if notifications:
                    await db.notifications.insert_many(notifications)
        
        return {"success": True, "message": "Assessment published successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/assign-batches")
async def assign_assessment_to_batches(
    assessment_id: str, 
    batch_ids: List[str], 
    user: UserModel = Depends(get_current_user)
):
    """Assign assessment to specific batches"""
    try:
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can assign assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Validate batch IDs
        valid_batch_ids = []
        for batch_id in batch_ids:
            if ObjectId.is_valid(batch_id):
                batch = await db.batches.find_one({
                    "_id": ObjectId(batch_id), 
                    "teacher_id": str(user.id)
                })
                if batch:
                    valid_batch_ids.append(batch_id)
        
        # Update assessment with assigned batches
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$set": {"assigned_batches": valid_batch_ids}}
        )
        
        return {"success": True, "message": f"Assessment assigned to {len(valid_batch_ids)} batch(es)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Student Assessment Endpoints

@router.get("/student/available", response_model=List[AssessmentResponse])
async def get_available_assessments(user: UserModel = Depends(get_current_user)):
    """Get assessments available to the student"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can view available assessments")
        
        # Get student's batch
        student_batches = await db.batches.find({"student_ids": str(user.id)}).to_list(None)
        batch_ids = [str(batch["_id"]) for batch in student_batches]
        
        # Get published assessments assigned to these batches
        assessments_cursor = await db.assessments.find({
            "status": "published",
            "assigned_batches": {"$in": batch_ids}
        }).to_list(None)
        
        assessments = []
        for assessment in assessments_cursor:
            # Check if student has already taken this assessment
            existing_result = await db.assessment_results.find_one({
                "assessment_id": str(assessment["_id"]),
                "student_id": str(user.id)
            })
            
            if not existing_result or existing_result.get("attempt_number", 0) < assessment.get("max_attempts", 1):
                assessment_response = AssessmentResponse(
                    id=str(assessment["_id"]),
                    title=assessment["title"],
                    topic=assessment["topic"],
                    difficulty=assessment["difficulty"],
                    description=assessment.get("description"),
                    time_limit=assessment.get("time_limit"),
                    max_attempts=assessment.get("max_attempts", 1),
                    question_count=len(assessment.get("questions", [])),
                    created_by=assessment["created_by"],
                    created_at=assessment["created_at"].isoformat(),
                    status=assessment["status"],
                    type=assessment.get("type", "mcq")
                )
                assessments.append(assessment_response)
        
        return assessments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/questions", response_model=List[QuestionResponse])
async def get_assessment_questions(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Get questions for an assessment (for taking the test)"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if student has access to this assessment
        if user.role == "student":
            student_batches = await db.batches.find({"student_ids": str(user.id)}).to_list(None)
            batch_ids = [str(batch["_id"]) for batch in student_batches]
            
            if not any(batch_id in assessment.get("assigned_batches", []) for batch_id in batch_ids):
                raise HTTPException(status_code=403, detail="Access denied")
        
        questions = []
        for i, question in enumerate(assessment.get("questions", [])):
            # For students, don't include correct answers
            if user.role == "student":
                question_response = QuestionResponse(
                    id=str(i + 1),
                    question=question["question"],
                    options=question["options"],
                    correct_answer=-1,  # Hide correct answer
                    explanation=None,  # Hide explanation
                    points=question.get("points", 1)
                )
            else:
                question_response = QuestionResponse(
                    id=str(i + 1),
                    question=question["question"],
                    options=question["options"],
                    correct_answer=question["correct_answer"],
                    explanation=question.get("explanation"),
                    points=question.get("points", 1)
                )
            questions.append(question_response)
        
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/submit", response_model=AssessmentResult)
async def submit_assessment(
    assessment_id: str, 
    submission: AssessmentSubmission, 
    user: UserModel = Depends(get_current_user)
):
    """Submit an assessment"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can submit assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if student has access
        student_batches = await db.batches.find({"student_ids": str(user.id)}).to_list(None)
        batch_ids = [str(batch["_id"]) for batch in student_batches]
        
        if not any(batch_id in assessment.get("assigned_batches", []) for batch_id in batch_ids):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check attempt limit
        existing_results = await db.assessment_results.find({
            "assessment_id": assessment_id,
            "student_id": str(user.id)
        }).to_list(None)
        
        if len(existing_results) >= assessment.get("max_attempts", 1):
            raise HTTPException(status_code=400, detail="Maximum attempts exceeded")
        
        # Grade the assessment
        questions = assessment.get("questions", [])
        score = 0
        total_questions = len(questions)
        
        for i, question in enumerate(questions):
            if i < len(submission.answers):
                user_answer = submission.answers[i]
                correct_answer_index = question.get("correct_answer", -1)
                correct_answer = ""
                options = question.get("options", [])
                
                # Handle both string and integer correct answers
                if isinstance(correct_answer_index, int) and correct_answer_index >= 0:
                    if correct_answer_index < len(options):
                        correct_answer = options[correct_answer_index]
                else:
                    correct_answer = question.get("answer", "")
                
                # If correct answer is just a letter (A, B, C, D), map to option index
                if len(correct_answer) == 1 and correct_answer.isalpha():
                    letter = correct_answer.upper()
                    letter_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}
                    if letter in letter_to_index and letter_to_index[letter] < len(options):
                        correct_answer = options[letter_to_index[letter]]
                
                # Convert user answer to text if it's an index
                user_answer_text = ""
                if isinstance(user_answer, int) and 0 <= user_answer < len(options):
                    user_answer_text = options[user_answer]
                else:
                    user_answer_text = str(user_answer)
                
                # Compare the text versions
                if user_answer_text == correct_answer:
                    score += question.get("points", 1)
        
        percentage = (score / sum(q.get("points", 1) for q in questions)) * 100 if questions else 0
        
        # Convert user answers to text format for question review
        user_answers_text = []
        for i, question in enumerate(questions):
            if i < len(submission.answers):
                user_answer_raw = submission.answers[i]
                options = question.get("options", [])
                
                # Convert to text if it's an index
                if isinstance(user_answer_raw, int) and 0 <= user_answer_raw < len(options):
                    user_answers_text.append(options[user_answer_raw])
                else:
                    user_answers_text.append(str(user_answer_raw))
            else:
                user_answers_text.append("")
        
        # Create result
        result_doc = {
            "assessment_id": assessment_id,
            "student_id": str(user.id),
            "student_name": user.username or user.email,
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "time_taken": submission.time_taken,
            "submitted_at": datetime.utcnow(),
            "attempt_number": len(existing_results) + 1,
            "answers": submission.answers,  # Keep original format
            "user_answers": user_answers_text,  # Add text format for review
            "questions": questions  # Store questions for review
        }
        
        result = await db.assessment_results.insert_one(result_doc)
        
        # Create notification for student about result
        notification = {
            "student_id": str(user.id),
            "type": "result_available",
            "title": f"Assessment Result: {assessment['title']}",
            "message": f"Your assessment result is available. Score: {score}/{sum(q.get('points', 1) for q in questions)} ({percentage:.1f}%)",
            "assessment_id": assessment_id,
            "created_at": datetime.utcnow(),
            "is_read": False
        }
        await db.notifications.insert_one(notification)
        
        # Create assessment completion notifications
        teacher_id = assessment.get("created_by")
        await create_assessment_completion_notification(
            db, 
            str(user.id), 
            assessment['title'], 
            percentage, 
            teacher_id
        )
        
        # Update user gamification data
        await update_user_progress(db, str(user.id), score, percentage, total_questions)
        
        return AssessmentResult(
            id=str(result.inserted_id),
            assessment_id=assessment_id,
            student_id=str(user.id),
            student_name=result_doc["student_name"],
            score=score,
            total_questions=total_questions,
            percentage=percentage,
            time_taken=submission.time_taken,
            submitted_at=result_doc["submitted_at"].isoformat(),
            attempt_number=result_doc["attempt_number"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/leaderboard", response_model=AssessmentLeaderboard)
async def get_assessment_leaderboard(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Get leaderboard for an assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if user has access to this assessment
        if user.role == "student":
            student_batches = await db.batches.find({"student_ids": str(user.id)}).to_list(None)
            batch_ids = [str(batch["_id"]) for batch in student_batches]
            
            if not any(batch_id in assessment.get("assigned_batches", []) for batch_id in batch_ids):
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all results for this assessment
        results_cursor = await db.assessment_results.find({
            "assessment_id": assessment_id
        }).sort("percentage", -1).to_list(None)
        
        leaderboard = []
        for i, result in enumerate(results_cursor):
            entry = LeaderboardEntry(
                student_id=result["student_id"],
                student_name=result["student_name"],
                score=result["score"],
                percentage=result["percentage"],
                time_taken=result.get("time_taken"),
                rank=i + 1
            )
            leaderboard.append(entry)
        
        return AssessmentLeaderboard(
            assessment_id=assessment_id,
            assessment_title=assessment["title"],
            total_students=len(leaderboard),
            leaderboard=leaderboard
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Notification Endpoints

@router.get("/notifications", response_model=List[StudentNotification])
async def get_student_notifications(user: UserModel = Depends(get_current_user)):
    """Get notifications for a student"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can view notifications")
        
        print(f"🔍 [NOTIFICATIONS] Fetching notifications for student: {user.id}")
        
        notifications_cursor = await db.notifications.find({
            "student_id": str(user.id)
        }).sort("created_at", -1).to_list(None)
        
        print(f"📋 [NOTIFICATIONS] Found {len(notifications_cursor)} notifications")
        
        notifications = []
        for notification in notifications_cursor:
            try:
                # Handle created_at field - it might be a datetime or string
                created_at = notification.get("created_at")
                if isinstance(created_at, datetime):
                    created_at_str = created_at.isoformat()
                elif isinstance(created_at, str):
                    created_at_str = created_at
                else:
                    created_at_str = datetime.utcnow().isoformat()
                
                notification_response = StudentNotification(
                    id=str(notification["_id"]),
                    student_id=notification["student_id"],
                    type=notification["type"],
                    title=notification["title"],
                    message=notification["message"],
                    assessment_id=notification.get("assessment_id"),
                    created_at=created_at_str,
                    is_read=notification.get("is_read", False)
                )
                notifications.append(notification_response)
            except Exception as e:
                print(f"❌ [NOTIFICATIONS] Error processing notification {notification.get('_id')}: {str(e)}")
                continue
        
        print(f"✅ [NOTIFICATIONS] Returning {len(notifications)} notifications")
        return notifications
    except Exception as e:
        print(f"❌ [NOTIFICATIONS] Error in get_student_notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user: UserModel = Depends(get_current_user)):
    """Mark a notification as read"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can mark notifications as read")
        
        if not ObjectId.is_valid(notification_id):
            raise HTTPException(status_code=400, detail="Invalid notification ID")
        
        await db.notifications.update_one(
            {"_id": ObjectId(notification_id), "student_id": str(user.id)},
            {"$set": {"is_read": True}}
        )
        
        return {"success": True, "message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str, user: UserModel = Depends(get_current_user)):
    """Delete a notification"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can delete notifications")
        
        if not ObjectId.is_valid(notification_id):
            raise HTTPException(status_code=400, detail="Invalid notification ID")
        
        result = await db.notifications.delete_one({
            "_id": ObjectId(notification_id), 
            "student_id": str(user.id)
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"success": True, "message": "Notification deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/coding-submit", response_model=CodingSubmissionResponse)
async def submit_coding_solution(
    assessment_id: str,
    submission_data: CodingSubmission,
    user: UserModel = Depends(get_current_user)
):
    """Submit a coding solution for a coding question"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can submit coding solutions")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Find the coding question
        coding_question = None
        for question in assessment.get("questions", []):
            if question.get("type") == "coding" and str(question.get("_id", "")) == submission_data.question_id:
                coding_question = question
                break
        
        if not coding_question:
            raise HTTPException(status_code=404, detail="Coding question not found")
        
        # Execute the code (this would integrate with your code execution service)
        # For now, we'll simulate the execution
        test_results = []
        score = 0
        status = "accepted"
        
        # Simulate test case execution
        for test_case in coding_question.get("test_cases", []):
            # This would call your code execution service
            test_result = {
                "input": test_case.get("input"),
                "expected_output": test_case.get("expected_output"),
                "actual_output": "Simulated output",  # This would be the actual execution result
                "passed": True,  # This would be determined by the execution service
                "execution_time": 100,  # milliseconds
                "memory_used": 50  # MB
            }
            test_results.append(test_result)
            if test_result["passed"]:
                score += 1
        
        # Create submission record
        submission_doc = {
            "assessment_id": assessment_id,
            "question_id": submission_data.question_id,
            "student_id": str(user.id),
            "code": submission_data.code,
            "language": submission_data.language,
            "status": status,
            "test_results": test_results,
            "score": score,
            "max_score": len(coding_question.get("test_cases", [])),
            "execution_time": sum(t.get("execution_time", 0) for t in test_results),
            "memory_used": max(t.get("memory_used", 0) for t in test_results) if test_results else 0,
            "submitted_at": datetime.utcnow()
        }
        
        result = await db.coding_submissions.insert_one(submission_doc)
        
        return CodingSubmissionResponse(
            id=str(result.inserted_id),
            assessment_id=assessment_id,
            question_id=submission_data.question_id,
            status=status,
            execution_time=submission_doc["execution_time"],
            memory_used=submission_doc["memory_used"],
            test_results=test_results,
            score=score,
            max_score=submission_doc["max_score"],
            submitted_at=submission_doc["submitted_at"].isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/details")
async def get_assessment_details(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Get detailed assessment information including questions"""
    try:
        db = await get_db()
        
        # Accept both ObjectId and string IDs used by some seed data
        assessment = None
        if ObjectId.is_valid(assessment_id):
            assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            assessment = await db.assessments.find_one({"_id": assessment_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if user has access to this assessment (teachers can view their own or any if admin)
        if str(getattr(user, "role", "")).lower() == "teacher":
            created_by = str(assessment.get("created_by", ""))
            if created_by and created_by != str(user.id):
                # Allow viewing even if not creator, but hide questions to avoid leakage
                return {
                    "id": str(assessment.get("_id")),
                    "title": assessment.get("title"),
                    "topic": assessment.get("topic"),
                    "difficulty": assessment.get("difficulty"),
                    "description": assessment.get("description"),
                    "time_limit": assessment.get("time_limit"),
                    "max_attempts": assessment.get("max_attempts", 1),
                    "question_count": len(assessment.get("questions", [])),
                    "created_by": created_by,
                    "created_at": (assessment.get("created_at") or datetime.utcnow()).isoformat(),
                    "status": assessment.get("status", "active"),
                    "type": assessment.get("type", "mcq"),
                    "questions": []
                }
        
        return {
            "id": str(assessment["_id"]),
            "title": assessment["title"],
            "topic": assessment["topic"],
            "difficulty": assessment["difficulty"],
            "description": assessment.get("description"),
            "time_limit": assessment.get("time_limit"),
            "max_attempts": assessment.get("max_attempts", 1),
            "question_count": len(assessment.get("questions", [])),
            "created_by": assessment["created_by"],
            "created_at": (assessment.get("created_at") or datetime.utcnow()).isoformat(),
            "status": assessment["status"],
            "type": assessment.get("type", "mcq"),
            "questions": assessment.get("questions", [])  # Include questions in response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def send_assessment_notifications(db, assessment_id: str, batch_ids: List[str], assessment_title: str):
    """Send notifications to students when a new assessment is created"""
    try:
        print(f"📢 [NOTIFICATION] Sending assessment notifications for: {assessment_title}")
        
        # Get all students from the selected batches
        students = []
        for batch_id in batch_ids:
            # First, get the batch to find student_ids
            batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
            if batch and batch.get("student_ids"):
                # Get students by their IDs from the batch
                student_ids = batch["student_ids"]
                batch_students = await db.users.find({
                    "_id": {"$in": [ObjectId(sid) for sid in student_ids]},
                    "role": "student",
                    "is_active": True
                }).to_list(length=None)
                students.extend(batch_students)
                print(f"📢 [NOTIFICATION] Found {len(batch_students)} students in batch {batch_id}")
            else:
                print(f"❌ [NOTIFICATION] No students found in batch {batch_id}")
        
        # Create notifications for each student
        notifications = []
        for student in students:
            notification = {
                "student_id": str(student["_id"]),
                "type": "assessment_assigned",
                "title": "New Assessment Available",
                "message": f"A new assessment '{assessment_title}' has been assigned to you.",
                "assessment_id": assessment_id,
                "created_at": datetime.utcnow(),
                "is_read": False
            }
            notifications.append(notification)
        
        # Insert notifications in bulk
        if notifications:
            await db.notifications.insert_many(notifications)
            print(f"✅ [NOTIFICATION] Sent {len(notifications)} notifications to students")
        
    except Exception as e:
        print(f"❌ [NOTIFICATION] Error sending notifications: {str(e)}")

@router.get("/upcoming", response_model=List[AssessmentResponse])
async def get_upcoming_assessments(user: UserModel = Depends(get_current_user)):
    """Get upcoming assessments for a student"""
    try:
        db = await get_db()
        
        # Get student's batch_id
        student = await db.users.find_one({"_id": ObjectId(user.id)})
        if not student or not student.get("batch_id"):
            return []
        
        batch_id = student["batch_id"]
        
        # Find assessments assigned to this batch that are active
        assessments = await db.assessments.find({
            "assigned_batches": batch_id,
            "is_active": True,
            "status": "active"
        }).to_list(length=None)
        
        # Check if student has already submitted these assessments
        submitted_assessments = await db.assessment_submissions.find({
            "student_id": user.id
        }).to_list(length=None)
        
        submitted_ids = [sub["assessment_id"] for sub in submitted_assessments]
        
        # Filter out already submitted assessments
        upcoming_assessments = [
            assessment for assessment in assessments 
            if str(assessment["_id"]) not in submitted_ids
        ]
        
        return [
            AssessmentResponse(
                id=str(assessment["_id"]),
                title=assessment["title"],
                subject=assessment["subject"],
                difficulty=assessment["difficulty"],
                description=assessment["description"],
                time_limit=assessment["time_limit"],
                max_attempts=assessment["max_attempts"],
                question_count=assessment["question_count"],
                created_by=assessment["created_by"],
                created_at=assessment["created_at"].isoformat(),
                status=assessment["status"],
                type=assessment.get("type", "mcq"),
                is_active=assessment["is_active"],
                total_questions=assessment["question_count"]
            )
            for assessment in upcoming_assessments
        ]
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching upcoming assessments: {str(e)}")
        return []

@router.get("/teacher/upcoming", response_model=List[AssessmentResponse])
async def get_teacher_assessments(user: UserModel = Depends(get_current_user)):
    """Get teacher-assigned assessments for the current user (student consumption)."""
    try:
        print(f"🔍 [TEACHER_ASSESSMENT] Starting request for user: {user.id}")
        
        # Validate user object
        if not user or not hasattr(user, 'id'):
            print(f"❌ [TEACHER_ASSESSMENT] Invalid user object")
            return []
        
        print(f"🔍 [TEACHER_ASSESSMENT] User validated: {user.id}")
        
        # Get database connection with error handling
        try:
            db = await get_db()
            print(f"🔍 [TEACHER_ASSESSMENT] Database connection established")
        except Exception as db_error:
            print(f"❌ [TEACHER_ASSESSMENT] Database connection failed: {str(db_error)}")
            return []
        
        # Get student's batch_id from batches collection
        try:
            print(f"🔍 [TEACHER_ASSESSMENT] Looking for student batches...")
            student_batches = await db.batches.find({
                "student_ids": str(user.id)
            }).to_list(length=None)
            
            if not student_batches:
                print(f"❌ [TEACHER_ASSESSMENT] Student {user.id} is not in any batch")
                return []
            
            batch_ids = [str(batch["_id"]) for batch in student_batches]
            print(f"🔍 [TEACHER_ASSESSMENT] Student {user.id} is in batches: {batch_ids}")
        except Exception as batch_error:
            print(f"❌ [TEACHER_ASSESSMENT] Error fetching student batches: {str(batch_error)}")
            return []
        
        # Check if teacher_assessments collection exists; if not, fall back to regular assessments
        try:
            print(f"🔍 [TEACHER_ASSESSMENT] Checking collections...")
            collections = await db.list_collection_names()
            has_teacher_collection = "teacher_assessments" in collections
        except Exception as collection_error:
            print(f"❌ [TEACHER_ASSESSMENT] Error checking collections: {str(collection_error)}")
            has_teacher_collection = False
        
        # Find teacher assessments assigned to these batches
        try:
            teacher_assessments = []
            if has_teacher_collection:
                print(f"🔍 [TEACHER_ASSESSMENT] Querying teacher assessments...")
                teacher_assessments = await db.teacher_assessments.find({
                    "batches": {"$in": batch_ids},
                    "is_active": True,
                    "status": "published"
                }).to_list(length=None)
                print(f"📊 [TEACHER_ASSESSMENT] Found {len(teacher_assessments)} teacher assessments for batches {batch_ids}")
            else:
                print(f"🔍 [TEACHER_ASSESSMENT] Falling back to assessments collection...")
                teacher_assessments = await db.assessments.find({
                    "assigned_batches": {"$in": batch_ids},
                    "is_active": True,
                    "status": "active"
                }).to_list(length=None)
                print(f"📊 [TEACHER_ASSESSMENT] Found {len(teacher_assessments)} fallback assessments for batches {batch_ids}")
        except Exception as query_error:
            print(f"❌ [TEACHER_ASSESSMENT] Error querying assessments: {str(query_error)}")
            return []
        
        # Check if student has already submitted these assessments (both collections)
        submitted_assessments = []
        submitted_ids = []
        try:
            if "teacher_assessment_results" in collections:
                print(f"🔍 [TEACHER_ASSESSMENT] Checking submitted teacher assessments...")
                submitted_assessments = await db.teacher_assessment_results.find({
                    "student_id": user.id
                }).to_list(length=None)
                submitted_ids.extend([sub.get("assessment_id") for sub in submitted_assessments if sub.get("assessment_id")])
            else:
                print(f"⚠️ [TEACHER_ASSESSMENT] teacher_assessment_results collection not found")
        except Exception as submitted_error:
            print(f"⚠️ [TEACHER_ASSESSMENT] Error fetching teacher submissions: {str(submitted_error)}")
        # Also include regular assessment submissions for fallback assessments
        try:
            regular_submissions = await db.assessment_submissions.find({
                "student_id": user.id
            }).to_list(length=None)
            submitted_ids.extend([sub.get("assessment_id") for sub in regular_submissions if sub.get("assessment_id")])
        except Exception as sub_err:
            print(f"⚠️ [TEACHER_ASSESSMENT] Error fetching regular submissions: {str(sub_err)}")
        
        try:
            # Filter out already submitted assessments
            available_assessments = [
                assessment for assessment in teacher_assessments 
                if str(assessment["_id"]) not in submitted_ids
            ]
            
            # Format response
            print(f"🔍 [TEACHER_ASSESSMENT] Formatting response...")
            formatted_assessments = []
            for assessment in available_assessments:
                try:
                    formatted_assessments.append({
                        "id": str(assessment["_id"]),
                        "title": assessment.get("title", assessment.get("subject", "Untitled Assessment")),
                        "description": f"Teacher-created assessment on {assessment.get('topic', assessment.get('subject', 'General'))}",
                        "subject": assessment.get("topic", assessment.get("subject", "General")),
                        "difficulty": assessment.get("difficulty", "medium"),
                        "time_limit": 30,  # Default 30 minutes for teacher assessments
                        "max_attempts": 1,
                        "question_count": assessment.get("question_count", 0),
                        "created_by": str(assessment.get("teacher_id", assessment.get("created_by", "unknown"))),
                        "created_at": assessment.get("created_at", datetime.utcnow()).isoformat(),
                        "status": assessment.get("status", "active"),
                        "type": "teacher",
                        "is_active": assessment.get("is_active", True),
                        "total_questions": assessment.get("question_count", 0),
                        "assigned_batches": assessment.get("batches", assessment.get("assigned_batches", []))
                    })
                except Exception as format_error:
                    print(f"⚠️ [TEACHER_ASSESSMENT] Error formatting assessment {assessment.get('_id')}: {str(format_error)}")
                    continue
            
            print(f"✅ [TEACHER_ASSESSMENT] Returning {len(formatted_assessments)} available assessments")
            return formatted_assessments
            
        except Exception as format_error:
            print(f"❌ [TEACHER_ASSESSMENT] Error in final formatting: {str(format_error)}")
            return []
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Unexpected error in teacher assessments: {str(e)}")
        import traceback
        print(f"❌ [ASSESSMENT] Traceback: {traceback.format_exc()}")
        # Return empty list instead of raising exception to avoid 500 error
        return []

@router.get("/teacher/{assessment_id}")
async def get_teacher_assessment_details(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Get details of a teacher-assigned assessment"""
    try:
        db = await get_db()
        
        print(f"🔍 [TEACHER_ASSESSMENT] Fetching details for assessment: {assessment_id}")
        
        # Validate ID format but don't fail hard; we'll try both ObjectId and string lookups
        is_oid = ObjectId.is_valid(assessment_id)
        
        # Determine storage and fetch with fallback
        collections = await db.list_collection_names()
        assessment = None
        if "teacher_assessments" in collections:
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)}) if is_oid else None
            if not assessment:
                assessment = await db.teacher_assessments.find_one({"_id": assessment_id})
        if not assessment:
            assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)}) if is_oid else None
            if not assessment:
                assessment = await db.assessments.find_one({"_id": assessment_id})
            if assessment:
                assessment.setdefault("batches", assessment.get("assigned_batches", []))
                assessment.setdefault("is_active", assessment.get("is_active", False))
                assessment.setdefault("topic", assessment.get("subject", "General"))
        if not assessment:
            print(f"❌ [TEACHER_ASSESSMENT] Assessment {assessment_id} not found")
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        print(f"✅ [TEACHER_ASSESSMENT] Found assessment: {assessment.get('title', 'Untitled')}")
        
        # If the requester is a teacher/admin, allow access without batch checks
        if str(getattr(user, "role", "")).lower() not in ["teacher", "admin"]:
            # Check if student has access (is in one of the assigned batches)
            # Support both ObjectId and string user IDs in users collection
            student = None
            try:
                if ObjectId.is_valid(str(user.id)):
                    student = await db.users.find_one({"_id": ObjectId(str(user.id))})
            except Exception:
                student = None
            if not student:
                student = await db.users.find_one({"_id": str(user.id)})
            if not student:
                print(f"❌ [TEACHER_ASSESSMENT] Student {user.id} not found")
                raise HTTPException(status_code=403, detail="Access denied")

            # Get student's batches
            student_batches = await db.batches.find({
                "student_ids": str(user.id)
            }).to_list(length=None)

            if not student_batches:
                print(f"❌ [TEACHER_ASSESSMENT] Student {user.id} is not in any batch")
                raise HTTPException(status_code=403, detail="Access denied")

            batch_ids = [str(batch["_id"]) for batch in student_batches]
            assessment_batches = assessment.get("batches", assessment.get("assigned_batches", []))

            # Check if student is in any of the assessment's batches
            if not any(batch_id in assessment_batches for batch_id in batch_ids):
                print(f"❌ [TEACHER_ASSESSMENT] Student {user.id} not in assessment batches. Student batches: {batch_ids}, Assessment batches: {assessment_batches}")
                raise HTTPException(status_code=403, detail="Assessment not assigned to your batch")
        
        # Check if assessment is active (skip for teachers/admins so they can review)
        if str(getattr(user, "role", "")).lower() not in ["teacher", "admin"]:
            if not assessment.get("is_active", False):
                print(f"❌ [TEACHER_ASSESSMENT] Assessment {assessment_id} is not active")
                raise HTTPException(status_code=400, detail="Assessment is not active")
        
        # Check if student has already submitted this assessment
        if "teacher_assessment_results" in collections:
            existing_submission = await db.teacher_assessment_results.find_one({
                "assessment_id": assessment_id,
                "student_id": user.id
            })
            if existing_submission:
                print(f"⚠️ [TEACHER_ASSESSMENT] Student {user.id} has already submitted assessment {assessment_id}")
                raise HTTPException(status_code=400, detail="Assessment already submitted")
        
        # Return assessment details
        created_at_val = assessment.get("created_at", datetime.utcnow())
        created_at_iso = created_at_val.isoformat() if hasattr(created_at_val, 'isoformat') else str(created_at_val)
        return {
            "id": str(assessment["_id"]),
            "title": assessment.get("title", assessment.get("subject", "Untitled Assessment")),
            "subject": assessment.get("topic", assessment.get("subject", "General")),
            "difficulty": assessment.get("difficulty", "medium"),
            "question_count": assessment.get("question_count", len(assessment.get("questions", []))),
            "time_limit": assessment.get("time_limit", 30),
            "max_attempts": assessment.get("max_attempts", 1),
            "type": "teacher",
            "questions": assessment.get("questions", []),
            "created_at": created_at_iso,
            "is_active": assessment.get("is_active", True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching teacher assessment details: {str(e)}")
        import traceback
        print(f"❌ [ASSESSMENT] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/teacher/{assessment_id}/submit")
async def submit_teacher_assessment(
    assessment_id: str,
    submission_data: dict,
    user: UserModel = Depends(get_current_user)
):
    """Submit a teacher-assigned assessment"""
    try:
        db = await get_db()
        
        # Get assessment details with fallback
        assessment = None
        collections = await db.list_collection_names() if hasattr(db, 'list_collection_names') else []
        if "teacher_assessments" in collections:
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
            if assessment:
                assessment.setdefault("topic", assessment.get("subject", "General"))
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if student has already submitted
        existing_submission = await db.teacher_assessment_results.find_one({
            "assessment_id": assessment_id,
            "student_id": user.id
        })
        
        if existing_submission:
            raise HTTPException(status_code=400, detail="Assessment already submitted")
        
        # Calculate score
        questions = assessment.get("questions", [])
        answers = submission_data.get("answers", [])
        score = 0
        
        for i, question in enumerate(questions):
            if i < len(answers):
                user_answer = answers[i]
                correct_answer_index = question.get("correct_answer", -1)
                correct_answer = ""
                options = question.get("options", [])
                
                # Handle both string and integer correct answers
                if isinstance(correct_answer_index, int) and correct_answer_index >= 0:
                    if correct_answer_index < len(options):
                        correct_answer = options[correct_answer_index]
                else:
                    correct_answer = question.get("answer", "")
                
                # If correct answer is just a letter (A, B, C, D), map to option index
                if len(correct_answer) == 1 and correct_answer.isalpha():
                    letter = correct_answer.upper()
                    letter_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}
                    if letter in letter_to_index and letter_to_index[letter] < len(options):
                        correct_answer = options[letter_to_index[letter]]
                
                # Convert user answer to text if it's an index
                if isinstance(user_answer, int) and 0 <= user_answer < len(options):
                    user_answer_text = options[user_answer]
                else:
                    user_answer_text = str(user_answer)
                
                if user_answer_text == correct_answer:
                    score += 1
        
        percentage = (score / len(questions)) * 100 if questions else 0
        time_taken = submission_data.get("time_taken", 0)
        
        # Convert user answers to text format for question review
        user_answers_text = []
        for i, question in enumerate(questions):
            if i < len(answers):
                user_answer_raw = answers[i]
                options = question.get("options", [])
                
                # Convert to text if it's an index
                if isinstance(user_answer_raw, int) and 0 <= user_answer_raw < len(options):
                    user_answers_text.append(options[user_answer_raw])
                else:
                    user_answers_text.append(str(user_answer_raw))
            else:
                user_answers_text.append("")
        
        # Create result record
        result_doc = {
            "assessment_id": assessment_id,
            "student_id": user.id,
            "student_name": user.username or user.email,
            "score": score,
            "total_questions": len(questions),
            "percentage": percentage,
            "time_taken": time_taken,
            "answers": answers,  # Keep original format
            "user_answers": user_answers_text,  # Add text format for review
            "questions": questions,  # Store questions for review
            "submitted_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        result = await db.teacher_assessment_results.insert_one(result_doc)
        
        # Create notification for student about result
        notification = {
            "student_id": user.id,
            "type": "teacher_assessment_result",
            "title": f"Assessment Result: {assessment['title']}",
            "message": f"Your assessment result is available. Score: {score}/{len(questions)} ({percentage:.1f}%)",
            "assessment_id": assessment_id,
            "created_at": datetime.utcnow(),
            "is_read": False
        }
        await db.notifications.insert_one(notification)
        
        # Create assessment completion notifications
        teacher_id = assessment.get("created_by")
        await create_assessment_completion_notification(
            db, 
            str(user.id), 
            assessment['title'], 
            percentage, 
            teacher_id
        )
        
        return {
            "success": True,
            "result_id": str(result.inserted_id),
            "score": score,
            "total_questions": len(questions),
            "percentage": percentage,
            "message": f"Assessment submitted successfully! Score: {score}/{len(questions)} ({percentage:.1f}%)"
        }
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error submitting teacher assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_assessment(submission_data: dict, user: UserModel = Depends(get_current_user)):
    """Submit an assessment"""
    try:
        db = await get_db()
        
        # Create submission record
        submission_doc = {
            "assessment_id": submission_data["assessment_id"],
            "student_id": submission_data["student_id"],
            "answers": submission_data["answers"],
            "score": submission_data["score"],
            "percentage": submission_data["percentage"],
            "time_taken": submission_data["time_taken"],
            "submitted_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        result = await db.assessment_submissions.insert_one(submission_doc)
        
        # Update student's progress
        await db.users.update_one(
            {"_id": ObjectId(user.id)},
            {
                "$inc": {
                    "completed_assessments": 1,
                    "total_score": submission_data["score"]
                },
                "$set": {
                    "last_assessment_date": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "submission_id": str(result.inserted_id),
            "score": submission_data["score"],
            "percentage": submission_data["percentage"]
        }
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error submitting assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/results")
async def get_assessment_results(assessment_id: str, user: UserModel = Depends(require_teacher)):
    """Get results for a specific assessment - Teacher only.
    Aggregates from assessment_submissions and teacher_assessment_results.
    """
    try:
        db = await get_db()
        
        # Normalize id formats (support ObjectId values and strings stored in DB)
        id_filters = [{"assessment_id": assessment_id}]
        try:
            if ObjectId.is_valid(assessment_id):
                oid = ObjectId(assessment_id)
                # Match both the ObjectId value and any stringified variants
                id_filters.append({"assessment_id": oid})
                id_filters.append({"assessment_id": str(oid)})
        except Exception:
            pass

        # Gather submissions from regular assessments
        regular_submissions = []
        try:
            regular_submissions = await db.assessment_submissions.find({"$or": id_filters}).to_list(length=None)
        except Exception:
            regular_submissions = []

        # Gather submissions from teacher assessments
        teacher_submissions = []
        try:
            teacher_submissions = await db.teacher_assessment_results.find({"$or": id_filters}).to_list(length=None)
        except Exception:
            teacher_submissions = []

        # Merge and format
        all_submissions = []
        for sub in regular_submissions:
            all_submissions.append({
                "student_id": sub.get("student_id"),
                "score": sub.get("score", 0),
                "percentage": sub.get("percentage", 0),
                "time_taken": sub.get("time_taken", 0),
                "submitted_at": sub.get("submitted_at"),
                "total_questions": sub.get("total_questions", len(sub.get("answers", [])))
            })
        for sub in teacher_submissions:
            all_submissions.append({
                "student_id": sub.get("student_id"),
                "score": sub.get("score", 0),
                "percentage": sub.get("percentage", 0),
                "time_taken": sub.get("time_taken", 0),
                "submitted_at": sub.get("submitted_at"),
                "total_questions": sub.get("total_questions", 0)
            })

        # Attach student details and batch information
        results = []
        for sub in all_submissions:
            student = None
            sid = sub.get("student_id")
            # try both ObjectId and string
            try:
                if sid and ObjectId.is_valid(str(sid)):
                    student = await db.users.find_one({"_id": ObjectId(str(sid))})
            except Exception:
                student = None
            if not student and sid:
                student = await db.users.find_one({"_id": str(sid)})

            # Get student's batch information
            batch_info = None
            if student:
                # First try to get batch info from student's batch_id field
                student_batch_id = student.get("batch_id")
                
                if student_batch_id:
                    try:
                        batch = await db.batches.find_one({"_id": ObjectId(str(student_batch_id))})
                        if batch:
                            batch_info = {
                                "batch_id": str(batch.get("_id")),
                                "batch_name": batch.get("name", batch.get("batch_name", "Unknown Batch"))
                            }
                    except Exception:
                        pass
                
                # If not found via batch_id, try finding via student_ids array
                if not batch_info:
                    student_batches = await db.batches.find({
                        "student_ids": str(student.get("_id"))
                    }).to_list(length=None)
                    
                    if student_batches:
                        batch = student_batches[0]  # Take the first batch
                        batch_info = {
                            "batch_id": str(batch.get("_id")),
                            "batch_name": batch.get("name", batch.get("batch_name", "Unknown Batch"))
                        }

            results.append({
                "student_id": str(student.get("_id", sid)) if student else str(sid),
                "student_name": student.get("name") or student.get("username") if student else "Unknown",
                "student_email": student.get("email") if student else "",
                "score": sub.get("score", 0),
                "percentage": sub.get("percentage", 0),
                "time_taken": sub.get("time_taken", 0),
                "submitted_at": (sub.get("submitted_at") or datetime.utcnow()).isoformat(),
                "total_questions": sub.get("total_questions", 0),
                "batch_info": batch_info
            })

        # Sort by submitted_at desc
        results.sort(key=lambda r: r.get("submitted_at", ""), reverse=True)
        return results
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching assessment results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Assigned students with attendance for an assessment (teacher view)
@router.get("/{assessment_id}/assigned-students")
async def get_assigned_students(assessment_id: str, user: UserModel = Depends(require_teacher)):
    """Return students assigned to an assessment (via batches) and their submission/attendance status.
    Supports both teacher_assessments (AI/teacher-created) and regular assessments collections.
    """
    try:
        db = await get_db()

        # Try to resolve assessment from teacher_assessments first, then regular assessments
        teacher_assessment = None
        regular_assessment = None

        try:
            if ObjectId.is_valid(assessment_id):
                teacher_assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        except Exception:
            teacher_assessment = None

        if not teacher_assessment:
            try:
                if ObjectId.is_valid(assessment_id):
                    regular_assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
            except Exception:
                regular_assessment = None

        # Collect batch ids from the resolved assessment
        batch_ids: list[str] = []
        if teacher_assessment:
            # teacher_assessments store batch ids (strings)
            batch_ids = [str(b) for b in teacher_assessment.get("batches", [])]
        elif regular_assessment:
            batch_ids = [str(b) for b in regular_assessment.get("assigned_batches", [])]
        else:
            # Nothing found
            return []

        # Find batches and accumulate student ids
        student_ids: set[str] = set()
        for bid in batch_ids:
            # batches.student_ids are strings of user ids
            try:
                batch = await db.batches.find_one({"_id": ObjectId(bid)})
            except Exception:
                batch = await db.batches.find_one({"_id": bid})
            if batch and batch.get("student_ids"):
                for sid in batch["student_ids"]:
                    if isinstance(sid, ObjectId):
                        student_ids.add(str(sid))
                    else:
                        student_ids.add(str(sid))

        # Fetch user docs for display
        students: dict[str, dict] = {}
        for sid in student_ids:
            doc = None
            try:
                if ObjectId.is_valid(sid):
                    doc = await db.users.find_one({"_id": ObjectId(sid)})
            except Exception:
                doc = None
            if not doc:
                doc = await db.users.find_one({"_id": sid})
            if doc:
                students[sid] = doc

        # Build id filters for submissions lookup
        id_filters = [{"assessment_id": assessment_id}]
        try:
            if ObjectId.is_valid(assessment_id):
                oid = ObjectId(assessment_id)
                id_filters.append({"assessment_id": oid})
                id_filters.append({"assessment_id": str(oid)})
        except Exception:
            pass

        # Fetch submissions across collections
        teacher_submissions = []
        regular_submissions = []
        try:
            teacher_submissions = await db.teacher_assessment_results.find({"$or": id_filters}).to_list(length=None)
        except Exception:
            teacher_submissions = []
        try:
            regular_submissions = await db.assessment_submissions.find({"$or": id_filters}).to_list(length=None)
        except Exception:
            regular_submissions = []

        # Map submissions by student_id
        submissions_by_student: dict[str, dict] = {}
        for sub in teacher_submissions:
            sid = sub.get("student_id")
            sid_str = str(sid) if sid is not None else ""
            submissions_by_student[sid_str] = {
                "result_id": str(sub.get("_id")),
                "score": sub.get("score", 0),
                "percentage": sub.get("percentage", 0.0),
                "time_taken": sub.get("time_taken", 0),
                "submitted_at": sub.get("submitted_at")
            }
        for sub in regular_submissions:
            sid = sub.get("student_id")
            sid_str = str(sid) if sid is not None else ""
            # do not override teacher submission if already present
            if sid_str not in submissions_by_student:
                submissions_by_student[sid_str] = {
                    "result_id": str(sub.get("_id")),
                    "score": sub.get("score", 0),
                    "percentage": sub.get("percentage", 0.0),
                    "time_taken": sub.get("time_taken", 0),
                    "submitted_at": sub.get("submitted_at")
                }

        # Get batch information for each student
        batch_info_map = {}
        for batch_id in batch_ids:
            try:
                batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
                if batch:
                    batch_info_map[batch_id] = {
                        "batch_id": str(batch["_id"]),
                        "batch_name": batch.get("name", batch.get("batch_name", "Unknown Batch"))
                    }
            except Exception:
                batch_info_map[batch_id] = {
                    "batch_id": batch_id,
                    "batch_name": "Unknown Batch"
                }

        # Construct response
        response = []
        for sid in sorted(student_ids):
            student = students.get(sid)
            sub = submissions_by_student.get(sid)
            
            # Find which batch this student belongs to
            student_batch_info = None
            if student:
                # First try to get batch info from student's batch_id field
                student_batch_id = student.get("batch_id")
                if student_batch_id:
                    try:
                        batch = await db.batches.find_one({"_id": ObjectId(str(student_batch_id))})
                        if batch:
                            student_batch_info = {
                                "batch_id": str(batch.get("_id")),
                                "batch_name": batch.get("name", batch.get("batch_name", "Unknown Batch"))
                            }
                    except Exception:
                        pass
                
                # If not found via batch_id, try finding via student_ids array
                if not student_batch_info:
                    student_batches = await db.batches.find({
                        "student_ids": str(student.get("_id"))
                    }).to_list(length=None)
                    
                    if student_batches:
                        batch = student_batches[0]  # Take the first batch
                        student_batch_info = {
                            "batch_id": str(batch.get("_id")),
                            "batch_name": batch.get("name", batch.get("batch_name", "Unknown Batch"))
                        }
            
            item = {
                "student_id": sid,
                "student_name": (student.get("name") or student.get("username") or "Unknown") if student else "Unknown",
                "student_email": (student.get("email") or "") if student else "",
                "assigned_via_batches": batch_ids,
                "batch_id": student_batch_info.get("batch_id") if student_batch_info else None,
                "batch_name": student_batch_info.get("batch_name") if student_batch_info else "No Batch Assigned",
                "submitted": sub is not None,
                "result_id": sub.get("result_id") if sub else None,
                "score": sub.get("score") if sub else None,
                "total_questions": None,
                "percentage": sub.get("percentage") if sub else None,
                "time_taken": sub.get("time_taken") if sub else None,
                "submitted_at": (sub.get("submitted_at").isoformat() if hasattr(sub.get("submitted_at"), "isoformat") else sub.get("submitted_at")) if sub else None,
            }
            response.append(item)

        return response
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching assigned students: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoints for comprehensive assessment system

@router.get("/student/upcoming", response_model=List[StudentAssessment])
async def get_student_upcoming_assessments(user: UserModel = Depends(get_current_user)):
    """Get upcoming assessments for a student"""
    try:
        db = await get_db()
        
        # Get student's batch_id from batches collection
        student_batches = await db.batches.find({
            "student_ids": str(user.id)
        }).to_list(length=None)
        
        if not student_batches:
            print(f"❌ [ASSESSMENT] Student {user.id} is not in any batch")
            return []
        
        batch_ids = [str(batch["_id"]) for batch in student_batches]
        print(f"🔍 [ASSESSMENT] Student {user.id} is in batches: {batch_ids}")
        
        # Find assessments assigned to these batches that are active
        assessments = await db.assessments.find({
            "assigned_batches": {"$in": batch_ids},
            "is_active": True,
            "status": "active"
        }).to_list(length=None)
        
        print(f"📊 [ASSESSMENT] Found {len(assessments)} assessments for batches {batch_ids}")
        
        # Check if student has already submitted these assessments
        submitted_ids = []
        try:
            submitted_assessments = await db.assessment_submissions.find({
                "student_id": user.id
            }).to_list(length=None)
            submitted_ids.extend([str(sub.get("assessment_id")) for sub in submitted_assessments if sub.get("assessment_id")])
        except Exception:
            pass
        # Also include teacher_assessment_results if any assessments are mirrored there
        try:
            teacher_submissions = await db.teacher_assessment_results.find({
                "student_id": user.id
            }).to_list(length=None)
            submitted_ids.extend([str(sub.get("assessment_id")) for sub in teacher_submissions if sub.get("assessment_id")])
        except Exception:
            pass
        
        # Filter out already submitted assessments
        upcoming_assessments = [
            assessment for assessment in assessments 
            if str(assessment["_id"]) not in submitted_ids
        ]
        
        # Get teacher names for each assessment
        result = []
        for assessment in upcoming_assessments:
            teacher = await db.users.find_one({"_id": ObjectId(assessment["created_by"])})
            teacher_name = teacher.get("name", "Unknown Teacher") if teacher else "Unknown Teacher"
            
            result.append(StudentAssessment(
                id=str(assessment["_id"]),
                title=assessment["title"],
                subject=assessment["subject"],
                difficulty=assessment["difficulty"],
                description=assessment["description"],
                time_limit=assessment["time_limit"],
                question_count=assessment["question_count"],
                type=assessment.get("type", "mcq"),
                is_active=assessment["is_active"],
                created_at=assessment["created_at"].isoformat(),
                teacher_name=teacher_name
            ))
        
        return result
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching upcoming assessments: {str(e)}")
        return []

@router.get("/{assessment_id}/questions")
async def get_assessment_questions(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Get questions for a specific assessment"""
    try:
        db = await get_db()
        
        # Get assessment details
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if student has access to this assessment
        student = await db.users.find_one({"_id": ObjectId(user.id)})
        if not student or not student.get("batch_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        batch_id = student["batch_id"]
        if batch_id not in assessment.get("assigned_batches", []):
            raise HTTPException(status_code=403, detail="Assessment not assigned to your batch")
        
        # Check if assessment is active
        if not assessment.get("is_active", False):
            raise HTTPException(status_code=400, detail="Assessment is not active")
        
        # Check if student has already submitted
        existing_submission = await db.assessment_submissions.find_one({
            "assessment_id": assessment_id,
            "student_id": user.id
        })
        
        if existing_submission:
            raise HTTPException(status_code=400, detail="Assessment already submitted")
        
        # Return assessment with questions
        return {
            "id": str(assessment["_id"]),
            "title": assessment["title"],
            "subject": assessment["subject"],
            "difficulty": assessment["difficulty"],
            "description": assessment["description"],
            "time_limit": assessment["time_limit"],
            "question_count": assessment["question_count"],
            "questions": assessment.get("questions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching assessment questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/submit")
async def submit_assessment_answers(
    assessment_id: str, 
    submission_data: dict, 
    user: UserModel = Depends(get_current_user)
):
    """Submit answers for a teacher-created assessment"""
    try:
        db = await get_db()
        
        # Get assessment details
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if student has access
        student = await db.users.find_one({"_id": ObjectId(user.id)})
        if not student or not student.get("batch_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        batch_id = student["batch_id"]
        if batch_id not in assessment.get("assigned_batches", []):
            raise HTTPException(status_code=403, detail="Assessment not assigned to your batch")
        
        # Check if already submitted (in both teacher and regular result collections)
        existing_submission = await db.assessment_submissions.find_one({
            "assessment_id": assessment_id,
            "student_id": user.id
        })
        if not existing_submission:
            existing_submission = await db.teacher_assessment_results.find_one({
            "assessment_id": assessment_id,
            "student_id": user.id
        })
        
        if existing_submission:
            raise HTTPException(status_code=400, detail="Assessment already submitted")
        
        # Calculate score
        questions = assessment.get("questions", [])
        answers = submission_data.get("answers", [])
        score = 0
        
        for i, question in enumerate(questions):
            if i < len(answers):
                user_answer = answers[i]
                correct_answer_index = question.get("correct_answer", -1)
                correct_answer = ""
                options = question.get("options", [])
                
                # Handle both string and integer correct answers
                if isinstance(correct_answer_index, int) and correct_answer_index >= 0:
                    if correct_answer_index < len(options):
                        correct_answer = options[correct_answer_index]
                else:
                    correct_answer = question.get("answer", "")
                
                # If correct answer is just a letter (A, B, C, D), map to option index
                if len(correct_answer) == 1 and correct_answer.isalpha():
                    letter = correct_answer.upper()
                    letter_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}
                    if letter in letter_to_index and letter_to_index[letter] < len(options):
                        correct_answer = options[letter_to_index[letter]]
                
                # Convert user answer to text if it's an index
                if isinstance(user_answer, int) and 0 <= user_answer < len(options):
                    user_answer_text = options[user_answer]
                else:
                    user_answer_text = str(user_answer)
                
                if user_answer_text == correct_answer:
                    score += 1
        
        percentage = (score / len(questions)) * 100 if questions else 0
        time_taken = submission_data.get("time_taken", 0)
        
        # Convert user answers to text format for question review
        user_answers_text = []
        for i, question in enumerate(questions):
            if i < len(answers):
                user_answer_raw = answers[i]
                options = question.get("options", [])
                
                # Convert to text if it's an index
                if isinstance(user_answer_raw, int) and 0 <= user_answer_raw < len(options):
                    user_answers_text.append(options[user_answer_raw])
                else:
                    user_answers_text.append(str(user_answer_raw))
            else:
                user_answers_text.append("")
        
        # Create submission record and ensure upcoming endpoints filter it out
        submission_doc = {
            "assessment_id": assessment_id,
            "student_id": user.id,
            "answers": answers,  # Keep original format
            "user_answers": user_answers_text,  # Add text format for review
            "questions": questions,  # Store questions for review
            "score": score,
            "percentage": round(percentage, 2),
            "time_taken": time_taken,
            "submitted_at": datetime.utcnow(),
            "is_completed": True
        }
        
        result = await db.assessment_submissions.insert_one(submission_doc)
        
        # Update student's progress
        await db.users.update_one(
            {"_id": ObjectId(user.id)},
            {
                "$inc": {
                    "completed_assessments": 1,
                    "total_score": score
                },
                "$set": {
                    "last_assessment_date": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "submission_id": str(result.inserted_id),
            "score": score,
            "percentage": round(percentage, 2),
            "total_questions": len(questions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error submitting assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/history")
async def get_student_assessment_history(user: UserModel = Depends(get_current_user)):
    """Get student's assessment submission history"""
    try:
        db = await get_db()
        
        # Get all results by this student from db.results collection
        results = await db.results.find({
            "user_id": ObjectId(user.id)
        }).sort("submitted_at", -1).to_list(length=None)
        
        # Get assessment details for each result
        history = []
        for result in results:
            history.append({
                "submission_id": str(result["_id"]),
                "assessment_id": str(result["_id"]),  # Use result ID as assessment ID for compatibility
                "title": result.get("test_name", "Test"),
                "subject": result.get("topic", ""),
                "difficulty": result.get("difficulty", "medium"),
                "score": result.get("score", 0),
                "percentage": (result.get("score", 0) / result.get("total_questions", 1)) * 100,
                "time_taken": result.get("time_spent", 0),
                "submitted_at": result.get("submitted_at", datetime.utcnow()).isoformat(),
                "total_questions": result.get("total_questions", 0)
            })
        
        return history
        
    except Exception as e:
        print(f"❌ [ASSESSMENT] Error fetching assessment history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


