# AI WellnessVision 🧠💚

An intelligent wellness platform that combines AI, computer vision, natural language processing, and speech recognition to provide personalized health insights and support.

## Features

- **🖼️ Image Recognition**: Computer vision for health-related image analysis
- **💬 NLP Engine**: Natural language processing with multilingual support (including Indic languages)
- **🎤 Speech Interface**: Voice interaction using Whisper and TTS
- **🔍 Explainable AI**: Transparent AI decisions with LIME and Grad-CAM
- **🌐 Web Interface**: User-friendly Streamlit application
- **🤖 Conversational AI**: Rasa-powered chatbot for wellness guidance

## Technology Stack

- **Deep Learning**: TensorFlow, Keras, PyTorch
- **Computer Vision**: OpenCV, Pillow
- **NLP**: Transformers, Rasa, Indic language libraries
- **Speech**: OpenAI Whisper, Coqui TTS
- **Explainability**: LIME, Grad-CAM
- **Frontend**: Streamlit
- **Data Science**: NumPy, Pandas, Scikit-learn

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Launch web interface**:
   ```bash
   streamlit run src/ui_app.py
   ```

## Project Structure

```
ai-wellnessvision/
├── src/
│   ├── config.py           # Configuration settings
│   ├── image_recognition.py # Computer vision module
│   ├── nlp_engine.py       # Natural language processing
│   ├── speech_engine.py    # Speech recognition and synthesis
│   ├── explainable_ai.py   # AI interpretability tools
│   └── ui_app.py          # Streamlit web interface
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development Status

🚧 **In Development** - Core modules are being implemented

## Contributing

This project is in active development. Contributions welcome!

## License

MIT License