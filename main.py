import tkinter as tk
from tkinter import scrolledtext, messagebox, font as tkfont
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
import math
import time

# ─── GROQ API CONFIGURATION ───────────────────────────────────────────────────
# Get your API key at: https://console.groq.com/keys
GROQ_API_KEY = "My_API_Key"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Latest model (Llama 4 Maverick) — 128K context, MoE architecture, best quality
MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"
# Fallback: "llama-3.3-70b-versatile"  ← production-stable, slightly faster

# ─── VOICE ENGINE ─────────────────────────────────────────────────────────────
speaker = win32com.client.Dispatch("SAPI.SpVoice")
VOICE_SPEED  = 1
VOICE_VOLUME = 100
speaker.Rate   = VOICE_SPEED
speaker.Volume = VOICE_VOLUME

# ─── STATE ────────────────────────────────────────────────────────────────────
conversation_history = []
notes_list           = []
chat_history_log     = []   # list of (role, text) for in-app chat log


# ══════════════════════════════════════════════════════════════════════════════
#  DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════════════════
BG_DEEP    = "#0D0F14"
BG_PANEL   = "#13161E"
BG_CARD    = "#1A1E2A"
BG_HOVER   = "#1F2535"

ACCENT_A   = "#00C8FF"   # cyan  – primary
ACCENT_B   = "#7B61FF"   # violet
ACCENT_C   = "#00FF8C"   # mint green (success / active)
ACCENT_RED = "#FF4D6A"   # danger

TEXT_HI    = "#E8EAF0"
TEXT_MID   = "#8A90A2"
TEXT_DIM   = "#4A5066"

BORDER     = "#252B3D"
BORDER_ACT = "#2E3550"

FONT_HEAD  = ("Segoe UI", 9, "bold")
FONT_BODY  = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 9)
FONT_BIG   = ("Segoe UI", 22, "bold")
FONT_LABEL = ("Segoe UI", 8)


# ══════════════════════════════════════════════════════════════════════════════
#  AI & FEATURE FUNCTIONS  (unchanged logic, same as original)
# ══════════════════════════════════════════════════════════════════════════════

def get_ai_response(user_message):
    try:
        conversation_history.append({"role": "user", "content": user_message})
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": MODEL, "messages": conversation_history,
                   "temperature": 0.7, "max_tokens": 500}
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=25)
        resp.raise_for_status()
        msg = resp.json()["choices"][0]["message"]["content"]
        conversation_history.append({"role": "assistant", "content": msg})
        if len(conversation_history) > 10:
            conversation_history[:] = conversation_history[-10:]
        return {"success": True, "response": msg}
    except Exception as e:
        return {"success": False, "response": f"AI Error: {str(e)}"}

def get_weather(city="Delhi"):
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        r = requests.get(url, timeout=5)
        return r.text.strip() if r.status_code == 200 else "Weather unavailable"
    except:
        return "Could not fetch weather"

def run_file():
    subprocess.run(["python", "C:/Users/lenovo/OneDrive/Desktop/pdf_merger/main.py"])

def search_wikipedia(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get("extract", "No information found")[:300] + "..."
        return "Wikipedia search failed"
    except:
        return "Wikipedia unavailable"

def calculate(expression):
    try:
        expression = expression.replace("^", "**")
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Invalid expression"
        return str(eval(expression, {"__builtins__": {}}, {}))
    except:
        return "Calculation error"

def open_application(app_name):
    apps = {"notepad": "notepad.exe", "calculator": "calc.exe",
            "paint": "mspaint.exe", "chrome": "chrome.exe",
            "edge": "msedge.exe", "explorer": "explorer.exe",
            "word": "winword.exe", "excel": "excel.exe"}
    try:
        name = app_name.lower()
        for key, exe in apps.items():
            if key in name:
                subprocess.Popen(exe)
                return f"Opening {key.title()}"
        return f"App '{app_name}' not found"
    except:
        return f"Could not open {app_name}"

def add_note(note_text):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    notes_list.append(f"[{ts}] {note_text}")
    return f"Note saved: {note_text}"

def get_notes():
    return "\n".join(notes_list) if notes_list else "No notes yet"

def get_system_info():
    try:
        return (f"OS: {platform.system()} {platform.release()}\n"
                f"Machine: {platform.machine()}\n"
                f"Processor: {platform.processor()}")
    except:
        return "Could not get system info"

def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why don't eggs tell jokes? They'd crack up!",
        "What's a computer's favorite snack? Microchips!"
    ]
    return random.choice(jokes)

