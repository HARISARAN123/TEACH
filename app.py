import logging
import requests
from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def generate_question(subject, syllabus, grade, difficulty, count):
    """Generate detailed questions."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Generate {count} detailed questions for {subject} with syllabus {syllabus}, grade {grade}, and {difficulty} difficulty."
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

            questions = []
            for i, part in enumerate(question_parts, start=1):
                question_text = part.get('text', 'No question available')
                questions.append(question_text)

            logger.info(f"Questions generated: {questions}")
            return questions
        else:
            logger.warning("No candidates returned from the API.")
            return []

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return []

@app.route('/')
def home():
    """Render the home page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return jsonify({'error': 'An error occurred while rendering the page.'}), 500

@app.route('/question', methods=['GET', 'POST'])
def question():
    """Handle question generation and display."""
    if request.method == 'POST':
        subject = request.form.get('subject')
        syllabus = request.form.get('syllabus')
        grade = request.form.get('grade')
        difficulty = request.form.get('difficulty')
        count = int(request.form.get('count', 1))  # Default to 1 if not provided

        questions = generate_question(subject, syllabus, grade, difficulty, count)
        return render_template('question.html', questions=questions)

    return render_template('question.html')

@app.route('/doubt', methods=['GET', 'POST'])
def doubt():
    """Handle doubt resolution."""
    if request.method == 'POST':
        doubt = request.form.get('doubt')
        answer = generate_doubt_answer(doubt)
        return render_template('doubt.html', answer=answer)
    return render_template('doubt.html')

def generate_doubt_answer(doubt):
    """Generate an answer to a doubt."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Provide an answer to the following doubt: {doubt}"
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
            answer_parts = content.get('parts', [{}])
            answer_text = answer_parts[0].get('text', 'No answer available')

            return answer_text

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return "Error fetching answer. Please try again later."

if __name__ == '__main__':
    app.run(debug=True)
