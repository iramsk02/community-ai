# backend/services/tts_hf.py

import torch
from transformers import AutoProcessor, AutoModelForTextToWaveform
import soundfile as sf
import logging
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
logger = logging.getLogger(__name__)

tts_cache = {}
device = "cuda:0" if torch.cuda.is_available() else "cpu"

async def generate_speech(text: str, language: str = "eng", output_file: str = "output.wav"):
    """
    Asynchronously generates speech from text using the MMS TTS model.
    """
    try:
        model_id = f"facebook/mms-tts-{language}"
        
        # Read the token from the environment to authenticate
        hf_token = os.getenv("HUGGING_FACE_TOKEN")
        if not hf_token:
            raise ValueError("HUGGING_FACE_TOKEN not found in .env file.")

        if language in tts_cache:
            processor, model = tts_cache[language]
        else:
            logger.info(f"Loading TTS model '{model_id}' for the first time...")
            
            # Pass the token when loading the processor and model
            processor = await asyncio.to_thread(AutoProcessor.from_pretrained, model_id, token=hf_token)
            model = await asyncio.to_thread(AutoModelForTextToWaveform.from_pretrained, model_id, token=hf_token)
            model.to(device)
            
            tts_cache[language] = (processor, model)
            logger.info(f"TTS model for '{language}' loaded and cached.")

        inputs = processor(text=text, return_tensors="pt").to(device)

        def _generate():
            with torch.no_grad():
                return model(**inputs).waveform.cpu().numpy().squeeze()
        
        speech_waveform = await asyncio.to_thread(_generate)
        
        sampling_rate = model.config.sampling_rate
        
        def _write_file():
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            sf.write(output_file, speech_waveform, sampling_rate)

        await asyncio.to_thread(_write_file)
        
        logger.info(f"Speech successfully generated and saved to '{output_file}'")
        return output_file

    except Exception as e:
        logger.error(f"Failed to generate speech for language '{language}': {e}", exc_info=True)
        return None
# backend/main.py

import asyncio

async def main():
    """
    Demonstrates concurrent Text-to-Speech generation for multiple languages.
    """
    print("Starting Text-to-Speech demonstration...")
    tasks = [
        generate_speech(
            text="Your current account balance is five toustand and fourty seven rupees",
            language="eng",
            output_file="output/english.wav" # Save to an output sub-directory
        ),
        # generate_speech(
        #     text="नमस्ते, आपके वॉइस बैंकिंग सहायक में आपका स्वागत है।",
        #     language="hin",
        #     output_file="output/hindi.wav"
        # ),
        # generate_speech(
        #     text="Hola, bienvenido a tu asistente bancario por voz.",
        #     language="spa",
        #     output_file="output/spanish.wav"
        # )
    ]

    # Run all tasks concurrently and wait for them all to complete
    results = await asyncio.gather(*tasks)

    print("\n--- Generation Complete ---")
    for result_path in results:
        if result_path:
            print(f"✅ Speech saved to: {result_path}")
        else:
            print("❌ A speech generation task failed.")


if __name__ == "__main__":
    asyncio.run(main())