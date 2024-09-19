import speech_recognition as sr
import win32com.client
import webbrowser

speaker = win32com.client.Dispatch("SAPI.SpVoice")

def main():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use the microphone as the source of audio input
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        print("Listening...")
        while True:
            try:
                # Listen for the first phrase and extract it into audio data
                audio_data = recognizer.listen(source)
                print("Recognizing...")

                # Recognize speech using Google Web Speech API
                text = recognizer.recognize_google(audio_data)

                # Check for Google search command
                if "search google" in text.lower():
                    query = text.lower().replace("search google", "")
                    search_url = f"https://www.google.com/search?q={query}"
                    webbrowser.open(search_url)
                    speaker.Speak(f"Searching for {query} on Google.")
                else:
                    speaker.Speak(text)
                    print(f"You said: {text}")

            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    main()