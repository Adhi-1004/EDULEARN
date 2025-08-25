def calculate_new_cgpa(previous_cgpa, previous_attempts, current_gpa):
    total_score = (previous_cgpa * previous_attempts) + current_gpa
    total_attempts = previous_attempts + 1
    new_cgpa = round(total_score / total_attempts, 2)
    return new_cgpa



def calculate_subject_gpa(scores):
    return round((sum(scores) / len(scores)) * 10, 2) if scores else 0.0




def calculate_cgpa(previous_cgpa, previous_attempts, current_gpa):
    total = previous_cgpa * previous_attempts + current_gpa
    return round(total / (previous_attempts + 1), 2)





def detect_strengths_weaknesses(subject_gpas):
    strengths = [s for s, g in subject_gpas.items() if g >= 8.0]
    weaknesses = [s for s, g in subject_gpas.items() if g < 6.0]
    return {"strengths": strengths, "weaknesses": weaknesses}




def analyze_gpa_trend(gpa_history):
    if len(gpa_history) < 2:
        return "Not enough data"
    if gpa_history[-1] > gpa_history[-2]:
        return "Improving"
    elif gpa_history[-1] < gpa_history[-2]:
        return "Declining"
    return "Stable"






def calculate_confidence(qtype_scores):
    def label(score): return "High" if score >= 8 else "Medium" if score >= 6 else "Low"
    return {
        qtype: {
            "accuracy": f"{(sum(scores) / len(scores)) * 100:.1f}%",
            "confidence": label((sum(scores) / len(scores)) * 10)
        } for qtype, scores in qtype_scores.items() if scores
    }





def calculate_topic_mastery(topic_scores):
    mastery = {}
    for topic, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        if avg >= 0.8: mastery[topic] = "Strong"
        elif avg >= 0.5: mastery[topic] = "Moderate"
        else: mastery[topic] = "Weak"
    return mastery





def predict_next_gpa(gpa_history):
    return round(sum(gpa_history[-3:]) / min(len(gpa_history), 3), 2)





def generate_alerts(subject_gpas, gpa_trends):
    alerts = []
    for subj, trend in gpa_trends.items():
        if trend == "Declining":
            alerts.append(f"GPA dropped in {subj}. Consider reviewing.")
        elif subject_gpas[subj] >= 8 and trend == "Improving":
            alerts.append(f"Great improvement in {subj}! 🎉")
    return alerts