def set_reminder(message, seconds=60):
    def remind():
        time.sleep(seconds)
        speaker.Speak(f"Reminder: {message}")
        append_chat("JEKS", f"⏰ Reminder: {message}", tag="ai")
    threading.Thread(target=remind, daemon=True).start()
    return f"Reminder set for {seconds} seconds"


# ══════════════════════════════════════════════════════════════════════════════
#  GUI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def append_chat(role, text, tag="user"):
    """Append a message to the chat log widget."""
    ts = datetime.datetime.now().strftime("%H:%M")
    chat_log.config(state=tk.NORMAL)
    if tag == "user":
        chat_log.insert(tk.END, f"\n  You  {ts}\n", "usr_name")
        chat_log.insert(tk.END, f"  {text}\n", "usr_msg")
    else:
        chat_log.insert(tk.END, f"\n  JEKS  {ts}\n", "bot_name")
        chat_log.insert(tk.END, f"  {text}\n", "bot_msg")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)


def set_status(text, color=TEXT_MID):
    status_var.set(text)
    status_label.config(fg=color)
    root.update_idletasks()


def set_indicator(state):
    """state: 'idle' | 'listen' | 'think' | 'speak' | 'error'"""
    colors = {
        "idle":   (TEXT_DIM, "—"),
        "listen": (ACCENT_C, "●  Listening"),
        "think":  (ACCENT_A, "◎  Processing"),
        "speak":  (ACCENT_B, "▶  Speaking"),
        "error":  (ACCENT_RED, "✕  Error"),
    }
    c, lbl = colors.get(state, colors["idle"])
    indicator_dot.config(bg=c)
    indicator_label.config(text=lbl, fg=c)
    root.update_idletasks()


# ══════════════════════════════════════════════════════════════════════════════
#  ANIMATED WAVEFORM CANVAS
# ══════════════════════════════════════════════════════════════════════════════

wave_active   = False
wave_frame_id = None

def _draw_wave(canvas, w, h, tick, amplitudes):
    canvas.delete("wave")
    bars   = 28
    gap    = 3
    bar_w  = (w - gap * (bars + 1)) / bars
    cx     = w / 2
    for i in range(bars):
        phase   = tick * 0.18 + i * 0.45
        amp     = amplitudes[i % len(amplitudes)]
        height  = amp * abs(math.sin(phase)) * (h * 0.55) + 4
        x1 = gap + i * (bar_w + gap)
        x2 = x1 + bar_w
        cy = h / 2
        # gradient-ish: centre bars brighter
        dist = abs(i - bars / 2) / (bars / 2)
        alpha_factor = 1 - dist * 0.5
        color = ACCENT_C if wave_active else TEXT_DIM
        canvas.create_rectangle(
            x1, cy - height / 2, x2, cy + height / 2,
            fill=color, outline="", tags="wave"
        )

def start_wave_anim(canvas, w, h):
    global wave_active, wave_frame_id
    wave_active = True
    amps = [random.uniform(0.3, 1.0) for _ in range(14)]
    tick = [0]

    def step():
        if not wave_active:
            canvas.delete("wave")
            _draw_wave(canvas, w, h, 0, [0.05] * 14)
            return
        tick[0] += 1
        _draw_wave(canvas, w, h, tick[0], amps)
        canvas.after(55, step)

    step()

