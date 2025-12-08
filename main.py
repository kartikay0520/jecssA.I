import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import speech_recognition as sr
import win32com.client
import webbrowser
import datetime
import random
import requests
import json
import os
import subprocess
import platform

#  GROQ API CONFIGURATION 
GROQ_API_KEY = "My_API_Key"  # Get from https://console.groq.com
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

# Voice Engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

# Settings
VOICE_SPEED = 1  # -10 to 10 (0 is default)
VOICE_VOLUME = 100  # 0 to 100
speaker.Rate = VOICE_SPEED
speaker.Volume = VOICE_VOLUME

# Conversation history
conversation_history = []
notes_list = []

#  AI INTEGRATION 
def get_ai_response(user_message):
    """Get response from GROQ AI"""
    try:
        conversation_history.append({"role": "user", "content": user_message})
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL,
            "messages": conversation_history,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        
        result = response.json()
        ai_message = result["choices"][0]["message"]["content"]
        
        conversation_history.append({"role": "assistant", "content": ai_message})
        
        # Keep last 10 messages
        if len(conversation_history) > 10:
            conversation_history[:] = conversation_history[-10:]
        
        return {"success": True, "response": ai_message}
        
    except Exception as e:
        return {"success": False, "response": f"AI Error: {str(e)}"}

#  FEATURE FUNCTIONS 

def get_weather(city="Delhi"):
    """Get weather information (OpenWeatherMap API - free)"""
    try:
        # Using free weather API (no key needed for basic)
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        return "Weather service unavailable"
    except:
        return "Could not fetch weather"


def run_file():
    file_path = "C:/Users/lenovo/OneDrive/Desktop/pdf_merger/main.py"  # your file path

    subprocess.run(["python", file_path])

def search_wikipedia(query):
    """Search Wikipedia"""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('extract', 'No information found')[:300] + "..."
        return "Wikipedia search failed"
    except:
        return "Wikipedia unavailable"

def calculate(expression):
    """Safe calculator"""
    try:
        # Remove dangerous functions
        expression = expression.replace("^", "**")
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Invalid expression"
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except:
        return "Calculation error"

def open_application(app_name):
    """Open common applications"""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "explorer": "explorer.exe",
        "word": "winword.exe",
        "excel": "excel.exe"
    }
    
    try:
        app_name = app_name.lower()
        for key, exe in apps.items():
            if key in app_name:
                subprocess.Popen(exe)
                return f"Opening {key.title()}"
        return f"Application '{app_name}' not found"
    except:
        return f"Could not open {app_name}"

def add_note(note_text):
    """Add a note"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    notes_list.append(f"[{timestamp}] {note_text}")
    return f"Note added: {note_text}"

def get_notes():
    """Get all notes"""
    if not notes_list:
        return "No notes saved"
    return "\n".join(notes_list)

def get_system_info():
    """Get system information"""
    try:
        info = f"OS: {platform.system()} {platform.release()}\n"
        info += f"Machine: {platform.machine()}\n"
        info += f"Processor: {platform.processor()}"
        return info
    except:
        return "Could not get system info"

def tell_joke():
    """Random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why don't eggs tell jokes? They'd crack up!",
        "What's a computer's favorite snack? Microchips!"
    ]
    return random.choice(jokes)

def set_reminder(message, seconds=60):
    """Set a simple reminder"""
    def remind():
        import time
        time.sleep(seconds)
        speaker.Speak(f"Reminder: {message}")
        show_output_window(f"⏰ Reminder:\n{message}")
    
    threading.Thread(target=remind, daemon=True).start()
    return f"Reminder set for {seconds} seconds"

# ============= GUI FUNCTIONS =============

def show_output_window(message):
    """Enhanced popup window"""
    output_win = tk.Toplevel(app)
    output_win.title("JEKS Output")
    output_win.configure(bg="#1a1a1a")
    output_win.geometry("500x300")

    # Scrolled text for long content
    text_area = scrolledtext.ScrolledText(
        output_win,
        wrap=tk.WORD,
        font=("Consolas", 11),
        bg="#2d2d2d",
        fg="white",
        padx=15,
        pady=15
    )
    text_area.pack(expand=True, fill="both", padx=10, pady=10)
    text_area.insert(tk.END, message)
    text_area.config(state=tk.DISABLED)

    ok_btn = tk.Button(
        output_win,
        text="OK",
        command=output_win.destroy,
        bg="#2962FF",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15
    )
    ok_btn.pack(pady=10)
    
    output_win.transient(app)
    output_win.grab_set()
    output_win.focus_force()

