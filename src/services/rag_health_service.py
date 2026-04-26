import logging
import os
from typing import Dict, List, Optional

from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from transformers import pipeline

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants & Configuration
# ---------------------------------------------------------------------------
PERSIST_DIR = "data/health_kb"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama3:latest"
TRANSLATOR_MODEL = "facebook/nllb-200-distilled-600M"

# NLLB-200 Language Codes for Indian Languages + English
NLLB_LANG_CODES = {
    "en": "eng_Latn",
    "hi": "hin_Deva",  # Hindi
    "ta": "tam_Taml",  # Tamil
    "te": "tel_Telu",  # Telugu
    "bn": "ben_Beng",  # Bengali
    "mr": "mar_Deva",  # Marathi
    "gu": "guj_Gujr",  # Gujarati
    "kn": "kan_Knda",  # Kannada
    "ml": "mal_Mlym",  # Malayalam
}

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
HEALTH_PROMPT_TEMPLATE = """You are a helpful, empathetic health information assistant. 
Your goal is to provide general health education based ONLY on the provided context.
NEVER diagnose a patient. ALWAYS recommend consulting a doctor or healthcare professional.
Be warm, clear, and non-alarmist.

Context:
{context}

User Question: {question}

Helpful Answer:"""

HEALTH_PROMPT = PromptTemplate(
    template=HEALTH_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

# ---------------------------------------------------------------------------
# Service Definition
# ---------------------------------------------------------------------------
class RAGHealthService:
    def __init__(self):
        logger.info("Initializing RAG Health Service...")
        
        # 1. Initialize LLM (Ollama running locally)
        logger.info(f"Connecting to Ollama model: {LLM_MODEL}")
        self.llm = Ollama(model=LLM_MODEL, temperature=0.3)
        
        # 2. Initialize Embeddings & Vector Store
        logger.info(f"Loading HuggingFace Embeddings: {EMBEDDING_MODEL}")
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        logger.info(f"Loading ChromaDB from {PERSIST_DIR}")
        if not os.path.exists(PERSIST_DIR):
            logger.warning("VectorDB directory not found. Please run build_knowledge_base.py first!")
        
        self.vectorstore = Chroma(
            persist_directory=PERSIST_DIR, 
            embedding_function=self.embeddings
        )
        
        # 3. Setup RAG Chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": HEALTH_PROMPT},
            return_source_documents=True
        )
        
        # 4. Initialize Translator Pipeline
        logger.info(f"Loading NLLB-200 Translation model: {TRANSLATOR_MODEL}")
        self.translator = pipeline(
            "translation",
            model=TRANSLATOR_MODEL,
            max_length=512
        )
        logger.info("✅ RAG Health Service initialized successfully.")

    def _is_emergency(self, text: str) -> bool:
        """Detect life-threatening keywords."""
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "can't breathe", 
            "cannot breathe", "shortness of breath", "bleeding heavily", 
            "unconscious", "suicide", "kill myself", "severe pain"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in emergency_keywords)

    def _translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        """Translate text using NLLB-200."""
        if src_lang == tgt_lang:
            return text
            
        src_code = NLLB_LANG_CODES.get(src_lang, "eng_Latn")
        tgt_code = NLLB_LANG_CODES.get(tgt_lang, "eng_Latn")
        
        try:
            result = self.translator(text, src_lang=src_code, tgt_lang=tgt_code)
            return result[0]['translation_text']
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    async def process_message(self, message: str, language: str = "en") -> Dict:
        """
        Process user message via local RAG pipeline with multilingual support.
        """
        logger.info(f"Processing message in language: {language}")
        
        # 1. Translate to English if needed
        english_message = self._translate(message, src_lang=language, tgt_lang="en")
        
        # 2. Safety check for emergency keywords
        if self._is_emergency(english_message):
            emergency_text = (
                "🚨 MEDICAL EMERGENCY DETECTED 🚨\n"
                "Please seek immediate medical attention. "
                "In India, call 108 for an Ambulance or 112 for General Emergency immediately. "
                "Do not wait for advice here."
            )
            # Translate emergency message back to user's language
            translated_emergency = self._translate(emergency_text, src_lang="en", tgt_lang=language)
            
            return {
                "response": translated_emergency,
                "sources": [],
                "confidence": 1.0,
                "follow_up_questions": [],
                "disclaimer": "This system detects potential emergencies and redirects to professional help."
            }
            
        # 3. RAG Retrieval & LLM Generation
        logger.info("Executing RAG chain...")
        try:
            result = self.qa_chain({"query": english_message})
            english_response = result['result']
            source_docs = result.get('source_documents', [])
            sources = [doc.metadata.get('source', 'Unknown') for doc in source_docs]
        except Exception as e:
            logger.error(f"RAG QA failed: {e}")
            english_response = "I'm sorry, I couldn't process your request at the moment. Please consult a doctor."
            sources = []

        # 4. Translate response back to user's language
        final_response = self._translate(english_response, src_lang="en", tgt_lang=language)
        
        # 5. Extract a standard disclaimer
        disclaimer = (
            "Disclaimer: I am an AI health educator, not a doctor. "
            "Please consult a qualified healthcare professional for medical advice."
        )
        translated_disclaimer = self._translate(disclaimer, src_lang="en", tgt_lang=language)

        return {
            "response": final_response,
            "sources": list(set(sources)),
            "confidence": 0.85,  # Heuristic confidence
            "follow_up_questions": [], # Could be generated by another LLM call if needed
            "disclaimer": translated_disclaimer
        }
