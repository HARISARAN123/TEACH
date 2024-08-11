import logging
import re
import requests
from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def generate_quiz_question(subject, syllabus, grade, difficulty):
    """Generate a multiple-choice question (MCQ) with options A, B, C, D."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Generate a multiple-choice question (MCQ) with four options (A, B, C, D) for {subject} with syllabus {syllabus}, grade {grade}, and {difficulty} difficulty."
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        response.raise_for_status()

        response_data = response.json()
        if 'candidates' in response_data and response_data['candidates']:
            content = response_data['candidates'][0].get('content', {})
            question_parts = content.get('parts', [{}])
            question_text = question_parts[0].get('text', 'No question available')

            # Extract options and correct answer
            options = {}
            correct_option = ''
            for part in question_parts[1:]:
                option_text = part.get('text', '')
                match = re.match(r'^([A-D])\)\s*(.*)', option_text)
                if match:
                    options[match.group(1)] = match.group(2).strip()
                elif 'Answer' in option_text:
                    correct_option_match = re.search(r'Answer:\s*(\w)', option_text)
                    if correct_option_match:
                        correct_option = correct_option_match.group(1).upper()

            return question_text, options, correct_option

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return "Error fetching question. Please try again later.", {}, None

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
    """Handle quiz generation and answer verification."""
    if request.method == 'POST':
        subject = request.form.get('subject')
        syllabus = request.form.get('syllabus')
        grade = request.form.get('grade')
        difficulty = request.form.get('difficulty')
        user_answer = request.form.get('user_answer')
        correct_answer = request.form.get('correct_answer')
        question = request.form.get('question')

        if user_answer:
            if user_answer.strip().upper() == correct_answer.upper():
                feedback = "Correct answer!"
            else:
                feedback = f"Incorrect. The correct answer was: {correct_answer}"
            return render_template('quiz.html', feedback=feedback, question=question, options=None)

        question, options, correct_answer = generate_quiz_question(subject, syllabus, grade, difficulty)
        return render_template('quiz.html', question=question, options=options, correct_answer=correct_answer)

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
    app.run(debug=True)
