import pyttsx3
import speech_recognition as sr


class SpeechIO:
    def __init__(self, rate: int = 200, volume: float = 1.0, mic_index: int | None = None):
        # Initialize TTS engine
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", rate)
        self._engine.setProperty("volume", volume)
        self._engine.startLoop(False) # Start engine loop in non-blocking mode

        # Initialize STT engine
        self._recognizer = sr.Recognizer()
        self._mic = sr.Microphone(device_index=mic_index)
        print("Calibrating for ambient noise...")
        with self._mic as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready.")
    
    def __del__(self):
        """End TTS loop on object deletion."""
        self._engine.endLoop()

    def speak(self, text: str) -> None:
        """Queue speech; iterate event loop until speech finishes."""
        self._engine.say(text)
        while self._engine.isBusy():
            self._engine.iterate()
        print(f"[TTS] {text}")

    def listen(self, timeout: int | None = None, phrase_limit: int = 8) -> str | None:
        with self._mic as source:
            try:
                audio = self._recognizer.listen(source=source,
                                                timeout=timeout,
                                                phrase_time_limit=phrase_limit)
                return self._recognizer.recognize_google(audio).lower()
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                print(f"[STT] Google Speech API error: {e}")
                return None
