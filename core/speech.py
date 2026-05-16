import asyncio
import edge_tts
import pygame
import os
import tempfile

class JARVISSpeech:
    def __init__(self):
        # en-GB-RyanNeural is a very good British male voice for JARVIS
        self.voice = "en-GB-RyanNeural"
        pygame.mixer.init()

    def stop(self):
        """Stops the current playback."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            return True
        return False

    async def speak(self, text: str):
        """Generates speech and plays it."""
        # Remove TOOL_CALL lines from speech
        clean_text = "\n".join([line for line in text.split("\n") if not line.startswith("TOOL_CALL:")])
        if not clean_text.strip():
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_path = tmp_file.name

        try:
            communicate = edge_tts.Communicate(clean_text, self.voice)
            await communicate.save(tmp_path)

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
            pygame.mixer.music.unload()
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

def speak_sync(text: str):
    """Wrapper to run async speak in a synchronous way if needed."""
    speech = JARVISSpeech()
    asyncio.run(speech.speak(text))

if __name__ == "__main__":
    # Test
    # asyncio.run(JARVISSpeech().speak("Hello sir, I am JARVIS. How can I help you today?"))
    pass
