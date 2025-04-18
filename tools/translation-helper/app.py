import os
import gradio as gr
from dotenv import load_dotenv
import google.generativeai as genai

# Load API Key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Supported languages (from the list you shared)
supported_languages = [
    "Arabic", "Bengali", "Bulgarian", "Chinese (Simplified)", "Chinese (Traditional)", 
    "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Finnish", 
    "French", "German", "Greek", "Hebrew", "Hindi", "Hungarian", "Indonesian", 
    "Italian", "Japanese", "Korean", "Latvian", "Lithuanian", "Norwegian", 
    "Polish", "Portuguese", "Romanian", "Russian", "Serbian", "Slovak", 
    "Slovenian", "Spanish", "Swahili", "Swedish", "Thai", "Turkish", "Ukrainian", 
    "Vietnamese"
]

# Translation logic
def translate_text(input_text, target_language, formal):
    if target_language not in supported_languages:
        return "❌ Error: The selected language is not supported."
    
    tone = "formal" if formal else "informal"
    prompt = f"Translate the following text into {target_language} in a {tone} tone. Only provide the translated text without any explanation or additional commentary:\n\n{input_text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error: {e}"

# Gradio Interface
with gr.Blocks(title="Multilingual Translator") as app:
    gr.Markdown("# 🌐 AI Translator with Gemini 2.0 Flash")
    gr.Markdown("Type in English and translate to supported languages using Gemini 2.0 Flash")

    with gr.Row():
        input_text = gr.Textbox(label="Enter English text", placeholder="e.g. How are you doing?", interactive=True)
        language = gr.Dropdown(choices=supported_languages, label="Target Language")
        tone = gr.Checkbox(label="Use Formal Tone", value=True)
    
    translate_btn = gr.Button("Translate 🔁")
    output_text = gr.Textbox(label="Translated Output")

    # Trigger translation when "Enter" is pressed on the input_text textbox
    input_text.submit(fn=translate_text, inputs=[input_text, language, tone], outputs=output_text)

    # Button click still works as fallback
    translate_btn.click(fn=translate_text, inputs=[input_text, language, tone], outputs=output_text)

# Run app
if __name__ == "__main__":
    app.launch()
