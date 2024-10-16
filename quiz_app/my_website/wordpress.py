from flask import Blueprint, render_template, flash, url_for, request, redirect, session, jsonify, json
from flask_login import login_required
from . import basic_auth


wordpress = Blueprint("wordpress", __name__)

QUESTIONS_FILE = "wordpress.json"

def load_questions():
    try:
        with open(QUESTIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_questions(questions):
    with open(QUESTIONS_FILE, "w") as f:
        json.dump(questions, f)

@wordpress.route("/api/v1/wordpress/add", methods=["POST"])
@basic_auth.required
def add_question():
    question_data = request.get_json()

    # Validate the question data
    if not all(key in question_data for key in ["question", "options", "correct_answer"]):
        return jsonify(success=False, error="Invalid question data")

    # Load existing questions
    questions = load_questions()

    # Add the question to the list of questions
    questions.append(question_data)

    # Save the updated questions
    save_questions(questions)

    return jsonify(success=True)

@wordpress.route("/api/v1/wordpress/", methods=["GET"])
@basic_auth.required
def get_questions():
    questions = load_questions()
    return jsonify(questions)


@wordpress.route('quiz/quizzes/wordpress', methods=["GET", "POST"])
@login_required
def quiz():
    if "score" not in session:
        session["score"] = 0
        session["total"] = 0

    if request.method == "POST":
        selected_answer = request.form.get("answer")
        question_index = int(request.form.get("question_index"))

        questions = load_questions()

        if selected_answer == questions[question_index]["correct_answer"]:
            session["score"] += 1
            flash("Correct! 🎉")
        else:
            flash("Incorrect. The correct answer is: " + questions[question_index]["correct_answer"])

        session["total"] += 1
        question_index += 1

        if question_index >= len(questions):
            return redirect(url_for("wordpress.show_score"))

        return render_template("quizzes/python.html", question=questions[question_index], question_index=question_index, score=session["score"], total=session["total"], course="WordPress")

    session["score"] = 0
    session["total"] = 0
    questions = load_questions()
    return render_template("quizzes/python.html", question=questions[0], question_index=0, score=session["score"], total=session["total"], course="WordPress")


@wordpress.route("/score")
@login_required
def show_score():
    score = session.pop("score", 0)
    total = session.pop("total", 0)
    return render_template('quizzes/score.html', score=score, total=total)