def stop_wave_anim(canvas, w, h):
    global wave_active
    wave_active = False


# ══════════════════════════════════════════════════════════════════════════════
#  COMMAND PROCESSOR
# ══════════════════════════════════════════════════════════════════════════════

def listen_and_respond():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            set_indicator("listen")
            set_status("Adjusting for ambient noise…")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            set_status("Listening — speak now")
            start_wave_anim(wave_canvas, WAVE_W, WAVE_H)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
            stop_wave_anim(wave_canvas, WAVE_W, WAVE_H)

            set_indicator("think")
            set_status("Recognising speech…")
            text = recognizer.recognize_google(audio)

        append_chat("You", text, tag="user")
        text_lower = text.lower()
        out = ""

        # ── Greet
        if any(w in text_lower for w in ["greet", "hello", "hi", "hey"]):
            h = int(datetime.datetime.now().hour)
            out = "Good morning!" if h < 12 else ("Good afternoon!" if h < 16 else "Good evening!")

        # ── Introduce
        elif "intro" in text_lower or "introduce yourself" in text_lower:
            out = "Hi, I'm JEKS — your AI-powered voice assistant. I can answer questions, search the web, manage notes, and much more!"

        # ── Exit
        elif any(p in text_lower for p in ["close it", "exit", "goodbye", "bye"]):
            out = "Goodbye! Have a great day!"
            set_indicator("speak")
            speaker.Speak(out)
            append_chat("JEKS", out, tag="ai")
            set_status("Closing…", ACCENT_RED)
            root.after(900, root.destroy)
            return

        # ── Time
        elif "time" in text_lower:
            out = f"Current time is {datetime.datetime.now().strftime('%I:%M %p')}"

        # ── Date
        elif "date" in text_lower or "today" in text_lower:
            out = f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"

        # ── Weather
        elif "weather" in text_lower:
            city = "Delhi"
            if "in" in text_lower:
                parts = text_lower.split("in")
                if len(parts) > 1:
                    city = parts[1].strip()
            info = get_weather(city)
            out  = f"Weather in {city}: {info}"

        # ── Wikipedia
        elif "wikipedia" in text_lower or "wiki" in text_lower:
            q = text_lower.replace("wikipedia","").replace("wiki","").replace("search","").strip()
            if q:
                set_status("Searching Wikipedia…")
                out = f"Wikipedia › {q}\n\n{search_wikipedia(q)}"
            else:
                out = "Please specify what to search on Wikipedia"

        # ── Calculate
        elif "calculate" in text_lower or "compute" in text_lower:
            expr = text_lower.replace("calculate","").replace("compute","").replace("what is","").strip()
            out  = f"Result: {calculate(expr)}" if expr else "Please provide an expression"

        # ── Google
        elif "search google" in text_lower or "google search" in text_lower:
            q = text_lower.replace("search google for","").replace("google search","").strip()
            if q:
                webbrowser.open(f"https://www.google.com/search?q={q}")
                out = f"Searching Google for {q}"
            else:
                out = "What should I search for?"

        # ── PDF Merger
        elif "merge pdf" in text_lower or "merge files" in text_lower:
            out = "Opening PDF Merger…"
            run_file()

        # ── YouTube
        elif "youtube" in text_lower or "play video" in text_lower:
            q = text_lower.replace("youtube","").replace("play video","").replace("search","").strip()
            if q:
                webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
                out = f"Searching YouTube for {q}"
            else:
                webbrowser.open("https://www.youtube.com")
                out = "Opening YouTube"

        # ── Open App
        elif "open" in text_lower and any(a in text_lower for a in ["notepad","calculator","paint","chrome","edge","explorer","word","excel"]):
            out = open_application(text_lower.replace("open","").strip())

        # ── Take Note
        elif "note" in text_lower or "remember" in text_lower:
            body = text_lower.replace("take note","").replace("remember","").replace("note that","").strip()
            out  = add_note(body) if body else "What should I note?"

        # ── Show Notes
        elif "show notes" in text_lower or "my notes" in text_lower:
            out = f"Your Notes\n\n{get_notes()}"

        # ── Random Number
        elif "pick a number" in text_lower or "random number" in text_lower:
            n   = random.randint(1, 100)
            out = f"Random number: {n}"

        # ── Joke
        elif "joke" in text_lower or "make me laugh" in text_lower:
            out = tell_joke()

        # ── System Info
        elif "system info" in text_lower or "computer info" in text_lower:
            out = get_system_info()

        # ── Clear History
        elif "clear history" in text_lower:
            conversation_history.clear()
            out = "Conversation history cleared."

        # ── AI Chat (GROQ)
        elif GROQ_API_KEY != "YOUR_GROQ_API_KEY_HERE":
            set_status("Thinking…")
            result = get_ai_response(text)
            if result["success"]:
                out = result["response"]
            else:
                out = result["response"]

        # ── Default
        else:
            speaker.Speak(text)
            out = f"I heard: {text}"

        set_indicator("speak")
        speaker.Speak(out[:300])
        append_chat("JEKS", out, tag="ai")
        set_status("Ready", TEXT_MID)
        set_indicator("idle")

    except sr.WaitTimeoutError:
        stop_wave_anim(wave_canvas, WAVE_W, WAVE_H)
        set_indicator("error")
        set_status("No speech detected — try again", ACCENT_RED)
        speaker.Speak("I didn't hear anything")
    except sr.UnknownValueError:
        stop_wave_anim(wave_canvas, WAVE_W, WAVE_H)
        set_indicator("error")
        set_status("Couldn't understand — please repeat", ACCENT_RED)
        speaker.Speak("Sorry, I couldn't understand that")
    except sr.RequestError as e:
        stop_wave_anim(wave_canvas, WAVE_W, WAVE_H)
        set_indicator("error")
        set_status("Speech service error", ACCENT_RED)
        speaker.Speak("Speech recognition error")
    except Exception as e:
        stop_wave_anim(wave_canvas, WAVE_W, WAVE_H)
        set_indicator("error")
        set_status(f"Error: {e}", ACCENT_RED)
        speaker.Speak("An error occurred")
    finally:
        mic_btn.config(state=tk.NORMAL)


