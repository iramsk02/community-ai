# vector_db_integration.py
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def create_vector_database(documents, persist_directory="./slack_vectordb"):
    """
    Create a vector database from processed Slack messages.
    
    Args:
        documents (list): List of processed documents from slack_extractor
        persist_directory (str): Directory to persist the vector database
        
    Returns:
        VectorStore: The created vector database
    """
    # Initialize embeddings - you can replace with other embedding models
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Convert to Langchain documents
    langchain_docs = []
    for doc in documents:
        langchain_docs.append(
            Document(
                page_content=doc["content"],
                metadata=doc["metadata"]
            )
        )
    
    # Create and persist the vector database
    vectordb = Chroma.from_documents(
        documents=langchain_docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    
    return vectordb

def query_vector_database(query, persist_directory="./slack_vectordb", k=5):
    """
    Query the vector database.
    
    Args:
        query (str): The query string
        persist_directory (str): Directory where the vector database is persisted
        k (int): Number of results to return
        
    Returns:
        list: List of retrieved documents
    """
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    results = vectordb.similarity_search(query, k=k)
    
    return results

def generate_llm_response(query, persist_directory="./slack_vectordb", model_name="4o-mini", temperature=0):
    """
    Generate a response to a query using retrieved documents from the vector database as context.
    
    Args:
        query (str): The user's query
        persist_directory (str): Directory where the vector database is persisted
        model_name (str): The OpenAI model to use
        temperature (float): Controls randomness in the response (0 = deterministic, 1 = creative)
        
    Returns:
        str: The LLM's response
    """
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Load the vector database
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    # Create retriever
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    
    # Initialize LLM
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Create a custom prompt template
    template = """
    You are an assistant for Mifos community chat questions. Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    QA_PROMPT = PromptTemplate(
        template=template, 
        input_variables=["context", "question"]
    )
    
    # Create a retrieval QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": QA_PROMPT}
    )
    
    # Generate response using invoke instead of run (which is deprecated)
    response = qa_chain.invoke({"query": query})
    
    return response