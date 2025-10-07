import speech_recognition as sr
import pyttsx3
import webbrowser
import time
from flask import Flask, request, jsonify, render_template
from threading import Thread
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Load variables from .env

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

  # Make sure to set this in your environment variables

# Flask App Initialization
app = Flask(__name__)
CORS(app)

# Text-to-Speech Initialization
engine = pyttsx3.init()
engine.setProperty("rate", 150)

# ---------------- HELPER FUNCTIONS ----------------

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def ask_chatgpt(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant."},
                {"role": "user", "content": question}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't connect to ChatGPT right now."

def process_command(command):
    command = command.lower()
    response = ""

    if "open google" in command:
        webbrowser.open("https://www.google.com")
        response = "Opening Google..."
    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        response = "Opening YouTube..."
    elif "hello" in command:
        response = "Hello! How can I help you?"
    elif "close all tabs" in command:
        webbrowser.open("http://127.0.0.1:5000")  # Bring back the assistant page
        response = "Closed all tabs and returned to the assistant page."
    elif "exit" in command or "quit" in command:
        response = "Goodbye!"
    else:
        response = ask_chatgpt(command)

    speak(response)
    return response

def get_working_mic():
    mic_list = sr.Microphone.list_microphone_names()
    print("Available Microphones:")
    for i, name in enumerate(mic_list):
        print(f"{i}: {name}")
    for index in range(len(mic_list)):
        try:
            with sr.Microphone(device_index=index) as source:
                return index
        except Exception:
            continue
    return None

def listen_loop():
    mic_index = get_working_mic()
    if mic_index is None:
        speak("No working microphone found.")
        return

    recognizer = sr.Recognizer()
    speak("Hello! I am your voice assistant. You can say a command now.")

    while True:
        try:
            with sr.Microphone(device_index=mic_index) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🎤 Listening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
                command = recognizer.recognize_google(audio)
                print("You said:", command)

                response = process_command(command)

                if "exit" in command or "quit" in command:
                    print("🛑 Exiting assistant.")
                    break

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError:
            print("Network error.")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(1.5)

# ---------------- FLASK ROUTES ----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get('command', '')
    print("Received command:", command)
    response = process_command(command)
    return jsonify({"reply": response})

# ---------------- MAIN RUN ----------------

def run_flask():
    webbrowser.open("http://127.0.0.1:5000")
    app.run(port=5000)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    listen_loop()