def on_listen_click():
    mic_btn.config(state=tk.DISABLED)
    set_indicator("listen")
    threading.Thread(target=listen_and_respond, daemon=True).start()


# ── Text input send ───────────────────────────────────────────────────────────
def on_text_send(event=None):
    text = text_input.get().strip()
    if not text:
        return
    text_input.delete(0, tk.END)
    append_chat("You", text, tag="user")

    def handle():
        set_indicator("think")
        set_status("Thinking…")
        if GROQ_API_KEY != "YOUR_GROQ_API_KEY_HERE":
            result = get_ai_response(text)
            out = result["response"]
        else:
            out = "GROQ API key not configured."
        set_indicator("speak")
        speaker.Speak(out[:300])
        append_chat("JEKS", out, tag="ai")
        set_status("Ready", TEXT_MID)
        set_indicator("idle")

    threading.Thread(target=handle, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  COMMAND PANEL (slide-in frame)
# ══════════════════════════════════════════════════════════════════════════════
cmd_panel_visible = False

COMMANDS = [
    ("Basic",           ["hello / hi", "introduce yourself", "time", "date", "goodbye"]),
    ("Search & Web",    ["search google for …", "youtube …", "wikipedia …", "weather in …"]),
    ("Math",            ["calculate …", "compute …"]),
    ("Apps",            ["open notepad", "open calculator", "open chrome", "open paint"]),
    ("Notes",           ["take note …", "show notes", "clear history"]),
    ("Fun",             ["tell me a joke", "random number"]),
    ("System",          ["system info"]),
    ("AI Chat",         ["ask anything naturally!"]),
]

def toggle_cmd_panel():
    global cmd_panel_visible
    if cmd_panel_visible:
        cmd_panel.place_forget()
        cmd_panel_visible = False
    else:
        cmd_panel.place(x=0, y=0, relwidth=1, relheight=1)
        cmd_panel_visible = True


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS WINDOW
# ══════════════════════════════════════════════════════════════════════════════

def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings")
    win.geometry("380x300")
    win.configure(bg=BG_PANEL)
    win.resizable(False, False)

    def section(parent, title):
        tk.Label(parent, text=title, bg=BG_PANEL, fg=TEXT_MID,
                 font=FONT_LABEL).pack(anchor="w", padx=20, pady=(16, 2))

    def lbl(parent, text, **kw):
        return tk.Label(parent, text=text, bg=BG_PANEL, fg=TEXT_HI,
                        font=FONT_BODY, **kw)

    tk.Label(win, text="Settings", bg=BG_PANEL, fg=TEXT_HI,
             font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20, pady=(20, 4))

    sep(win).pack(fill="x", padx=20, pady=4)

    section(win, "VOICE SPEED")
    speed_var = tk.IntVar(value=VOICE_SPEED)
    spd = tk.Scale(win, from_=-10, to=10, orient=tk.HORIZONTAL, variable=speed_var,
                   bg=BG_PANEL, fg=TEXT_HI, troughcolor=BG_CARD, highlightthickness=0,
                   activebackground=ACCENT_A, length=320,
                   command=lambda v: setattr(speaker, "Rate", int(float(v))))
    spd.pack(padx=20)

    section(win, "VOICE VOLUME")
    vol_var = tk.IntVar(value=VOICE_VOLUME)
    vol = tk.Scale(win, from_=0, to=100, orient=tk.HORIZONTAL, variable=vol_var,
                   bg=BG_PANEL, fg=TEXT_HI, troughcolor=BG_CARD, highlightthickness=0,
                   activebackground=ACCENT_A, length=320,
                   command=lambda v: setattr(speaker, "Volume", int(float(v))))
    vol.pack(padx=20)

    flat_btn(win, "Close", win.destroy, ACCENT_B).pack(pady=16)


# ══════════════════════════════════════════════════════════════════════════════
#  REUSABLE WIDGET FACTORIES
# ══════════════════════════════════════════════════════════════════════════════

def sep(parent):
    return tk.Frame(parent, bg=BORDER, height=1)

def flat_btn(parent, text, cmd, accent=ACCENT_A, w=None):
    kw = {}
    if w:
        kw["width"] = w
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=BG_CARD, fg=accent, activebackground=BG_HOVER,
        activeforeground=accent, relief=tk.FLAT, cursor="hand2",
        font=FONT_HEAD, bd=0, padx=14, pady=7,
        highlightthickness=1, highlightbackground=BORDER,
        **kw
    )
    return b

