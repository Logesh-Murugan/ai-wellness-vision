#!/usr/bin/env python3
"""
Build Knowledge Base for RAG Health Service
============================================
Scrapes/loads basic health fact sheets (WHO, MedlinePlus style),
chunks them into 500-token passages, embeds them using MiniLM,
and stores them in a local Chroma vector database.
"""

import logging
import os
from pathlib import Path
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
PERSIST_DIR = "data/health_kb"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# A mix of URLs and raw text for a robust initial knowledge base
HEALTH_URLS = [
    "https://medlineplus.gov/ency/article/000303.htm",  # Diabetes
    "https://medlineplus.gov/ency/article/000468.htm",  # Hypertension
    "https://medlineplus.gov/ency/article/000821.htm",  # Asthma
]

RAW_TEXT_FALLBACKS = [
    Document(
        page_content="""
        Skin Cancer and Sun Safety: 
        Skin cancer is the most common form of cancer. To protect yourself, always wear a broad-spectrum 
        sunscreen with an SPF of at least 30, even on cloudy days. Reapply every two hours, or after swimming 
        or sweating. Seek shade between 10 a.m. and 4 p.m., when the sun's rays are strongest. 
        Wear protective clothing, such as long-sleeved shirts, pants, and wide-brimmed hats.
        Warning signs include changes in size, shape, or color of a mole. Always consult a dermatologist 
        for a professional skin check.
        """,
        metadata={"source": "General Health Education - Skin"}
    ),
    Document(
        page_content="""
        Nutrition and Diet:
        A healthy diet includes a variety of fruits, vegetables, whole grains, lean proteins, and healthy fats.
        Limit intake of added sugars, sodium, and saturated fats. Drinking plenty of water is essential for 
        hydration. Caloric needs vary based on age, sex, and activity level. Eating a balanced diet can help 
        prevent chronic diseases such as heart disease, diabetes, and obesity.
        """,
        metadata={"source": "General Health Education - Nutrition"}
    ),
    Document(
        page_content="""
        Mental Health and Stress Management:
        Chronic stress can lead to serious health issues, including hypertension, anxiety, and depression.
        Effective stress management techniques include regular physical activity, mindfulness meditation, 
        deep breathing exercises, and getting 7-9 hours of quality sleep per night. If you feel overwhelmed,
        it is important to speak with a mental health professional or counselor.
        """,
        metadata={"source": "General Health Education - Mental Health"}
    )
]

def build_kb():
    logger.info("Initializing Knowledge Base Build Process...")
    
    # 1. Load Data
    documents = []
    logger.info(f"Loading web documents from {len(HEALTH_URLS)} URLs...")
    try:
        loader = WebBaseLoader(HEALTH_URLS)
        web_docs = loader.load()
        documents.extend(web_docs)
        logger.info(f"Successfully loaded {len(web_docs)} web documents.")
    except Exception as e:
        logger.warning(f"Failed to load some web documents: {e}")
        
    logger.info("Injecting curated raw health documents...")
    documents.extend(RAW_TEXT_FALLBACKS)

    if not documents:
        logger.error("No documents loaded. Aborting.")
        return

    # 2. Chunking
    logger.info("Chunking documents (chunk_size=500, overlap=50)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Generated {len(chunks)} text chunks.")

    # 3. Embedding and Storage
    logger.info(f"Initializing Embeddings Model: {EMBEDDING_MODEL}")
    logger.info("This may download the model if it is the first run...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    logger.info(f"Storing vectors in ChromaDB at {PERSIST_DIR}...")
    os.makedirs(PERSIST_DIR, exist_ok=True)
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )
    
    # Force persist to disk
    vectorstore.persist()
    logger.info("✅ Knowledge Base successfully built and persisted to disk!")


if __name__ == "__main__":
    build_kb()
