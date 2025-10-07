import speech_recognition as sr 
import pyttsx3
import webbrowser
import time
from flask import Flask, request, jsonify, render_template
from threading import Thread
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

engine = pyttsx3.init()
engine.setProperty("rate", 150)

recognizer = sr.Recognizer()
mic_index = None
listening = False

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mic-control', methods=['POST'])
def mic_control():
    action = request.json.get('action')
    if action == 'start':
        mic_event.set()
        return jsonify({'status': 'listening started'})
    elif action == 'stop':
        mic_event.clear()
        return jsonify({'status': 'listening stopped'})
    return jsonify({'error': 'invalid action'}), 400


@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get('command', '').lower()
    print("Received command from frontend:", command)
    response = process_command(command)
    return jsonify({"reply": response})

def process_command(command):
    command = command.lower()
    response = ""

    if "open google" in command:
        webbrowser.open_new_tab("https://www.google.com")
        response = "Opening Google."
    elif "open youtube" in command:
        webbrowser.open_new_tab("https://www.youtube.com")
        response = "Opening YouTube."
    elif "close all tabs" in command:
        webbrowser.open_new_tab("http://127.0.0.1:5000")
        response = "Redirecting to assistant page."
    elif "hello" in command:
        response = "Hello! How can I help you?"
    elif "exit" in command or "quit" in command:
        global listening
        listening = False
        response = "Goodbye! Voice assistant is shutting down."
    else:
        response = f"You said: {command}"

    speak(response)
    return response

def get_working_mic():
    mic_list = sr.Microphone.list_microphone_names()
    for index in range(len(mic_list)):
        try:
            with sr.Microphone(device_index=index) as source:
                return index
        except:
            continue
    return None

def listen_loop():
    global mic_index, listening
    if mic_index is None:
        mic_index = get_working_mic()
        if mic_index is None:
            speak("No working microphone found.")
            return

    speak("Hello! I am your voice assistant. You can say a command now.")
    while listening:
        try:
            with sr.Microphone(device_index=mic_index) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("🎤 Listening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
                command = recognizer.recognize_google(audio)
                print("You said:", command)
                process_command(command)

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError:
            print("Network error.")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

def run_flask():
    webbrowser.open("http://127.0.0.1:5000")
    app.run(port=5000)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    # DO NOT start listen_loop() here — it will auto-start only from frontend request
    while True:
        time.sleep(1)