def icon_btn(parent, text, cmd, accent=ACCENT_A, size=40):
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=BG_CARD, fg=accent, activebackground=BG_HOVER,
        activeforeground=accent, relief=tk.FLAT, cursor="hand2",
        font=("Segoe UI", 11, "bold"), bd=0,
        width=4, height=2,
        highlightthickness=1, highlightbackground=BORDER,
    )
    return b


# ══════════════════════════════════════════════════════════════════════════════
#  BUILD MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
root = tk.Tk()
root.title("JEKS — AI Voice Assistant")
root.geometry("680x760")
root.minsize(580, 680)
root.configure(bg=BG_DEEP)

# ── Title bar ─────────────────────────────────────────────────────────────────
title_bar = tk.Frame(root, bg=BG_PANEL, height=64)
title_bar.pack(fill="x")
title_bar.pack_propagate(False)

tk.Label(title_bar, text="JEKS", bg=BG_PANEL, fg=ACCENT_A,
         font=("Segoe UI", 20, "bold")).place(x=22, y=12)

tk.Label(title_bar, text="AI Voice Assistant", bg=BG_PANEL, fg=TEXT_MID,
         font=FONT_BODY).place(x=22, y=40)

# header right buttons
hdr_right = tk.Frame(title_bar, bg=BG_PANEL)
hdr_right.place(relx=1.0, x=-16, y=12, anchor="ne")

