import pymongo
from scoreCalculate import calculate_new_cgpa,calculate_subject_gpa,calculate_cgpa,analyze_gpa_trend,detect_strengths_weaknesses

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

studentdb = myclient["Student"]
studcol = studentdb["StudentDetails"]

# DataBase Schema
"""
details = {
    "id": studid,
    "name": <name of the student>,
    "age": <age of the student>,
    "NoOfTests": [<ofCourse1>, <ofCourse2> ...],
    "courses": [<course 1>, <course 2> ...],
    "gpa": [<ofCourse1>, <ofCourse2> ...]
}
"""

def putStudDetails(studid, details):
    # Insert the whole details object directly
    studcol.insert_one(details)

def updateStudGPA(studid, new_gpas):
    # new_gpas should be a list matching the order of courses
    studcol.update_one(
        {"id": studid},
        {"$set": {"gpa": new_gpas}}
    )


def updateStudGPA(studid, new_scores_by_course):
    student = studcol.find_one({"id": studid})
    if not student:
        print("Student not found.")
        return

    courses = student["courses"]
    gpas = student["gpa"]
    no_of_tests = student["NoOfTests"]

    updated_gpas = []
    new_gpa_per_course = {}

    for i, course in enumerate(courses):
        if course in new_scores_by_course:
            old_gpa = gpas[i]
            prev_attempts = no_of_tests[i]
            new_score = new_scores_by_course[course]  # already a float like 0.85
            new_gpa = round(new_score * 10, 2)

            # Update course GPA
            updated = calculate_new_cgpa(old_gpa, prev_attempts, new_gpa)
            updated_gpas.append(updated)
            new_gpa_per_course[course] = updated
            no_of_tests[i] += 1
        else:
            # If no new score provided, keep old GPA
            updated_gpas.append(gpas[i])

    # Recalculate CGPA
    current_avg_gpa = round(sum(updated_gpas) / len(updated_gpas), 2)
    previous_cgpa = student.get("cgpa", 0.0)
    previous_attempts = student.get("cgpa_attempts", 0)
    new_cgpa = calculate_cgpa(previous_cgpa, previous_attempts, current_avg_gpa)

    # GPA Trend Analysis
    gpa_history = student.get("gpa_history", [])
    gpa_history.append(current_avg_gpa)
    trend = analyze_gpa_trend(gpa_history)

    # Strengths and Weaknesses
    subject_analysis = detect_strengths_weaknesses(new_gpa_per_course)

    # Update in DB
    studcol.update_one(
        {"id": studid},
        {"$set": {
            "gpa": updated_gpas,
            "NoOfTests": no_of_tests,
            "cgpa": new_cgpa,
            "cgpa_attempts": previous_attempts + 1,
            "gpa_history": gpa_history,
            "gpa_trend": trend,
            "subject_analysis": subject_analysis
        }}
    )

    print("Student GPA and CGPA updated.")
