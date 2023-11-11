import os
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from pydub import AudioSegment
import pdfkit
import tempfile
import openai
import speech_recognition as sr
import time
import random
import re

openai.api_key = "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"

def get_file_length(file_path):
    audio = AudioSegment.from_file(file_path)
    duration = audio.duration_seconds
    return duration

def convert_speech_and_generate_qa():
    file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])

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

    random.seed(time.time())
    duration_threshold = round(random.uniform(1.0, 2.5), 1)

    random.seed(time.time())
    language = 'en-US'

    try:
        text = r.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        text = "Google speech recognition could not understand audio"
    except sr.RequestError:
        text = "Couldn't get results from Google Speech Recognition"

    word_count = len(text.split())

    clean_text = re.sub(r'\s+', ' ', text).strip()
    clean_text_no_punctuation = re.sub(r'[^\w\s]', '', clean_text)
    clean_text_no_punctuation = re.sub(r'\s+', ' ', clean_text_no_punctuation)

    num_questions = 5

    api_response = question_gen(clean_text_no_punctuation, num_questions)

    update_window(file_path, clean_text_no_punctuation, api_response, word_count)

    file_name = 'para.txt'
    with open(file_name, 'w') as file:
        file.write(clean_text_no_punctuation)
        print("Text written to file:", file_name)


    file_length = get_file_length(file_path)
    file_length_label.config(text=f"File Length: {file_length:.2f} seconds")

def create_options(rawtext, num_questions):
    messages = [
        {"role": "user", "content": f"Give me 5 questions with 4 options leave a line and then FOLLOWED by ANSWERS for the following content:\n{rawtext} \n just display the questions and answers nothing else "},
    ]

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    reply = chat.choices[0].message.content

    #raw API response on termi
    print("API Response:")
    print(reply)

    return reply


def question_gen(rawtext, num_questions):
    reply = create_options(rawtext, num_questions)
    return reply


def update_window(file_path, speech_to_text, api_response, word_count):
    # Clear the existing content in the window
    text_output.delete(1.0, tk.END)
    qa_output.delete(1.0, tk.END)

    # Update the S to T output
    text_output.insert(tk.END, speech_to_text)

    # Update the word count
    word_count_label.config(text=f"Word Count: {word_count}")

    # Update the QA output with the API response
    qa_output.insert(tk.END, api_response)

    # Update the file path label
    file_label.config(text=f"Selected File: {file_path}")


def create_pdf():

    api_response = qa_output.get(1.0, tk.END)


    api_response = api_response.replace("Answer:", "\nAnswer:")

    # Create a temporary HTML file with the formatted content
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
        temp_file.write("<html><body>".encode("utf-8"))
        temp_file.write(api_response.encode("utf-8"))
        temp_file.write("</body></html>".encode("utf-8"))
        temp_file.flush()  # Flush the file to ensure its content is written

        # Generate PDF from the HTML file
        pdf_file = temp_file.name.replace(".html", ".pdf")

        # Specify the path to the wkhtmltopdf executable
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

        pdfkit.from_file(temp_file.name, pdf_file, configuration=config)

    # Open the generated PDF file
    import platform
    if platform.system() == "Darwin":  # macOS
        import subprocess
        subprocess.call(["open", pdf_file])
    elif platform.system() == "Windows":  # Windows
        os.startfile(pdf_file)
    else:  # other systems
        import webbrowser
        webbrowser.open_new_tab(pdf_file)


root = tk.Tk()
root.title("Speech to Text and Question Generation")
root.geometry("800x600")

file_label = tk.Label(root, text="Selected File: ")
file_label.pack()

file_length_label = tk.Label(root, text="File Length: ")
file_length_label.pack()

text_label = tk.Label(root, text="Speech to Text: ")
text_label.pack()

text_output = scrolledtext.ScrolledText(root, height=5, width=50)
text_output.pack()

word_count_label = tk.Label(root, text="Word Count: ")
word_count_label.pack()

qa_label = tk.Label(root, text="Generated Questions and Answers: ")
qa_label.pack()

qa_output = scrolledtext.ScrolledText(root, height=15, width=70)
qa_output.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

upload_button = tk.Button(button_frame, text="Upload File", command=convert_speech_and_generate_qa)
upload_button.grid(row=0, column=0, padx=10)

pdf_button = tk.Button(button_frame, text="Create PDF", command=create_pdf)
pdf_button.grid(row=0, column=1, padx=10)

root.mainloop()