def show_chat_window(user_input, ai_response):
    """Show AI conversation"""
    chat_win = tk.Toplevel(app)
    chat_win.title("AI Conversation")
    chat_win.configure(bg="#1a1a1a")
    chat_win.geometry("650x450")

    chat_display = scrolledtext.ScrolledText(
        chat_win,
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg="#2d2d2d",
        fg="white",
        padx=15,
        pady=15
    )
    chat_display.pack(expand=True, fill="both", padx=10, pady=10)
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    chat_display.insert(tk.END, f"[{timestamp}] ", "time")
    chat_display.insert(tk.END, "You:\n", "user")
    chat_display.insert(tk.END, f"{user_input}\n\n", "user_text")
    
    chat_display.insert(tk.END, f"[{timestamp}] ", "time")
    chat_display.insert(tk.END, "JEKS AI:\n", "ai")
    chat_display.insert(tk.END, ai_response, "ai_text")
    
    chat_display.tag_config("time", foreground="#888888", font=("Consolas", 8))
    chat_display.tag_config("user", foreground="#00FF9D", font=("Consolas", 10, "bold"))
    chat_display.tag_config("user_text", foreground="#E0E0E0")
    chat_display.tag_config("ai", foreground="#2962FF", font=("Consolas", 10, "bold"))
    chat_display.tag_config("ai_text", foreground="#FFFFFF")
    
    chat_display.config(state=tk.DISABLED)
    
    tk.Button(
        chat_win,
        text="Close",
        command=chat_win.destroy,
        bg="#2962FF",
        fg="white",
        font=("Arial", 10, "bold"),
        width=15
    ).pack(pady=10)
    
    chat_win.transient(app)
    chat_win.grab_set()

#  MAIN COMMAND PROCESSOR 

