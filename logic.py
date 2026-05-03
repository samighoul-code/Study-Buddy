"""
منطق التحقق من الإجابات وحساب النقاط
Answer checking and score calculation logic
"""

def check_answer(questions, question_index, selected_index):
    """التحقق من صحة الإجابة المختارة"""
    question = questions[question_index]
    correct_index = question["correct_index"]
    correct = (selected_index == correct_index)
    return {
        "correct": correct,
        "correct_index": correct_index,
        "explanation": question.get("explanation", ""),
    }


def calculate_score(total, score):
    """حساب النسبة المئوية وتقييم الأداء"""
    if total == 0:
        return 0, "لم يتم الإجابة على أي سؤال"
    percentage = round((score / total) * 100)
    if percentage >= 90:
        performance = "ممتاز! أنت نجم 🌟"
    elif percentage >= 75:
        performance = "جيد جداً! استمر 👍"
    elif percentage >= 60:
        performance = "جيد! يمكنك التحسن 💪"
    else:
        performance = "تحتاج إلى مزيد من التدريب 📚"
    return percentage, performance
