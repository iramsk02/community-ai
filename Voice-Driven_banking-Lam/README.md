# Voice-Driven Banking Assistant

This project is a complete, end-to-end Voice Banking Assistant built to provide a hands-free, multilingual interface for common banking tasks. This is a contribution to the [OpenMF Community AI Initiative](https://github.com/openMF/community-ai/issues/5#issue-2922033762).

The application features a React frontend that captures user audio and a robust FastAPI backend that processes the request using a pipeline of modern AI services and by to use a LLM to give commands/prompts to produce the  Basic LAM Model.


The included React application serves as a demonstration client to visualize and interact with the backend's capabilities.

The backend is designed as a standalone service that can be easily integrated into other applications, such as those within the Mifos ecosystem. It exposes a powerful conversational endpoint that requires only a user identifier, an audio file, and a session ID to function. Internally, it orchestrates a complete pipeline of AI services to understand the user's request, securely fetch their financial data, and generate a natural spoken response.


FLow Chat:

https://mifosforge.jira.com/wiki/spaces/RES/whiteboard/4641226783


<img width="1872" height="756" alt="image" src="https://github.com/user-attachments/assets/ec431b78-a8ed-4c03-91e9-6374cd1cd0d6" />

The ultimate vision is to create a specialized, domain-specific AI agent for the banking sector, capable of handling complex, multi-turn financial queries in multiple languages.
## Features

- **End-to-End Conversational AI**: Speak a command and receive a spoken audio response.
- **Multilingual Support**: Fully functional in English, Hindi, Spanish, French, and German and  many religious languages
- **Core Banking Intents**:
  - Check account balance.
  - List recent transactions with on-screen details.
  - Securely transfer money using a multi-step confirmation and email OTP flow.
- **Stateful Conversations**: Remembers the context of the conversation to handle follow-up questions.
- **Polished UI**: Features a dynamic, animated microphone UI that provides real-time feedback for recording, processing, and speaking states.
- **Admin/Debug Tools**: Includes a logs page to review full conversation histories for any user.

## Tech Stack

- **Backend**: Python, FastAPI
- **AI Services**:
  - **STT**: Hugging Face Transformers (Whisper)
  - **NLU & NLG**: Google Gemini API (via Vertex AI)
  - **TTS**: Hugging Face Transformers (MMS)
- **Database**: Google Firestore
- **Frontend**: React, Tailwind CSS

## Setup and Installation

### Prerequisites
- Python 3.11
- Node.js and npm
- FFmpeg (installed and added to your system's PATH)

### Backend Setup

1.  **Navigate to the Backend Directory**:
    ```bash
    cd Backend
    ```
2.  **Create and Activate a Virtual Environment**:
    ```bash
    # Create
    python -m venv .venv
    # Activate (Windows PowerShell)
    .\.venv\Scripts\Activate.ps1
    ```
3.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables**:
    - For Detailed Setup, please read the Setup for environment pdf. 
    - Copy the `.env.example` file to a new file named `.env`.
    - Fill in the required credentials for your Google Cloud/Firestore project, Hugging Face account, and email service.

6.  **Populate Firestore with Mock Data**:
    - To get started with test data, run the data population script:
    ```bash
    python data_populate.py
    ```
    - This will create a test user with a savings account, a current account, and several sample transactions in your Firestore database.

### Frontend Setup

1.  **Navigate to the Frontend Directory**:
    ```bash
    cd frontend
    ```
2.  **Install Node.js Dependencies**:
    ```bash
    npm install
    ```

## Running the Application

You will need to run the backend and frontend servers in two separate terminals.

**Terminal 1 (from `Backend` folder):**
```bash
uvicorn main:app --reload
```

**Terminal 2 (from 'Frontend' folder navigate to voicedriven project):**
```bash
npm install
npm start
```
Your application will be available at http://localhost:3000.


See the drive link video for what kind of questions and queries users can ask for this initial Phase.

https://drive.google.com/file/d/1HvkQ6v2KEk92pOyfSE7oKp1107CTQq-Z/view?usp=sharing



https://github.com/user-attachments/assets/6ea9464e-fc70-420e-9cca-6b88ecd2dd88