flat_btn(hdr_right, "Commands", toggle_cmd_panel, ACCENT_B).pack(side=tk.LEFT, padx=4)
flat_btn(hdr_right, "Settings", open_settings,   TEXT_MID).pack(side=tk.LEFT, padx=4)
flat_btn(hdr_right, "✕ Quit",   root.destroy,     ACCENT_RED).pack(side=tk.LEFT, padx=(4,0))

sep(root).pack(fill="x")

# ── Indicator row ─────────────────────────────────────────────────────────────
ind_row = tk.Frame(root, bg=BG_DEEP, pady=10)
ind_row.pack(fill="x", padx=22)

indicator_dot = tk.Label(ind_row, text=" ", bg=TEXT_DIM, width=2, relief=tk.FLAT)
indicator_dot.pack(side=tk.LEFT, padx=(0, 8))

indicator_label = tk.Label(ind_row, text="—", bg=BG_DEEP, fg=TEXT_DIM, font=FONT_BODY)
indicator_label.pack(side=tk.LEFT)

# ── Waveform canvas ───────────────────────────────────────────────────────────
WAVE_W, WAVE_H = 636, 70
wave_canvas = tk.Canvas(root, width=WAVE_W, height=WAVE_H,
                         bg=BG_PANEL, highlightthickness=0)
wave_canvas.pack(padx=22, pady=(4, 0))
# draw idle bars
_draw_wave(wave_canvas, WAVE_W, WAVE_H, 0, [0.15] * 14)

# ── MIC button ────────────────────────────────────────────────────────────────
mic_row = tk.Frame(root, bg=BG_DEEP)
mic_row.pack(fill="x", padx=22, pady=10)

mic_btn = tk.Button(
    mic_row, text="⏺  START LISTENING",
    command=on_listen_click,
    bg=ACCENT_C, fg="#0A120E",
    activebackground="#00D97A", activeforeground="#0A120E",
    font=("Segoe UI", 11, "bold"),
    relief=tk.FLAT, cursor="hand2", bd=0,
    padx=20, pady=10,
    highlightthickness=0
)
mic_btn.pack(side=tk.LEFT, fill="x", expand=True)

# ── Status bar ────────────────────────────────────────────────────────────────
status_var   = tk.StringVar(value="Press  START LISTENING  or type below")
status_label = tk.Label(root, textvariable=status_var, bg=BG_DEEP, fg=TEXT_MID,
                        font=FONT_BODY, anchor="w")
status_label.pack(fill="x", padx=24, pady=(0, 8))

sep(root).pack(fill="x", padx=0)

# ── Chat log ──────────────────────────────────────────────────────────────────
chat_frame = tk.Frame(root, bg=BG_DEEP)
chat_frame.pack(fill="both", expand=True, padx=0, pady=0)

chat_log = tk.Text(
    chat_frame,
    bg=BG_DEEP, fg=TEXT_HI,
    font=FONT_MONO,
    relief=tk.FLAT, bd=0,
    padx=20, pady=14,
    wrap=tk.WORD,
    state=tk.DISABLED,
    cursor="arrow",
    insertbackground=ACCENT_A,
    selectbackground=ACCENT_B,
    selectforeground=TEXT_HI,
    spacing3=4,
)
sb = tk.Scrollbar(chat_frame, command=chat_log.yview, bg=BG_PANEL, troughcolor=BG_PANEL,
                  relief=tk.FLAT, bd=0, width=8)
chat_log.configure(yscrollcommand=sb.set)
sb.pack(side=tk.RIGHT, fill="y")
chat_log.pack(side=tk.LEFT, fill="both", expand=True)

