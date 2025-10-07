from pydantic import BaseModel
from typing import Optional

class VoiceEnrollmentRequest(BaseModel):
    """
    Request to enroll a user's voiceprint.
    """
    user_id: str
    audio_data: str # Base64 encoded audio string

class VoiceVerificationRequest(BaseModel):
    """
    Request to verify a user's voice against their enrolled print.
    """
    user_id: str
    audio_data: str # Base64 encoded audio string

class AuthResponse(BaseModel):
    """
    Response indicating the success or failure of a voice authentication attempt.
    """
    authenticated: bool
    confidence_score: Optional[float] = None
    message: str