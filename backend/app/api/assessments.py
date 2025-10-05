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
    StudentNotification
)
from ..dependencies import require_teacher, require_admin, require_teacher_or_admin, require_student
from .auth import get_current_user
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
    
    # Use a combination of question number and topic to ensure variety
    import random
    random.seed(hash(f"{topic}_{question_num}"))
    selected_question = random.choice(questions)
    
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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        import jwt
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = await get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Assessment Management Endpoints

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(assessment_data: AssessmentCreate, user: dict = Depends(require_teacher)):
    """Create a new assessment - Teacher/Admin only"""
    try:
        db = await get_db()
        
        assessment_doc = {
            "title": assessment_data.title,
            "topic": assessment_data.topic,
            "difficulty": assessment_data.difficulty,
            "description": assessment_data.description,
            "time_limit": assessment_data.time_limit,
            "max_attempts": assessment_data.max_attempts,
            "type": getattr(assessment_data, 'type', 'mcq'),  # Default to 'mcq' if not specified
            "created_by": str(user["_id"]),
            "created_at": datetime.utcnow(),
            "status": "draft",
            "question_count": 0,
            "questions": [],
            "assigned_batches": []
        }
        
        result = await db.assessments.insert_one(assessment_doc)
        
        return AssessmentResponse(
            id=str(result.inserted_id),
            title=assessment_data.title,
            topic=assessment_data.topic,
            difficulty=assessment_data.difficulty,
            description=assessment_data.description,
            time_limit=assessment_data.time_limit,
            max_attempts=assessment_data.max_attempts,
            question_count=0,
            created_by=str(user["_id"]),
            created_at=assessment_doc["created_at"].isoformat(),
            status="draft",
            type=assessment_doc["type"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AssessmentResponse])
async def get_teacher_assessments(user: dict = Depends(get_current_user)):
    """Get all assessments created by the teacher"""
    try:
        db = await get_db()
        
        if user.get("role") != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can view assessments")
        
        assessments_cursor = await db.assessments.find({"created_by": str(user["_id"])}).to_list(None)
        assessments = []
        
        for assessment in assessments_cursor:
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

