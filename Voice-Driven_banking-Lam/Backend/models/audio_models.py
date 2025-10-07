from pydantic import BaseModel

class AudioInput(BaseModel):
    """
    Model for receiving audio data, typically as a Base64 encoded string.
    """
    audio_data: str
    language: str = "en"  # Default language is English
    session_id: str | None = None  # Optional session ID for tracking

class TextOutput(BaseModel):
    """
    Model for responding with transcribed text.
    """
    text: str

class AudioOutput(BaseModel):
    """
    Model for responding with generated audio data.
    """
    audio_data: str # Base64 encoded audio string
    content_type: str = "audio/wav"