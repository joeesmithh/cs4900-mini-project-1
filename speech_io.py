import string
import numpy as np
import pyttsx3
import speech_recognition as sr
import whisper

# Create translation table mapping "" to "" and completely remove
# punctuation symbols. Needed for stripping Whisper translations
# of punctuation before detecting phrases in the detected line.
_SYMBOLS = str.maketrans("", "", string.punctuation)


def _strip_symbols(text: str) -> str:
    """Strip punctuation symbols from text."""
    return text.translate(_SYMBOLS)


class SpeechIO:
    def __init__(self,
                 rate: int = 150,
                 volume: float = 1.0,
                 voice_index: int = 0,
                 mic_index: int | None = None,
                 model_name: str = "base") -> "SpeechIO":
        """Set up the offline TTS and STT engines.

        voice_index selects a pyttsx3 voice by its position in the system
        voice list (run list_voices() to see the available indices). An
        out-of-range value falls back to the engine's default voice.
        """
        # Initialize TTS engine
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", rate)
        self._engine.setProperty("volume", volume)

        # Select the requested voice; ignore a bad index rather than crash.
        voices = self._engine.getProperty("voices")
        if 0 <= voice_index < len(voices):
            self._engine.setProperty("voice", voices[voice_index].id)
        else:
            print(f"Voice index {voice_index} out of range; using default voice.")

        self._engine.startLoop(False)  # Start engine loop in non-blocking mode

        # Initialize STT: SpeechRecognition handles mic capture + voice-activity
        # detection; Whisper transcribes the captured audio locally.
        self._recognizer = sr.Recognizer()
        self._mic = sr.Microphone(device_index=mic_index)
        print(f"Loading Whisper model ({model_name})...")
        self._model = whisper.load_model(model_name)
        print("Calibrating for ambient noise...")
        with self._mic as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ready.")

    @property
    def engine(self) -> pyttsx3.Engine:
        self._engine
    
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
        """Return transcribed speech from microphone audio."""
        
        # Listen for speech
        print("Listening...")
        with self._mic as source:
            try:
                audio = self._recognizer.listen(source=source,
                                                timeout=timeout,
                                                phrase_time_limit=phrase_limit)
            except Exception:
                print("Nothing recognized...")
                return None

        # Convert audio to byte string; Whisper expects 16 kHz mono
        # float32 samples in [-1.0, 1.0] range
        raw = audio.get_raw_data(convert_rate=16000, convert_width=2)

        # Reinterpret byte buffer as array of 16-bit signed integers.
        # Values in range -32768 to 32767 converted to range -1.0 to 1.0
        samples = np.frombuffer(raw, dtype=np.int16).astype(
            np.float32) / 32768.0

        # Transcribe audio samples to text and return
        result = self._model.transcribe(samples, language="en", fp16=False)
        text = result["text"].strip()
        if not text:
            print("Nothing recognized...")
            return None
        print(f"Heard: {text}")
        return text.lower()

    def make_choice(self,
                    choices: list[str],
                    invalid_response: str,
                    timeout: int | None = None,
                    phrase_limit: int | None = None) -> str:
        """Listen while spoken phrase invalid or any word in spoken phrase is
        not in list of choices. Return the first occurring phrase in spoken
        phrase present in list of phrase choices."""
        result = self.listen(timeout, phrase_limit)
        while result is None or not any(
                item in _strip_symbols(result) for item in choices):
            self.speak(invalid_response)
            result = self.listen(timeout, phrase_limit)
        return next(
            (item for item in choices if item in _strip_symbols(result)), "")
        
    def list_voices(self) -> None:
        # Get the list of all available voices
        voices = self._engine.getProperty('voices')

        # Loop through and listen to each voice option
        for index, voice in enumerate(voices):
            print(f"Index: {index} | ID: {voice.id} | Name: {voice.name} | Languages: {voice.languages}")

            # Switch to the current voice in the loop
            self._engine.setProperty('voice', voice.id)
            self.speak(f"Testing voice number {index}")
