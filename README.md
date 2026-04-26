# AI WellnessVision 🧠💚

An intelligent, **100% offline and privacy-first** wellness platform that combines computer vision, natural language processing, and medical heuristics to provide comprehensive health insights. 

> ⚠️ **Medical Disclaimer**: This tool is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers.

## ✨ Core Features Built

### 🖼️ **Multi-Modal Computer Vision Engine**
All models run completely locally on your device without making external API calls.
- **Skin Condition Detection**: Custom-trained `EfficientNet-B0` on the **HAM10000 Dataset** to classify 7 common skin lesions (Melanoma, BCC, etc.).
- **Food & Nutrition Analyzer**: Deep learning model trained on **Food-101**, equipped with fallback nutritional heuristics for dietary analysis.
- **Emotion Recognition**: High-accuracy facial analysis using **DeepFace** with a robust **FER (MTCNN)** fallback engine, mapping human emotions to holistic wellness scores.
- **Eye Health Analyzer**: Leverages native **OpenCV Haar Cascades** to detect eye aspect ratios for fatigue/squinting and HSV color isolation for redness/irritation from standard selfies. Features a mock-ready pipeline for Diabetic Retinopathy screening.

### 💬 **Local RAG Health Service**
- **100% Local NLP**: Powered by **Ollama (`llama3.2:3b`)** running entirely on local RAM.
- **Knowledge Base**: Curated health documents ingested, chunked, and embedded using `sentence-transformers/all-MiniLM-L6-v2` and stored locally in **ChromaDB**.
- **Multilingual Support**: Supports 7 Indian regional languages seamlessly using the offline **Meta NLLB-200-distilled-600M** translation model.
- **Emergency Safety Pipeline**: Instantly intercepts high-risk medical keywords (e.g., "chest pain", "suicide") to immediately provide local emergency contact numbers (108/112).

## 🚀 Technology Stack
- **AI/ML**: PyTorch, DeepFace, OpenCV, FER, LangChain, HuggingFace, ChromaDB, Ollama
- **Backend**: Python 3.10, FastAPI, Uvicorn
- **Architecture**: Decoupled, modular inference engines (`src/ai_models/`) 

## 🛠️ Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install deepface fer opencv-python mediapipe langchain-community chromadb
```

### 2. Run the Local LLM
Ensure Ollama is installed on your machine.
```bash
ollama pull llama3.2:3b
```

### 3. Build the Knowledge Base
Scrape and embed the health documents into your local VectorDB.
```bash
python -m src.scripts.build_knowledge_base
```

### 4. Start the Application
```bash
uvicorn src.api.main:app --reload
```

## 🤝 Contributing
Feel free to fork this project and submit pull requests. All computer vision models are designed to be easily extensible. Just add a new class in `src/ai_models/` and route it through the analyzer!

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.