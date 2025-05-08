from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Load questions from text files
def load_questions(category):
    file_path = f"questions/{category}.txt"
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().split("<question>")
    
    questions = []
    for t in text[1:]:  # Skip the first split (empty before the first <question>)
        lines = t.strip().split("\n")
        question_text = lines[0].strip()
        options = [line[8:].strip() if line.startswith("<variant>") else line[13:].strip() for line in lines[1:]]
        correct = [opt for opt in lines if "<variantright>" in opt][0][13:].strip()
        questions.append({"question": question_text, "options": options, "correct": correct})
    
    return questions

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/quiz/<category>", methods=["GET", "POST"])
def quiz(category):
    # Load questions for the selected category
    questions = load_questions(category)
    if not questions:
        return f"No questions available for category: {category}", 404

    # Track the current question and score
    current_question = int(request.args.get("q", 0))
    score = int(request.args.get("score", 0))
    feedback = request.args.get("feedback", "")  # Retrieve feedback if available

    if request.method == "POST":
        if "restart" in request.form:
            # Restart the quiz
            return redirect(url_for("quiz", category=category, q=0, score=0))

        if "change_category" in request.form:
            # Change category
            new_category = request.form.get("category")
            return redirect(url_for("quiz", category=new_category, q=0, score=0))

        # Get the user's answer
        selected_option = request.form.get("answer")
        correct_answer = questions[current_question]["correct"]

        # Check if the answer is correct
        if selected_option == correct_answer:
            score += 1
            feedback = "Correct!"
        else:
            feedback = f"Wrong! The correct answer was: {correct_answer}"

        # Move to the next question
        current_question += 1
        if current_question >= len(questions):
            # Quiz finished
            return render_template("quiz.html", finished=True, score=score, total=len(questions))

        # Redirect to the next question with feedback
        return redirect(
            url_for("quiz", category=category, q=current_question, score=score, feedback=feedback)
        )

    # Render the quiz page
    return render_template(
        "quiz.html",
        question=questions[current_question]["question"],
        options=questions[current_question]["options"],
        current_question=current_question + 1,
        total_questions=len(questions),
        feedback=feedback,
        score=score,
        category=category,
    )


if __name__ == "__main__":
    app.run()
