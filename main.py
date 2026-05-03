"""
تطبيق رياضيات للمرحلة المتوسطة - الصفوف 7-9
Math Learning Platform for Middle School Students
"""

from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "math-edu-secret-2024"

# ---- مساعدات تحميل البيانات ----

def load_questions():
    """تحميل بنك الأسئلة من ملف JSON"""
    with open("data/questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_student():
    """تحميل بيانات الطالب من ملف JSON"""
    with open("data/student.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_student(data):
    """حفظ بيانات الطالب في ملف JSON"""
    with open("data/student.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_level_info(points):
    """احسب مستوى الطالب بناءً على النقاط"""
    if points < 50:
        return {"level": 1, "title": "مبتدئ 🌱", "next": 50, "color": "#6B7280"}
    elif points < 150:
        return {"level": 2, "title": "متعلم 📚", "next": 150, "color": "#059669"}
    elif points < 300:
        return {"level": 3, "title": "متقدم ⭐", "next": 300, "color": "#D97706"}
    elif points < 500:
        return {"level": 4, "title": "متميز 🏆", "next": 500, "color": "#7C3AED"}
    else:
        return {"level": 5, "title": "خبير 🎓", "next": None, "color": "#DC2626"}

def check_badges(student):
    """تحقق من الأوسمة الجديدة"""
    badges = student.get("badges", [])
    new_badges = []

    completed  = len(student.get("completed_exercises", []))
    tasks_done = sum(1 for t in student.get("tasks", []) if t.get("status") == "done")
    points     = student.get("points", 0)

    badge_rules = [
        {"id": "first_exercise", "name": "أول تمرين 🌟",  "condition": completed >= 1},
        {"id": "five_exercises",  "name": "خمسة تمارين 🔥","condition": completed >= 5},
        {"id": "ten_exercises",   "name": "عشرة تمارين 💎","condition": completed >= 10},
        {"id": "first_task",      "name": "أول مهمة ✅",   "condition": tasks_done >= 1},
        {"id": "five_tasks",      "name": "خمس مهام 📅",   "condition": tasks_done >= 5},
        {"id": "fifty_points",    "name": "50 نقطة 🥉",    "condition": points >= 50},
        {"id": "hundred_points",  "name": "100 نقطة 🥈",   "condition": points >= 100},
        {"id": "threehundred",    "name": "300 نقطة 🥇",   "condition": points >= 300},
    ]

    existing_ids = [b["id"] for b in badges]
    for rule in badge_rules:
        if rule["condition"] and rule["id"] not in existing_ids:
            badges.append({"id": rule["id"], "name": rule["name"]})
            new_badges.append(rule["name"])

    student["badges"] = badges
    return student, new_badges


# ---- المسارات (Routes) ----

@app.route("/")
def dashboard():
    """الشاشة الرئيسية - لوحة التحكم"""
    student        = load_student()
    questions_data = load_questions()
    level_info     = get_level_info(student["points"])

    # نسبة التقدم نحو المستوى التالي
    if level_info["next"]:
        prev_threshold = [0, 50, 150, 300][level_info["level"] - 1]
        progress_pct   = int(
            (student["points"] - prev_threshold) /
            (level_info["next"] - prev_threshold) * 100
        )
    else:
        progress_pct = 100

    # إحصاءات المهام
    tasks          = student.get("tasks", [])
    tasks_todo     = sum(1 for t in tasks if t.get("status") == "todo")
    tasks_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
    tasks_done     = sum(1 for t in tasks if t.get("status") == "done")

    return render_template(
        "dashboard.html",
        student=student,
        level_info=level_info,
        progress_pct=min(progress_pct, 100),
        topics=questions_data["topics"],
        tasks_todo=tasks_todo,
        tasks_progress=tasks_progress,
        tasks_done=tasks_done,
        total_topics=len(questions_data["topics"]),
    )


@app.route("/math")
def math():
    """شاشة اختيار المواضيع الرياضية"""
    student        = load_student()
    questions_data = load_questions()
    level_info     = get_level_info(student["points"])

    completed    = student.get("completed_exercises", [])
    topic_stats  = {}
    for topic in questions_data["topics"]:
        done = sum(1 for e in completed if e.get("topic_id") == topic["id"])
        topic_stats[topic["id"]] = {"done": done, "total": len(topic["questions"])}

    return render_template(
        "math.html",
        student=student,
        level_info=level_info,
        topics=questions_data["topics"],
        topic_stats=topic_stats,
    )


@app.route("/topic/<topic_id>")
def topic(topic_id):
    """شاشة أسئلة موضوع معين"""
    student        = load_student()
    questions_data = load_questions()
    level_info     = get_level_info(student["points"])

    topic_data = next((t for t in questions_data["topics"] if t["id"] == topic_id), None)
    if not topic_data:
        return redirect(url_for("math"))

    completed     = student.get("completed_exercises", [])
    completed_ids = [e["question_id"] for e in completed if e.get("topic_id") == topic_id]

    return render_template(
        "topic.html",
        student=student,
        level_info=level_info,
        topic=topic_data,
        completed_ids=completed_ids,
    )


@app.route("/api/answer", methods=["POST"])
def api_answer():
    """معالجة إجابة الطالب على سؤال"""
    data        = request.get_json()
    topic_id    = data.get("topic_id")
    question_id = int(data.get("question_id"))
    selected    = int(data.get("selected_index"))

    questions_data = load_questions()
    student        = load_student()

    topic_data = next((t for t in questions_data["topics"] if t["id"] == topic_id), None)
    if not topic_data:
        return jsonify({"error": "موضوع غير موجود"}), 404

    question = next((q for q in topic_data["questions"] if q["id"] == question_id), None)
    if not question:
        return jsonify({"error": "سؤال غير موجود"}), 404

    correct   = (selected == question["correct_index"])
    completed = student.get("completed_exercises", [])

    already_done = any(
        e.get("topic_id") == topic_id and e.get("question_id") == question_id
        for e in completed
    )

    points_earned = 0
    new_badges    = []

    if not already_done:
        points_map = {"سهل": 10, "متوسط": 20, "صعب": 30}
        if correct:
            points_earned       = points_map.get(question.get("difficulty", "سهل"), 10)
            student["points"]   = student.get("points", 0) + points_earned

        completed.append({
            "topic_id":    topic_id,
            "question_id": question_id,
            "correct":     correct,
            "timestamp":   datetime.now().isoformat()
        })
        student["completed_exercises"] = completed
        student, new_badges = check_badges(student)
        save_student(student)

    level_info = get_level_info(student["points"])

    return jsonify({
        "correct":       correct,
        "correct_index": question["correct_index"],
        "explanation":   question["explanation"],
        "points_earned": points_earned,
        "total_points":  student["points"],
        "new_badges":    new_badges,
        "level":         level_info["level"],
        "already_done":  already_done,
    })


@app.route("/tasks")
def tasks():
    """شاشة إدارة المهام"""
    student    = load_student()
    level_info = get_level_info(student["points"])
    task_list  = student.get("tasks", [])

    priority_order = {"عالية": 0, "متوسطة": 1, "منخفضة": 2}
    task_list = sorted(task_list, key=lambda t: priority_order.get(t.get("priority", "متوسطة"), 1))

    return render_template(
        "tasks.html",
        student=student,
        level_info=level_info,
        tasks=task_list,
    )


@app.route("/api/tasks/add", methods=["POST"])
def add_task():
    """إضافة مهمة جديدة"""
    data    = request.get_json()
    student = load_student()

    task = {
        "id":       int(datetime.now().timestamp() * 1000),
        "title":    data.get("title", "مهمة جديدة"),
        "subject":  data.get("subject", "عام"),
        "due_date": data.get("due_date", ""),
        "priority": data.get("priority", "متوسطة"),
        "status":   "todo",
        "created":  datetime.now().isoformat(),
    }

    tasks = student.get("tasks", [])
    tasks.append(task)
    student["tasks"] = tasks
    student, _ = check_badges(student)
    save_student(student)

    return jsonify({"success": True, "task": task})


@app.route("/api/tasks/update", methods=["POST"])
def update_task():
    """تحديث حالة مهمة"""
    data       = request.get_json()
    task_id    = int(data.get("id"))
    new_status = data.get("status")

    student = load_student()
    tasks   = student.get("tasks", [])

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = new_status
            break

    student["tasks"]    = tasks
    student, new_badges = check_badges(student)
    save_student(student)

    return jsonify({"success": True, "new_badges": new_badges})


@app.route("/api/tasks/delete", methods=["POST"])
def delete_task():
    """حذف مهمة"""
    data    = request.get_json()
    task_id = int(data.get("id"))

    student          = load_student()
    student["tasks"] = [t for t in student.get("tasks", []) if t["id"] != task_id]
    save_student(student)

    return jsonify({"success": True})


@app.route("/api/student/name", methods=["POST"])
def update_name():
    """تحديث اسم الطالب"""
    data = request.get_json()
    name = data.get("name", "").strip()
    if name:
        student         = load_student()
        student["name"] = name
        save_student(student)
        return jsonify({"success": True})
    return jsonify({"success": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