def listen_and_respond(status_label):
    """Process voice commands"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            status_label.config(text="🎧 Adjusting for noise...", fg="#FFD700")
            app.update()
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            status_label.config(text="🎤 Listening...", fg="#00FF9D")
            app.update()
            
            audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=20)
            
            status_label.config(text="🔄 Recognizing...", fg="#2962FF")
            app.update()
            
            text = recognizer.recognize_google(audio_data)
            output_msg = f"You said: {text}\n\n"
            print(f"[USER] {text}")
            
            text_lower = text.lower()
            
            # COMMAND PROCESSING 
            
            # Greeting
            if any(word in text_lower for word in ["greet", "hello", "hi", "hey"]):
                hour = int(datetime.datetime.now().hour)
                if hour < 12:
                    out = "Good morning!"
                elif hour < 16:
                    out = "Good afternoon!"
                else:
                    out = "Good evening!"
                speaker.Speak(out)
                output_msg += out
                status_label.config(text="✅ Greeted!", fg="#00FF9D")
            
            # Introduction
            elif "intro" in text_lower or "introduce yourself" in text_lower:
                out = "Hi, I'm JEKS, your AI-powered virtual assistant. I can help you with tasks, answer questions, and much more!"
                speaker.Speak(out)
                output_msg += out
                status_label.config(text="✅ Introduced", fg="#00FF9D")
            
            # Exit
            elif any(phrase in text_lower for phrase in ["close it", "exit", "goodbye", "bye"]):
                out = "Goodbye! Have a great day!"
                speaker.Speak(out)
                status_label.config(text="👋 Closing...", fg="#FF6B6B")
                output_msg += out
                show_output_window(output_msg)
                app.after(800, app.destroy)
                return
            
            # Time
            elif "time" in text_lower:
                now = datetime.datetime.now()
                time_str = now.strftime("%I:%M %p")
                out = f"Current time is {time_str}"
                speaker.Speak(out)
                output_msg += out
                status_label.config(text="🕐 Time told", fg="#00FF9D")
            
            # Date
            elif "date" in text_lower or "today" in text_lower:
                now = datetime.datetime.now()
                date_str = now.strftime("%B %d, %Y")
                out = f"Today is {date_str}"
                speaker.Speak(out)
                output_msg += out
                status_label.config(text="📅 Date told", fg="#00FF9D")
            
            # Weather
            elif "weather" in text_lower:
                city = "Delhi"  # Default city
                if "in" in text_lower:
                    words = text_lower.split("in")
                    if len(words) > 1:
                        city = words[1].strip()
                weather_info = get_weather(city)
                out = f"Weather in {city}: {weather_info}"
                speaker.Speak(out)
                output_msg += out
                status_label.config(text="🌤️ Weather fetched", fg="#00FF9D")
            
            # Wikipedia
            elif "wikipedia" in text_lower or "wiki" in text_lower:
                query = text_lower.replace("wikipedia", "").replace("wiki", "").replace("search", "").strip()
                if query:
                    status_label.config(text="📚 Searching Wikipedia...", fg="#FFD700")
                    app.update()
                    wiki_info = search_wikipedia(query)
                    speaker.Speak("Here's what I found on Wikipedia")
                    output_msg += f"Wikipedia: {query}\n\n{wiki_info}"
                    status_label.config(text="✅ Wikipedia search done", fg="#00FF9D")
                else:
                    out = "Please specify what to search on Wikipedia"
                    speaker.Speak(out)
                    output_msg += out
            
            # Calculator
            elif "calculate" in text_lower or "compute" in text_lower:
                expression = text_lower.replace("calculate", "").replace("compute", "").replace("what is", "").strip()
                if expression:
                    result = calculate(expression)
                    out = f"Result: {result}"
                    speaker.Speak(out)
                    output_msg += out
                    status_label.config(text="🔢 Calculated", fg="#00FF9D")
                else:
                    out = "Please provide an expression to calculate"
                    speaker.Speak(out)
                    output_msg += out
            
            # Google Search
            elif "search google" in text_lower or "google search" in text_lower:
                query = text_lower.replace("search google for", "").replace("google search", "").strip()
                if query:
                    search_url = f"https://www.google.com/search?q={query}"
                    webbrowser.open(search_url)
                    out = f"Searching Google for {query}"
                    speaker.Speak(out)
                    output_msg += out
                    status_label.config(text="🔍 Google opened", fg="#00FF9D")
                else:
                    out = "What should I search for?"
                    speaker.Speak(out)
                    output_msg += out
            
            # PDF Merger
            elif "merge pdf" in text_lower or "merge files" in text_lower:
                out = "Opening PDF Merger application"
                speaker.Speak(out)
                output_msg += out
                status_label.config(text="📂 Opening PDF Merger", fg="#00FF9D")
                run_file()
            
            # YouTube
            elif "youtube" in text_lower or "play video" in text_lower:
                query = text_lower.replace("youtube", "").replace("play video", "").replace("search", "").strip()
                if query:
                    yt_url = f"https://www.youtube.com/results?search_query={query}"
                    webbrowser.open(yt_url)
                    out = f"Searching YouTube for {query}"
                    speaker.Speak(out)
                    output_msg += out
                    status_label.config(text="📺 YouTube opened", fg="#00FF9D")
                else:
                    webbrowser.open("https://www.youtube.com")
                    out = "Opening YouTube"
                    speaker.Speak(out)
                    output_msg += out
            
            # Open Application
            elif "open" in text_lower and any(app in text_lower for app in ["notepad", "calculator", "paint", "chrome", "edge", "explorer", "word", "excel"]):
                app_name = text_lower.replace("open", "").strip()
                result = open_application(app_name)
                speaker.Speak(result)
                output_msg += result
                status_label.config(text="📱 App opened", fg="#00FF9D")
            
            # Take Note
            elif "note" in text_lower or "remember" in text_lower:
                note_text = text_lower.replace("take note", "").replace("remember", "").replace("note that", "").strip()
                if note_text:
                    result = add_note(note_text)
                    speaker.Speak("Note saved")
                    output_msg += result
                    status_label.config(text="📝 Note saved", fg="#00FF9D")
                else:
                    out = "What should I note?"
                    speaker.Speak(out)
                    output_msg += out
            
            # Show Notes
            elif "show notes" in text_lower or "my notes" in text_lower:
                notes = get_notes()
                speaker.Speak("Here are your notes")
                output_msg += f"Your Notes:\n\n{notes}"
                status_label.config(text="📋 Notes displayed", fg="#00FF9D")
            
            # Random Number
            elif "pick a number" in text_lower or "random number" in text_lower:
                rn = random.randint(1, 100)
                out = f"Random number: {rn}"
                speaker.Speak(str(rn))
                output_msg += out
                status_label.config(text=f"🎲 Number: {rn}", fg="#00FF9D")
            
            # Joke
            elif "joke" in text_lower or "make me laugh" in text_lower:
                joke = tell_joke()
                speaker.Speak(joke)
                output_msg += joke
                status_label.config(text="😄 Joke told", fg="#00FF9D")
            
            # System Info
            elif "system info" in text_lower or "computer info" in text_lower:
                info = get_system_info()
                speaker.Speak("Here is your system information")
                output_msg += info
                status_label.config(text="💻 System info", fg="#00FF9D")
            
            # Clear History
            elif "clear history" in text_lower:
                conversation_history.clear()
                speaker.Speak("Conversation history cleared")
                output_msg += "History cleared!"
                status_label.config(text="🗑️ History cleared", fg="#00FF9D")
            
            # AI Chat (if GROQ API key is set)
            elif GROQ_API_KEY != "YOUR_GROQ_API_KEY_HERE":
                status_label.config(text="🤖 AI thinking...", fg="#2962FF")
                app.update()
                
                result = get_ai_response(text)
                
                if result["success"]:
                    speech_text = result["response"][:250]
                    speaker.Speak(speech_text)
                    status_label.config(text="✅ AI responded", fg="#00FF9D")
                    show_chat_window(text, result["response"])
                    return  # Exit early to show chat window
                else:
                    speaker.Speak("AI service unavailable")
                    output_msg += result["response"]
            
            # Default: Repeat
            else:
                speaker.Speak(text)
                output_msg += f"I heard: {text}"
                status_label.config(text="🔊 Repeated", fg="#00FF9D")
            
            show_output_window(output_msg)
            
    except sr.WaitTimeoutError:
        err = "⏱️ No speech detected"
        status_label.config(text=err, fg="#FF6B6B")
        speaker.Speak("I didn't hear anything")
        
    except sr.UnknownValueError:
        err = "❓ Could not understand"
        status_label.config(text=err, fg="#FF6B6B")
        speaker.Speak("Sorry, I couldn't understand that")
        
    except sr.RequestError as e:
        err = "🔴 Speech service error"
        status_label.config(text=err, fg="#FF6B6B")
        speaker.Speak("Speech recognition error")
        print(f"Error: {e}")
        
    except Exception as e:
        status_label.config(text="❌ Error occurred", fg="#FF6B6B")
        speaker.Speak("An error occurred")
        print(f"Error: {e}")

def start_listening():
    """Start listening in separate thread"""
    threading.Thread(target=listen_and_respond, args=(status_label,), daemon=True).start()

def show_commands():
    """Show all available commands"""
    commands = """
