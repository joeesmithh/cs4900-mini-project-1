import pyttsx3
import speech_recognition as sr


class SpeechIO:
    def __init__(self,
                 rate: int = 150,
                 volume: float = 1.0,
                 mic_index: int | None = None) -> "SpeechIO":
        # Initialize TTS engine
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", rate)
        self._engine.setProperty("volume", volume)
        self._engine.startLoop(False)  # Start engine loop in non-blocking mode

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

    def listen(self,
               timeout: int | None = None,
               phrase_limit: int | None = None) -> str | None:
        print("Listening...")
        with self._mic as source:
            try:
                audio = self._recognizer.listen(source=source,
                                                timeout=timeout,
                                                phrase_time_limit=phrase_limit)
                result = self._recognizer.recognize_google(audio).lower()
                print(f"Heard: {result}")
                return result
            except sr.RequestError as e:
                print(f"[STT] Google Speech API error: {e}")
                return None
            except Exception:
                print("Nothing recognized...")
                return None

    def make_choice(self,
                    choices: list[str],
                    invalid_response: str,
                    timeout: int | None = None,
                    phrase_limit: int | None = None) -> str:
        """Listen while spoken phrase invalid or any word in spoken phrase is
        not in list of choices. Return the first occurring phrase in spoken
        phrase present in list of phrase choices."""
        result = self.listen(timeout, phrase_limit)
        while result is None or not any(item in result for item in choices):
            self.speak(invalid_response)
            result = self.listen(timeout, phrase_limit)
        return next((item for item in choices if item in result), "")