@router.post("/{assessment_id}/questions", response_model=QuestionResponse)
async def add_question_to_assessment(
    assessment_id: str, 
    question_data: QuestionCreate, 
    user: dict = Depends(require_teacher)
):
    """Add a question to an assessment"""
    try:
        db = await get_db()
        
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Check if assessment exists and belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id), 
            "created_by": str(user["_id"])
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
    user: dict = Depends(get_current_user)
):
    """Add a coding question to an assessment"""
    try:
        print(f"[DEBUG] [BACKEND] Received coding question data: {question_data}")
        print(f"[DEBUG] [BACKEND] Assessment ID: {assessment_id}")
        print(f"[DEBUG] [BACKEND] User: {user}")
        
        db = await get_db()
        
        if user.get("role") != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can add coding questions")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if assessment.get("created_by") != str(user["_id"]):
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
    user: dict = Depends(get_current_user)
):
    """Generate questions using AI for an assessment"""
    try:
        print(f"[AI] [AI GENERATION] Received request for assessment {assessment_id}")
        print(f"[AI] [AI GENERATION] Generation data: {generation_data}")
        
        db = await get_db()
        
        if user.get("role") != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can generate AI questions")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if assessment.get("created_by") != str(user["_id"]):
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
async def publish_assessment(assessment_id: str, user: dict = Depends(get_current_user)):
    """Publish an assessment and assign to batches"""
    try:
        db = await get_db()
        
        if user.get("role") != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can publish assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Check if assessment exists and belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id), 
            "created_by": str(user["_id"])
        })
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if len(assessment.get("questions", [])) == 0:
            raise HTTPException(status_code=400, detail="Assessment must have at least one question")
        
        # Update assessment status
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$set": {"status": "published", "published_at": datetime.utcnow()}}
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
                    notification = {
                        "student_id": student_id,
                        "type": "assessment_assigned",
                        "title": f"New Assessment: {assessment['title']}",
                        "message": f"A new {assessment['difficulty']} assessment on {assessment['topic']} has been assigned to you.",
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
    user: dict = Depends(get_current_user)
):
    """Assign assessment to specific batches"""
    try:
        db = await get_db()
        
        if user.get("role") != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can assign assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Validate batch IDs
        valid_batch_ids = []
        for batch_id in batch_ids:
            if ObjectId.is_valid(batch_id):
                batch = await db.batches.find_one({
                    "_id": ObjectId(batch_id), 
                    "teacher_id": str(user["_id"])
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
async def get_available_assessments(user: dict = Depends(get_current_user)):
    """Get assessments available to the student"""
    try:
        db = await get_db()
        
        if user.get("role") != "student":
            raise HTTPException(status_code=403, detail="Only students can view available assessments")
        
        # Get student's batch
        student_batches = await db.batches.find({"student_ids": str(user["_id"])}).to_list(None)
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
                "student_id": str(user["_id"])
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
async def get_assessment_questions(assessment_id: str, user: dict = Depends(get_current_user)):
    """Get questions for an assessment (for taking the test)"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if student has access to this assessment
        if user.get("role") == "student":
            student_batches = await db.batches.find({"student_ids": str(user["_id"])}).to_list(None)
            batch_ids = [str(batch["_id"]) for batch in student_batches]
            
            if not any(batch_id in assessment.get("assigned_batches", []) for batch_id in batch_ids):
                raise HTTPException(status_code=403, detail="Access denied")
        
        questions = []
        for i, question in enumerate(assessment.get("questions", [])):
            # For students, don't include correct answers
            if user.get("role") == "student":
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
    user: dict = Depends(get_current_user)
):
    """Submit an assessment"""
    try:
        db = await get_db()
        
        if user.get("role") != "student":
            raise HTTPException(status_code=403, detail="Only students can submit assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if student has access
        student_batches = await db.batches.find({"student_ids": str(user["_id"])}).to_list(None)
        batch_ids = [str(batch["_id"]) for batch in student_batches]
        
        if not any(batch_id in assessment.get("assigned_batches", []) for batch_id in batch_ids):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check attempt limit
        existing_results = await db.assessment_results.find({
            "assessment_id": assessment_id,
            "student_id": str(user["_id"])
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
                
                # Handle both string and integer correct answers
                if isinstance(correct_answer_index, int) and correct_answer_index >= 0:
                    options = question.get("options", [])
                    if correct_answer_index < len(options):
                        correct_answer = options[correct_answer_index]
                else:
                    correct_answer = question.get("answer", "")
                
                if user_answer == correct_answer:
                    score += question.get("points", 1)
        
        percentage = (score / sum(q.get("points", 1) for q in questions)) * 100 if questions else 0
        
        # Create result
        result_doc = {
            "assessment_id": assessment_id,
            "student_id": str(user["_id"]),
            "student_name": user.get("name") or user.get("username") or user.get("email"),
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "time_taken": submission.time_taken,
            "submitted_at": datetime.utcnow(),
            "attempt_number": len(existing_results) + 1,
            "answers": submission.answers
        }
        
        result = await db.assessment_results.insert_one(result_doc)
        
        # Create notification for student about result
        notification = {
            "student_id": str(user["_id"]),
            "type": "result_available",
            "title": f"Assessment Result: {assessment['title']}",
            "message": f"Your assessment result is available. Score: {score}/{sum(q.get('points', 1) for q in questions)} ({percentage:.1f}%)",
            "assessment_id": assessment_id,
            "created_at": datetime.utcnow(),
            "is_read": False
        }
        await db.notifications.insert_one(notification)
        
        # Update user gamification data
        await update_user_progress(db, str(user["_id"]), score, percentage, total_questions)
        
        return AssessmentResult(
            id=str(result.inserted_id),
            assessment_id=assessment_id,
            student_id=str(user["_id"]),
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
async def get_assessment_leaderboard(assessment_id: str, user: dict = Depends(get_current_user)):
    """Get leaderboard for an assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if user has access to this assessment
        if user.get("role") == "student":
            student_batches = await db.batches.find({"student_ids": str(user["_id"])}).to_list(None)
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
async def get_student_notifications(user: dict = Depends(get_current_user)):
    """Get notifications for a student"""
    try:
        db = await get_db()
        
        if user.get("role") != "student":
            raise HTTPException(status_code=403, detail="Only students can view notifications")
        
        notifications_cursor = await db.notifications.find({
            "student_id": str(user["_id"])
        }).sort("created_at", -1).to_list(None)
        
        notifications = []
        for notification in notifications_cursor:
            notification_response = StudentNotification(
                id=str(notification["_id"]),
                student_id=notification["student_id"],
                type=notification["type"],
                title=notification["title"],
                message=notification["message"],
                assessment_id=notification.get("assessment_id"),
                created_at=notification["created_at"].isoformat(),
                is_read=notification.get("is_read", False)
            )
            notifications.append(notification_response)
        
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user: dict = Depends(get_current_user)):
    """Mark a notification as read"""
    try:
        db = await get_db()
        
        if user.get("role") != "student":
            raise HTTPException(status_code=403, detail="Only students can mark notifications as read")
        
        if not ObjectId.is_valid(notification_id):
            raise HTTPException(status_code=400, detail="Invalid notification ID")
        
        await db.notifications.update_one(
            {"_id": ObjectId(notification_id), "student_id": str(user["_id"])},
            {"$set": {"is_read": True}}
        )
        
        return {"success": True, "message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/coding-submit", response_model=CodingSubmissionResponse)
async def submit_coding_solution(
    assessment_id: str,
    submission_data: CodingSubmission,
    user: dict = Depends(get_current_user)
):
    """Submit a coding solution for a coding question"""
    try:
        db = await get_db()
        
        if user.get("role") != "student":
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
            "student_id": str(user["_id"]),
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
async def get_assessment_details(assessment_id: str, user: dict = Depends(get_current_user)):
    """Get detailed assessment information including questions"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if user has access to this assessment
        if user.get("role") == "teacher" and assessment.get("created_by") != str(user["_id"]):
            raise HTTPException(status_code=403, detail="You can only view your own assessments")
        
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
            "created_at": assessment["created_at"].isoformat(),
            "status": assessment["status"],
            "type": assessment.get("type", "mcq"),
            "questions": assessment.get("questions", [])  # Include questions in response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

