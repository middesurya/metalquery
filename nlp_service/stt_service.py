import os
import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class WhisperSTT:
    def __init__(self):
        self._model = None
        
    def initialize(self):
        """
        Initialize the Faster-Whisper model.
        Using 'small' model which is a good balance of speed/accuracy for CPU.
        """
        if self._model is not None:
            return

        try:
            logger.info("🎙️ Loading Faster-Whisper model (small) on CPU...")
            # model_size can be "tiny", "base", "small", "medium", "large-v3"
            # "small" is ~461MB VRAM/RAM
            # "base" is ~142MB
            # "tiny" is ~72MB
            # quantization="int8" reduces memory usage with minimal accuracy loss
            self._model = WhisperModel("small", device="cpu", compute_type="int8")
            logger.info("✓ Faster-Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Faster-Whisper model: {e}")
            raise e

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe the given audio file using Faster-Whisper.
        """
        if self._model is None:
            self.initialize()
            
        try:
            # context: Provide context to help the model with domain-specific terms and starting abruptly
            segments, info = self._model.transcribe(
                audio_file_path, 
                beam_size=5,
                language="en",
                initial_prompt="This is a voice command for a manufacturing dashboard query. The user asks: "
            )
            
            logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")

            # Collect text from generator
            text_segments = []
            for segment in segments:
                text_segments.append(segment.text)
                
            final_text = " ".join(text_segments).strip()
            return final_text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise e

# Singleton instance
stt_service = WhisperSTT()
