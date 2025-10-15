import tkinter as tk
import threading
import speech_recognition as sr
import win32com.client
import webbrowser
import datetime
import random
import csv
import os

# Voice Engine
speaker = win32com.client.Dispatch("SAPI.SpVoice")

# File for logs
LOG_FILE = "assistant_log.csv"

# Ensure CSV file has headers if new
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Query", "Response"])

def log_query(query, response):
    """Log query, response, and time to CSV file."""
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, query, response])

def show_output_window(message):
    """Popup window for assistant output (black bg, white text)."""
    output_win = tk.Toplevel(app)
    output_win.title("Assistant Output")
    output_win.configure(bg="black")
    output_win.geometry("400x180")

    output_label = tk.Label(output_win, text=message, font=("Arial", 14),
                            bg="black", fg="white", wraplength=380, justify="left")
    output_label.pack(expand=True, padx=20, pady=30)

    ok_btn = tk.Button(output_win, text="OK", command=output_win.destroy,
                       bg="#1100FF", fg="#2962FF", font=("Arial", 11, "bold"), width=10)
    ok_btn.pack(pady=8)
    output_win.transient(app)
    output_win.grab_set()
    output_win.focus_force()

def listen_and_respond(status_label):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            status_label.config(text="Adjusting for noise...", fg="#2962FF")
            app.update()
            recognizer.adjust_for_ambient_noise(source)
            status_label.config(text="Listening...", fg="#4000FF")
            app.update()
            audio_data = recognizer.listen(source, timeout=6)
            status_label.config(text="Recognizing...", fg="#2962FF")
            app.update()
            text = recognizer.recognize_google(audio_data)
            output_msg = f"You said: {text}\n\n"
            print(f"You said: {text}")

            response = ""

            # Command logic and spoken responses
            if "greet" in text.lower():
                hour = int(datetime.datetime.now().hour)
                if hour >= 0 and hour < 12:
                    response = "Good morning!"
                elif hour >= 12 and hour < 16:
                    response = "Good afternoon!"
                else:
                    response = "Good evening!"
                speaker.Speak(response)
                status_label.config(text="Greeted!", fg="#2962FF")
                output_msg += response

            elif "intro" in text.lower():
                response = "Hi, I'm jeks the A.I bot. Speed 1 terahertz, memory 1 zigabyte."
                speaker.Speak(response)
                output_msg += response
                status_label.config(text="Introduced myself", fg="#2962FF")

            elif "close it" in text.lower():
                response = "Closing the program."
                speaker.Speak(response)
                status_label.config(text="Closing...", fg="#2962FF")
                output_msg += "Assistant is closing."
                log_query(text, response)
                show_output_window(output_msg)
                app.after(600, app.destroy)
                return

            elif "search google for" in text.lower():
                query = text.lower().replace("search google for", "")
                search_url = f"https://www.google.com/search?q={query}"
                webbrowser.open(search_url)
                response = f"Searching for {query} on Google."
                speaker.Speak(response)
                output_msg += response
                status_label.config(text=response, fg="#2962FF")

            elif "tell me time" in text.lower():
                now = datetime.datetime.now()
                hour, minute, second = now.strftime("%I"), now.strftime("%M"), now.strftime("%S")
                response = f"Time is {hour}:{minute}:{second}"
                speaker.Speak(hour)
                speaker.Speak(minute)
                speaker.Speak(second)
                output_msg += response
                status_label.config(text="Told you the time.", fg="#2962FF")

            elif "pick a number" in text.lower():
                rn = random.randint(-1111111111, 1111111111)
                response = f"Random number: {rn}"
                speaker.Speak(rn)
                output_msg += response
                status_label.config(text=f"Number: {rn}", fg="#2962FF")

            else:
                response = text
                speaker.Speak(response)
                output_msg += response
                status_label.config(text=f"You said: {text}", fg="#2962FF")

            # Log every query-response
            log_query(text, response)
            show_output_window(output_msg)

    except sr.UnknownValueError:
        err = "Sorry, I could not understand the audio."
        speaker.Speak(err)
        status_label.config(text=err, fg="red")
        show_output_window(err)
        log_query("Unrecognized Speech", err)

    except sr.RequestError as e:
        err = f"Could not request results; {e}"
        speaker.Speak(err)
        status_label.config(text=err, fg="red")
        show_output_window(err)
        log_query("Request Error", err)

    except Exception as e:
        err = f"An error occurred: {e}"
        speaker.Speak("An error occurred.")
        status_label.config(text=err, fg="red")
        show_output_window(err)
        log_query("Exception", err)

def start_listening():
    threading.Thread(target=listen_and_respond, args=(status_label,), daemon=True).start()

#------------------ GUI DESIGN --------------------#
app = tk.Tk()
app.title("JEKS - Virtual Assistant")
app.geometry("420x360")
app.configure(bg="#2962FF")

title_label = tk.Label(app, text="JEKS - Virtual Assistant", bg="#2962FF", fg="#FF0015", font=("Arial", 22, "bold"))
title_label.pack(pady=18)

status_label = tk.Label(app, text="Press START to listen...", bg="#2962FF", fg="white", font=("Arial", 14))
status_label.pack(pady=14)

button_frame = tk.Frame(app, bg="#2962FF")
button_frame.pack(pady=30)

start_button = tk.Button(button_frame, text="START", bg="#00FF9D", fg="#2962FF",
                         font=("Arial", 16, "bold"), width=12, height=2, command=start_listening)
start_button.grid(row=0, column=0, padx=12)

close_button = tk.Button(button_frame, text="CLOSE", bg="#00FF22", fg="#2962FF",
                         font=("Arial", 16, "bold"), width=12, height=2, command=app.destroy)
close_button.grid(row=0, column=1, padx=12)

help_label = tk.Label(app, text="Say: greet | intro | close it | tell me time | pick a number | search google for ...",
                      bg="#2962FF", fg="white", font=("Arial", 9))
help_label.pack(pady=8)

start_button.focus_set()

app.mainloop()
