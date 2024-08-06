import logging
import re
import requests
from flask import Flask, request, render_template, redirect, url_for, jsonify
import os

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def format_bold(text):
    """Convert **text** to <strong>text</strong>."""
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

def generate_quiz_question(subject, syllabus, grade, difficulty):
    """Generate a quiz question based on the subject, syllabus, grade, and difficulty."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": f"Generate a quiz question for {subject} with syllabus {syllabus}, grade {grade}, and {difficulty} difficulty"}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        response.raise_for_status()

        response_data = response.json()
        question = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No question available')
        answer = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[1].get('text', 'No answer available')  # Fetching answer here
        formatted_question = format_bold(question)
        return formatted_question, answer

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return "Error fetching question. Please try again later.", None

def generate_doubt_answer(doubt):
    """Generate an answer for a given doubt."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": f"Answer the following question in detail: {doubt}"}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        response.raise_for_status()

        response_data = response.json()
        answer = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No answer available')
        formatted_answer = format_bold(answer)
        return formatted_answer

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return "Error fetching answer. Please try again later."

@app.route('/')
def home():
    """Render the home page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return jsonify({'error': 'An error occurred while rendering the page.'}), 500

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Handle quiz generation."""
    if request.method == 'POST':
        if 'submit_answer' in request.form:
            user_answer = request.form.get('user_answer')
            correct_answer = request.form.get('correct_answer')
            if user_answer.strip().lower() == correct_answer.strip().lower():
                feedback = "Correct!"
            else:
                feedback = f"Wrong! The correct answer was: {correct_answer}"
            return render_template('quiz.html', feedback=feedback)

        subject = request.form.get('subject')
        syllabus = request.form.get('syllabus')
        grade = request.form.get('grade')
        difficulty = request.form.get('difficulty')
        question, correct_answer = generate_quiz_question(subject, syllabus, grade, difficulty)
        if correct_answer:
            return render_template('quiz.html', question=question, correct_answer=correct_answer)
        return render_template('quiz.html', question=question)

    return render_template('quiz.html')

@app.route('/doubt', methods=['GET', 'POST'])
def doubt():
    """Handle doubt resolution."""
    if request.method == 'POST':
        doubt = request.form.get('doubt')
        answer = generate_doubt_answer(doubt)
        return render_template('doubt.html', answer=answer)
    return render_template('doubt.html')

if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
