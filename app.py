from flask import Flask, render_template, request, jsonify
import os
import random
import re
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
import time
import openai

app = Flask(__name__)
openai.api_key = "YOUR_API_KEY"  # Replace with your actual OpenAI API key

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Process the uploaded audio file and generate questions and answers
    try:
        response = convert_speech_and_generate_qa(file_path)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_file_length(file_path):
    audio = AudioSegment.from_file(file_path)
    return audio.duration_seconds

def convert_speech_and_generate_qa(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    random.seed(time.time())
    energy_threshold = random.randint(3000, 5000)
    r.energy_threshold = energy_threshold

    random.seed(time.time())
    pause_threshold = round(random.uniform(0.6, 1.0), 1)
    r.pause_threshold = pause_threshold

    random.seed(time.time())
    silence_threshold = random.randint(500, 1500)
    r.silence_threshold = silence_threshold

    language = 'en-US'

    try:
        text = r.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "Google speech recognition could not understand audio"
    except sr.RequestError:
        return "Couldn't get results from Google Speech Recognition"

    clean_text = re.sub(r'\s+', ' ', text).strip()
    clean_text_no_punctuation = re.sub(r'[^\w\s]', '', clean_text)

    num_questions = 5
    api_response = question_gen(clean_text_no_punctuation, num_questions)

    return {
        "transcribed_text": clean_text_no_punctuation,
        "questions_and_answers": api_response,
        "file_length": get_file_length(file_path),
    }

def create_options(rawtext, num_questions):
    messages = [
        {"role": "user", "content": f"Give me {num_questions} questions with 4 options followed by answers for the following content:\n{rawtext}\nJust display the questions and answers, nothing else."},
    ]

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    reply = chat.choices[0].message.content
    return reply

def question_gen(rawtext, num_questions):
    reply = create_options(rawtext, num_questions)
    return reply

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
