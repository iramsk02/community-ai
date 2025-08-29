# In models/api_models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ConverseResponse(BaseModel):
    user_text: str
    response_text: str
    audio_data: str
    # NEW: Add a flexible data field for extra information
    data: Optional[Dict[str, Any]] = None
    pending_action: Optional[Dict[str, Any]] = None