🎤 AVAILABLE VOICE COMMANDS

━━━━━ BASIC ━━━━━
• greet / hello / hi
• introduce yourself
• time
• date / today
• goodbye / exit

━━━━━ SEARCH & INFO ━━━━━
• search google for [query]
• youtube [query]
• wikipedia [topic]
• weather in [city]

━━━━━ CALCULATOR ━━━━━
• calculate [expression]
• compute [expression]

━━━━━ APPLICATIONS ━━━━━
• open notepad
• open calculator
• open paint
• open chrome

━━━━━ NOTES & MEMORY ━━━━━
• take note [text]
• show notes / my notes
• clear history

━━━━━ FUN ━━━━━
• tell me a joke
• pick a number
• random number

━━━━━ SYSTEM ━━━━━
• system info
• computer info

━━━━━ AI CHAT ━━━━━
• Ask anything naturally!
• AI will understand context
    """
    
    messagebox.showinfo("Voice Commands", commands)

def show_settings():
    """Show settings window"""
    settings_win = tk.Toplevel(app)
    settings_win.title("Settings")
    settings_win.geometry("400x300")
    settings_win.configure(bg="#1a1a1a")
    
    tk.Label(settings_win, text="⚙️ Settings", bg="#1a1a1a", fg="white", 
             font=("Arial", 16, "bold")).pack(pady=20)
    
    # Voice speed
    tk.Label(settings_win, text="Voice Speed:", bg="#1a1a1a", fg="white",
             font=("Arial", 11)).pack(pady=5)
    
    def update_speed(val):
        global VOICE_SPEED
        VOICE_SPEED = int(float(val))
        speaker.Rate = VOICE_SPEED
    
    speed_scale = tk.Scale(settings_win, from_=-10, to=10, orient=tk.HORIZONTAL,
                          command=update_speed, bg="#2d2d2d", fg="white",
                          highlightthickness=0, length=250)
    speed_scale.set(VOICE_SPEED)
    speed_scale.pack(pady=10)
    
    # Voice volume
    tk.Label(settings_win, text="Voice Volume:", bg="#1a1a1a", fg="white",
             font=("Arial", 11)).pack(pady=5)
    
    def update_volume(val):
        global VOICE_VOLUME
        VOICE_VOLUME = int(float(val))
        speaker.Volume = VOICE_VOLUME
    
    volume_scale = tk.Scale(settings_win, from_=0, to=100, orient=tk.HORIZONTAL,
                           command=update_volume, bg="#2d2d2d", fg="white",
                           highlightthickness=0, length=250)
    volume_scale.set(VOICE_VOLUME)
    volume_scale.pack(pady=10)
    
    tk.Button(settings_win, text="Close", command=settings_win.destroy,
              bg="#2962FF", fg="white", font=("Arial", 10, "bold"),
              width=15).pack(pady=20)

# GUI DESIGN 
app = tk.Tk()
app.title("JEKS - AI Voice Assistant")
app.geometry("600x550")
app.configure(bg="#1a1a1a")

# Header
header_frame = tk.Frame(app, bg="#2962FF", height=100)
header_frame.pack(fill="x")

title_label = tk.Label(header_frame, text="🤖 JEKS", bg="#2962FF", fg="white",
                       font=("Arial", 28, "bold"))
title_label.pack(pady=8)

subtitle_label = tk.Label(header_frame, text="AI-Powered Voice Assistant",
                         bg="#2962FF", fg="#E0E0E0", font=("Arial", 11))
subtitle_label.pack()

# Status
status_label = tk.Label(app, text="Press START to activate voice control...",
                       bg="#1a1a1a", fg="white", font=("Arial", 13),
                       wraplength=550, pady=20)
status_label.pack()

# Main buttons
main_frame = tk.Frame(app, bg="#1a1a1a")
main_frame.pack(pady=25)

start_button = tk.Button(main_frame, text="🎤 START\nLISTENING",
                        bg="#00FF9D", fg="#1a1a1a",
                        font=("Arial", 14, "bold"), width=15, height=3,
                        command=start_listening, cursor="hand2")
start_button.grid(row=0, column=0, padx=10)

commands_button = tk.Button(main_frame, text="📋 COMMANDS\nLIST",
                           bg="#FFD700", fg="#1a1a1a",
                           font=("Arial", 14, "bold"), width=15, height=3,
                           command=show_commands, cursor="hand2")
commands_button.grid(row=0, column=1, padx=10)

# Secondary buttons
sec_frame = tk.Frame(app, bg="#1a1a1a")
sec_frame.pack(pady=15)

settings_btn = tk.Button(sec_frame, text="⚙️ Settings", bg="#2962FF", fg="white",
                        font=("Arial", 10, "bold"), width=12,
                        command=show_settings, cursor="hand2")
settings_btn.grid(row=0, column=0, padx=5)

close_button = tk.Button(sec_frame, text="❌ Close", bg="#FF6B6B", fg="white",
                        font=("Arial", 10, "bold"), width=12,
                        command=app.destroy, cursor="hand2")
close_button.grid(row=0, column=1, padx=5)

# Info panel
info_frame = tk.Frame(app, bg="#2d2d2d", relief=tk.GROOVE, borderwidth=2)
info_frame.pack(pady=20, padx=30, fill="x")

info_label = tk.Label(info_frame,
                     text="💡 Features: Voice Control • AI Chat • Weather • Wikipedia\n"
                          "Calculator • Notes • Apps • Jokes • And More!",
                     bg="#2d2d2d", fg="#E0E0E0", font=("Arial", 9),
                     justify="center", pady=15)
info_label.pack()

# Footer
footer = tk.Label(app, text="🔊 Speak naturally • JEKS understands context",
                 bg="#1a1a1a", fg="#888888", font=("Arial", 9, "italic"))
footer.pack(pady=10)

start_button.focus_set()

app.mainloop()