import logging
import asyncio
import os
import uuid
from typing import Optional, Dict, Any
from firebase_admin import firestore
from dotenv import load_dotenv

load_dotenv()

# --- THIS IS THE KEY CHANGE (PART 1) ---
# Import the entire firestore_db module, not just the 'db' variable
from . import firestore_db

logger = logging.getLogger(__name__)

def _get_sessions_collection_ref():
    """Internal helper to get a consistent reference to the sessions collection."""
    # --- THIS IS THE KEY CHANGE (PART 2) ---
    # Always check the 'db' variable through the module to get the live client
    if not firestore_db.db: 
        return None
    
    app_id = os.getenv("__app_id", "default-app-id")
    return firestore_db.db.collection("artifacts").document(app_id).collection("sessions")


async def get_sessionid_history(session_id: str, user_id: str) -> dict:
    """
    Retrieves the entire session document, including history and pending actions.
    """
    sessions_ref = _get_sessions_collection_ref()
    if not sessions_ref: 
        return {} # Return an empty dict if reference fails
    
    def _get_doc():
        doc_ref = sessions_ref.document(session_id)
        doc = doc_ref.get()
        if doc.exists:
            session_data = doc.to_dict()
            # Security Check
            if session_data.get("user_id") == user_id:
                # Return the whole session data dictionary
                return session_data
        # Return empty dict if no doc or user doesn't match
        return {}
    
    return await asyncio.to_thread(_get_doc)


async def append_to_session(
    session_id: str,
    user_id: str,
    user_query: str,
    assistant_response: str,
    pending_action: Optional[Dict[str, Any]] = None
):
    """
    Appends the latest turn to the conversation history and updates pending actions.
    
    Args:
        session_id: Unique identifier for the session
        user_id: User's identifier
        user_query: User's input text
        assistant_response: Assistant's response text
        pending_action: Optional dictionary containing pending action details
    """
    sessions_ref = _get_sessions_collection_ref()
    if not sessions_ref: return

    def _update_doc():
        try:
            doc_ref = sessions_ref.document(session_id)
            turn_id = str(uuid.uuid4())
            
            # Create message entries with turn_id
            history_turn = [
                {"turn_id": turn_id, "role": "user", "content": user_query},
                {"turn_id": turn_id, "role": "assistant", "content": assistant_response}
            ]

            # Prepare the update data
            data_to_set = {
                "user_id": user_id,
                "last_updated": firestore.SERVER_TIMESTAMP,
                "messages": firestore.ArrayUnion(history_turn)
            }

            # Only include pending_action if it's provided
            if pending_action is not None:
                data_to_set["pending_action"] = pending_action
            elif pending_action is None:
                # If explicitly set to None, remove the field
                data_to_set["pending_action"] = firestore.DELETE_FIELD

            doc_ref.set(data_to_set, merge=True)
            logger.info(f"Successfully wrote turn {turn_id} to session {session_id}")
            
        except Exception as e:
            logger.error(f"!!! FAILED to write to session document {session_id}: {e}", exc_info=True)

    await asyncio.to_thread(_update_doc)