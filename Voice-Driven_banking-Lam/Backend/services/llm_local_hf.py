import logging
import torch
import transformers
import asyncio
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv() 

logger = logging.getLogger(__name__)
pipeline = None
# The model ID is correct for Mistral
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

try:
    logger.info(f"Initializing pipeline for local LLM '{MODEL_ID}'...")

    # We MUST read the token from the environment to access this model
    hf_token = os.getenv("HUGGING_FACE_TOKEN")
    if not hf_token:
        raise ValueError("HUGGING_FACE_TOKEN not found in .env file. This is required for gated models.")

    # Pass the token directly to the pipeline for authentication
    pipeline = transformers.pipeline(
        "text-generation",
        model=MODEL_ID,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
        token=hf_token
    )

    logger.info("Local LLM pipeline initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize local LLM pipeline: {e}", exc_info=True)
    pipeline = None

# The rest of the file remains the same...
async def get_llm_response(prompt: str) -> str | None:
    if not pipeline:
        logger.error("Cannot get LLM response because the pipeline is not initialized.")
        return None
    try:
        def _run_inference():
            # For Mistral, the chat template format is slightly different but works well
            messages = [
                {"role": "user", "content": prompt}
            ]

            # Call the pipeline
            outputs = pipeline(
                messages,
                max_new_tokens=512,
                do_sample=False,
            )
            
            # The pipeline returns the full chat history. We need the last message's content.
            generated_text = outputs[0]["generated_text"][-1]['content']
            
            json_start_index = generated_text.find('{')
            json_end_index = generated_text.rfind('}')
            
            if json_start_index != -1 and json_end_index != -1:
                return generated_text[json_start_index : json_end_index + 1]
            else:
                logger.warning(f"Could not find JSON in the LLM pipeline response: {generated_text}")
                return generated_text

        return await asyncio.to_thread(_run_inference)
    except Exception as e:
        logger.error(f"An error occurred while running the local LLM pipeline: {e}", exc_info=True)
        return None