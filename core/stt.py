import os
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class JARVISSTT:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen_and_transcribe(self):
        """Listens for a command and transcribes it using Groq Whisper."""
        with self.microphone as source:
            print("[*] Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Save audio to a temp file
                with open("temp_audio.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                
                # Transcribe using Groq
                with open("temp_audio.wav", "rb") as file:
                    transcription = self.client.audio.transcriptions.create(
                        file=("temp_audio.wav", file.read()),
                        model="whisper-large-v3",
                        response_format="text",
                        language="en"
                    )
                
                # Cleanup
                if os.path.exists("temp_audio.wav"):
                    os.remove("temp_audio.wav")
                
                return transcription.strip()
            except sr.WaitTimeoutError:
                return ""
            except Exception as e:
                print(f"[*] STT Error: {e}")
                return ""

if __name__ == "__main__":
    stt = JARVISSTT()
    # print(stt.listen_and_transcribe())