chat_log.tag_config("usr_name", foreground=ACCENT_C,  font=("Segoe UI", 8, "bold"))
chat_log.tag_config("usr_msg",  foreground=TEXT_HI,   font=FONT_MONO, lmargin1=12, lmargin2=12)
chat_log.tag_config("bot_name", foreground=ACCENT_A,  font=("Segoe UI", 8, "bold"))
chat_log.tag_config("bot_msg",  foreground="#B0C8E8", font=FONT_MONO, lmargin1=12, lmargin2=12)

# opening message
root.after(300, lambda: append_chat("JEKS",
    "Hello! I'm JEKS. Say a command or type below. Try: 'tell me a joke', 'weather in Mumbai', or just ask me anything.", tag="ai"))

sep(root).pack(fill="x")

# ── Text input row ────────────────────────────────────────────────────────────
inp_row = tk.Frame(root, bg=BG_PANEL, pady=10)
inp_row.pack(fill="x", padx=0)

text_input = tk.Entry(
    inp_row,
    bg=BG_CARD, fg=TEXT_HI,
    insertbackground=ACCENT_A,
    font=FONT_BODY,
    relief=tk.FLAT, bd=0,
    highlightthickness=1, highlightbackground=BORDER,
    highlightcolor=ACCENT_A,
)
text_input.pack(side=tk.LEFT, fill="x", expand=True, padx=(16, 8), ipady=8)
text_input.bind("<Return>", on_text_send)

send_btn = tk.Button(
    inp_row, text="Send ↑",
    command=on_text_send,
    bg=ACCENT_A, fg=BG_DEEP,
    activebackground="#00A8D8", activeforeground=BG_DEEP,
    font=FONT_HEAD, relief=tk.FLAT, cursor="hand2",
    bd=0, padx=14, pady=8, highlightthickness=0
)
send_btn.pack(side=tk.LEFT, padx=(0, 16))


# ══════════════════════════════════════════════════════════════════════════════
#  COMMANDS OVERLAY PANEL
# ══════════════════════════════════════════════════════════════════════════════
cmd_panel = tk.Frame(root, bg=BG_PANEL)

# close button
tk.Button(cmd_panel, text="✕  Close", command=toggle_cmd_panel,
          bg=BG_PANEL, fg=TEXT_MID, activebackground=BG_HOVER,
          activeforeground=ACCENT_RED, relief=tk.FLAT, cursor="hand2",
          font=FONT_HEAD, bd=0, padx=14, pady=8).place(relx=1.0, x=-16, y=12, anchor="ne")

tk.Label(cmd_panel, text="Voice Commands", bg=BG_PANEL, fg=TEXT_HI,
         font=("Segoe UI", 14, "bold")).place(x=22, y=16)

cmd_scroll_frame = tk.Frame(cmd_panel, bg=BG_PANEL)
cmd_scroll_frame.place(x=0, y=54, relwidth=1, rely=0, height=999)  # overflow ok

y_off = 0
for section_title, items in COMMANDS:
    tk.Label(cmd_scroll_frame, text=section_title.upper(), bg=BG_PANEL, fg=ACCENT_A,
             font=("Segoe UI", 8, "bold")).place(x=22, y=y_off + 8)
    y_off += 26
    for item in items:
        tk.Label(cmd_scroll_frame, text=f"  › {item}", bg=BG_PANEL, fg=TEXT_HI,
                 font=FONT_MONO, anchor="w").place(x=22, y=y_off)
        y_off += 22
    tk.Frame(cmd_scroll_frame, bg=BORDER, height=1).place(x=22, y=y_off + 4, relwidth=1, width=-44)
    y_off += 18


# ══════════════════════════════════════════════════════════════════════════════
#  LAUNCH
# ══════════════════════════════════════════════════════════════════════════════
text_input.focus_set()
root.mainloop()
