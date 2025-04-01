# Slack Scraper Bot

## Overview
The Slack Scraper Bot is a project designed to facilitate the extraction and processing of messages from Slack channels. It includes various scripts for converting JSON data into a clean text format, removing personal identifiable information (PII), and interacting with the Mifos Slack community through a Jupyter Notebook.

### extract.py
This Python script converts a JSON file scraped from a Slack channel into a clean text file. It processes messages and formats them for easier readability.

### pii_removal.py
This Python script removes personal identifiable information (PII) such as names, addresses, and social handles from the text to comply with privacy regulations.

### demo_bot.ipynb
This Jupyter Notebook serves as a Retrieval-Augmented Generation (RAG) agent that interacts with the gsoc_channel from the Mifos Slack community. It requires OpenAI and Pinecone API keys for functionality.

### repo_parser.py
This script converts the content of a github repo into a text file. This can be used with a vector db to create a knowledge base.

### vector_db.sh
This script, based on WasmEdge, converts text files into a vector database. It can be used with a sample chatbot UI utilizing quantized open-source models.

### data/test.json
This file contains sample data in JSON format that is used by the extract.py script for processing.


## Usage Guidelines
- To create a txt file of messages from a Slack channel, run the `extract.py` script with the appropriate JSON file.
- Use `pii_removal.py` to clean the extracted text of any personal information.
- Open `demo_bot.ipynb` in Jupyter Notebook to interact with the Mifos Slack community.
- Execute `vector_db.sh` to convert text files into a vector database for use with the chatbot UI.

## License
This project is licensed under the MPL-2.0 License - see the LICENSE file for details.