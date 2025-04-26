# ![3473607](https://github.com/user-attachments/assets/3facb286-61f0-45fb-b87f-71fd184a0bfb)

# 🤖 Mifos Community AI Chatbot

Welcome to the Mifos Community AI project! This innovative tool is designed to improve support and accessibility for the global Mifos & Fineract community using the power of Generative AI.

##  Overview

As Mifos and Fineract applications grow in complexity and adoption, effective support becomes crucial. This chatbot offers a smarter way to assist implementers, developers, and new users—providing instant, intelligent responses to questions using AI.

## Why It Matters ?

- 🌐Community is growing rapidly → more queries, higher support demand.
- Current help via Slack or docs is inconsistent and delayed.
- Documentation is scattered → tough for new users to navigate.
- Response time depends on who’s available → not reliable.
- 🤖 This bot = 24/7 support + faster onboarding + reduced load on community mentors.

## 🎯 Project Goals

- Build an intelligent chatbot to answer queries about Mifos/Fineract.
- Integrate GPT models to improve understanding and answer generation.
- Guide users to relevant documentation and code snippets.
- Pre-train using real Slack Q&A and improve iteratively.
- Make support fast, consistent, and always available.

---

## Table of Contents

- [Project Overview](#mifos-community-ai-chatbot)
- [Goals & Why It Matters](#why-it-matters)
- [Features](#features)
- [Tech Stack](#technology-stack)
- [Getting Started](#installation)
- [How to Use](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Translation Tool](#translation-helper-tool)
- [Contributing](#contributing)
- [Resources](#resources)


  ---

## 💡 Features

> The Mifos Community AI Chatbot brings powerful capabilities to simplify and support your journey with Mifos and Fineract:

- **🗣️ Natural Language Understanding:**  
  Understands and interprets user queries just like a human would.

- **🤖 Smart Responses with OpenAI GPT:**  
  Leverages GPT models to generate accurate and helpful replies.

- **📚 Instant Access to Documentation and Code:**  
  Retrieves relevant snippets from the Mifos/Fineract codebase using vector search.

- **🗂️ Supports Multiple File Types:**  
  Easily searches across TypeScript, HTML, Markdown, Kotlin, JavaScript files and more.

- **Simple & Friendly Interface:**  
  Built with Gradio for a clean and smooth user experience.

---

## Technology Stack

> The chatbot is built with a modern, scalable stack to ensure a seamless AI experience:

- **Python 3.8+** — The core programming language powering the backend.
- **LangChain** — For handling natural language processing tasks and chaining AI models.
- **OpenAI GPT / Gemini AI** — To generate intelligent, human-like responses.
- **ChromaDB** — For storing and retrieving vector embeddings efficiently.
- **Gradio** — For building an intuitive and interactive user interface.

---

## ⚙️ Installation

To set up and run the Mifos Chatbot locally:

### 1. Clone the Repository:

```bash
git clone https://github.com/openMF/community-ai.git
cd Web-App
```

### 2. Install Dependencies:

```bash
pip install -r requirements.txt
```

Make sure you have **Python 3.8+** installed.

### 3. Set up your API Key:

Create a `.env` file in the project root with the following:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```
**OR**
```plaintext
GEMINI_API_KEY=your-gemini-api-key
```

---


1. Clone the repository:
   ```
   git clone https://github.com/openMF/community-ai.git
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
   
3. Set up your OpenAI API key:
   Create a `.env` file in the root directory and add:
   ```
   OPENAI_API_KEY= "your_api_key_here"
   ```
   
4. Navigate to Web-App directory:
   ```
   cd Web-App
   ```
   

## Usage

You can run the Mifos Chatbot in two ways:

### ▶️ Run Locally (Jupyter Notebook)

1. Launch Jupyter Notebook:

   ```bash
   jupyter notebook
   ```

2. Open the `web-app_bot.ipynb` file.

3. Run the notebook cells one by one.

4. Interact with the chatbot via the Gradio interface:
   - Enter your query in the input box.
   - Click **Submit** or press **Enter**.
   - Get instant responses based on the Mifos/Fineract codebase and docs!

---

### 🌐 Use Deployed Chatbots (No Setup Needed!)

Instantly access the bots hosted on Hugging Face Spaces:

- [Web App Bot](https://huggingface.co/spaces/MifosBot/Web-App)
- [Mifos Mobile Bot](https://huggingface.co/spaces/MifosBot/Mifos-Mobile)
- [Mobile Wallet Bot](https://huggingface.co/spaces/MifosBot/Mobile-Wallet)
- [Android Client Bot](https://huggingface.co/spaces/MifosBot/Android-Client)

No installation, just open the link and start asking questions! 🎯

---

## 🗂️ Project Structure

Here's how the repository is organized:

| Path/Folder                        | Description |
| :---------------------------------- | :---------- |
| `web-app/`                          | Contains Mifos Web App files analyzed by the chatbot. |
| `web-app_bot.ipynb`                 | Jupyter Notebook to run the chatbot locally. |
| `web_app_vector_storage_metadata/`  | Stores vector embeddings for fast information retrieval. |
| `tools/translation-helper/`         | (New!) Gemini-powered Translation Helper Tool. |
| `requirements.txt`                  | Python dependencies needed for running the chatbot and translation tool. |
| `CodeCommentingScript.py`           | Script for pre-processing the codebase and generating vector embeddings. |

---

## How It Works

- The chatbot processes and indexes the Mifos codebase, creating vector embeddings for efficient retrieval.
- When a user asks a question, the system finds the most relevant code snippets or documentation.
- The chatbot then uses GPT models to generate a human-like response based on the retrieved information.
- Responses focus on file organization, key components, and project structure.
  
---

## Translation Helper Tool (Gemini AI-based)

This tool enables seamless translation of English text into 35+ languages using Google's Gemini 2.0 Flash model, helping bridge language barriers across the Mifos community.

### Features

- 🌍 Multilingual support for 35+ global languages  
- 🎭 Formal/informal tone switch for contextual translations  
- 🤖 Powered by Gemini 2.0 Flash via Google Generative AI  
- 🔁 Trigger translation via Enter key or button  
- 🎨 Built using Gradio for a minimal, user-friendly UI  

### Getting Started

1. Clone the repo and navigate to the helper tool:
```bash
cd tools/translation-helper
```
2. Create a `.env` file and add your Gemini API key:
```plaintext
GEMINI_API_KEY=your-gemini-api-key
```
3. Run the app:
```bash
   python app.py
```
5. In the UI:

   - Enter English text.
   - Choose your target language from the dropdown.
   - Optionally check "Use Formal Tone".
   - Hit Enter or click "Translate 🔁" to get results.

### Why Use This Tool?

- Makes translation fast and intuitive for users across the globe
- Improves accessibility and inclusiveness in the Mifos ecosystem
- Encourages multilingual contributions and collaboration

### Note

- The `.env` file is gitignored to ensure your API key remains private and secure.

---

## Contributing

We welcome your ideas, bug reports, and contributions!
- Fork the repo
- Create a feature branch
- Submit a Pull Request

Let's build the future of community support together! 

---

## Links and Resources

For more information about Mifos and Fineract, 
visit [Mifos.org](https://mifos.org/) or join our [Mifos Slack Channel](https://mifos.slack.com/)
