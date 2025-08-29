# backend/services/stt_whisper.py

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import librosa
import logging
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
# Configure logging
logger = logging.getLogger(__name__)

# --- Global variables to hold the model and processor ---
# This prevents reloading the model every time we transcribe.
model = None
processor = None
device = "cuda:0" if torch.cuda.is_available() else "cpu"

def initialize_stt_model():
    """
    Initializes the Speech-to-Text model and processor from Hugging Face.
    This should be called once when the application starts.
    """
    global model, processor
    
    if model is not None and processor is not None:
        logger.info("STT model already initialized.")
        return

    try:
        # The model checkpoint to use. "whisper-base" is a good starting point 
        # the model is not able to transcribe Hindi, so we will use the "whisper-base" model
        # which is a smaller model that can handle multiple languages.

        # model_id = "openai/whisper-base"
        model_id = "openai/whisper-large-v3"  # Use a larger model for better accuracy
        
        logger.info(f"Initializing STT model '{model_id}' on device: {device}")
        
        # huggisface tkoen
        hf_token = os.getenv("HUGGING_FACE_TOKEN")
        if not hf_token:
            raise ValueError("HUGGING_FACE_TOKEN not found in .env file. This is required for accessing the model.")
        # Load the processor and model
  # Load the processor and model, passing the token for authentication
        processor = AutoProcessor.from_pretrained(model_id, token=hf_token) 
        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, token=hf_token).to(device) 
        
        logger.info("STT model initialized successfully. 🎤") 
        
    except Exception as e:
        logger.error(f"Error initializing STT model: {e}", exc_info=True)
        model = None
        processor = None
        raise

# ... (imports and initialize_stt_model function are the same) ...

def transcribe_audio_file(audio_file_path: str, language: str = "en") -> str | None:
    """
    Transcribes audio in a specific language using the Whisper model.

    Args:
        audio_file_path (str): The path to the audio file.
        language (str): The language code (e.g., "en", "hi").
    
    Returns:
        str | None: The transcribed text, or None if an error occurs.
    """
    if not model or not processor:
        logger.error("STT model is not initialized.")
        return None

    try:
        logger.info(f"Transcribing audio file: {audio_file_path} in language: {language}")
        audio_waveform, sampling_rate = librosa.load(audio_file_path, sr=16000)
        
        input_features = processor(
            audio_waveform, 
            sampling_rate=sampling_rate, 
            return_tensors="pt"
        ).input_features.to(device)

        # --- THIS IS THE KEY CHANGE ---
        # 1. Get the special tokens for the target language to force transcription.
        forced_decoder_ids = processor.get_decoder_prompt_ids(language=language, task="transcribe")
        
        # 2. Pass the language tokens to the model.generate() call.
        predicted_ids = model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
        # --- END OF CHANGE ---
        
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
        
        transcribed_text = transcription[0].strip()
        logger.info(f"Transcription successful: '{transcribed_text}'")
        
        return transcribed_text

    except Exception as e:
        logger.error(f"An error occurred during transcription: {e}", exc_info=True)
        return None
# Example usage:

# backend/main.py

import asyncio

def main():
    print("Starting Speech-to-Text Service...")

    # 1. Initialize the STT model on startup
    initialize_stt_model()
# English: en

# Hindi: hi

# Spanish: es

# French: fr

# German: de
    # --- Example Usage ---
    # Use the correct path where 'english.wav' is actually located
    test_audio_path = os.path.join(os.path.dirname(__file__), "english.wav")
    if not os.path.exists(test_audio_path):
        print(f"❌ Audio file not found: {test_audio_path}")
        print(
            "Please provide a valid audio file at the specified path before running transcription.")
        return

    print(f"\nAttempting to transcribe: {test_audio_path}")
    transcribed_text = transcribe_audio_file(test_audio_path, 'en')

    if transcribed_text:
        print(f"✅ Transcribed Text: {transcribed_text}")
    else:
        print("❌ Failed to transcribe audio.")

if __name__ == "__main__":
    main()