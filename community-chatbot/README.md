# Community Chatbot for Mifos Projects

An advanced, extensible chatbot platform designed for seamless integration with Jira, Slack, and GitHub. Built with a FastAPI (Python) backend and a Next.js (React) frontend, it leverages LangChain and OpenAI to provide intelligent, conversational automation and agent-based workflows. The platform features a modern UI, robust authentication, and is easily customizable for a variety of community and project management

This project was completed during Google Summer of Code (GSOC) 

---

## Features

- **Jira Agent**: Query Jira using natural language, generate JQL, and summarize results with LLM fallback.
- **Slack Agent**: Manage conversations and interact with Slack using agent tools to summarize the conversations inside our channel.
- **Github Agent**: Interact with your repo to ask questions related to the project in natural language.
- **Frontend Chatbot UI**: Modern, responsive chat interface built with Next.js and Tailwind CSS.
- **Authentication**: User sign-in and sign-up flows.
- **Extensible UI Components**: Reusable UI library for rapid development.

---

## Directory Structure

```
Chatbot_for_gsoc/
│
├── app/                # Next.js frontend (pages, components, styles)
├── components/         # React UI components (chatbot, UI library)
├── hooks/              # React hooks
├── lib/                # Frontend utility libraries
├── public/             # Static assets
├── scripts/            # FastAPI backend (Jira, Slack and Github agents)
├── styles/             # Global styles
├── ...
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+

### Backend Setup

1. **Create and activate a virtual environment**  
   On Unix/macOS:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   On Windows:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install Python dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**  
   A) Create a `.env` file with following credentials:
   ```
    NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
    OPENAI_API_KEY=
    SLACK_BOT_TOKEN=
    JIRA_API_TOKEN=
    JIRA_USERNAME=
    JIRA_INSTANCE_URL=
    JIRA_CLOUD=
    GITHUB_APP_ID=
    GITHUB_REPOSITORY=
    GITHUB_BRANCH=
    GITHUB_BASE_BRANCH=
    GITHUB_APP_PRIVATE_KEY=
   ```
   B) Create an `.env.local` file with these credentials (auth):
   ```
    GOOGLE_CLIENT_ID=
    GOOGLE_CLIENT_SECRET=
    NEXTAUTH_SECRET=
    NEXTAUTH_URL=http://localhost:3000
   ```
4. **Run FastAPI server**  
   **Note**:- Uncomment this line in github_agent.py
   ```os.environ['GITHUB_APP_PRIVATE_KEY']``` as there is some issue loading it from the env file and then run this bash command to start the backend server.
   ```bash
   ./scripts/run_backend.sh
   ```

### Frontend Setup

1. **Install Node dependencies**  
Run this bash command in the root directory of the project. 
   ```bash
   npm install
   ```

2. **Run Next.js app**  
   ```bash
   npm run dev
   ```

---


## To Do

- **Add new agent tools**: Extend `scripts/`
- **UI customization**: Modify components in `components/` and styles in `styles/`.
- **Database Integration**: Add support for a database to store user history.
- **And a lot of code cleanup** 😊
