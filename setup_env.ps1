# Setup Python Virtual Environment and Install Dependencies

# Step 1: Check if virtual environment exists, if not, create it
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists."
}

# Step 2: Activate virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Step 3: Upgrade pip, setuptools, wheel
Write-Host "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

# Step 4: Install dependencies from requirements.txt
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found. Creating one..."
    @"
tensorflow
keras
torch
torchvision
torchaudio
scikit-learn
numpy
pandas
matplotlib
opencv-python
pillow
rasa
transformers
sentencepiece==0.2.0
indic-nlp-library
indic-transliteration
openai-whisper
coqui-tts
soundfile
streamlit
lime
grad-cam
requests
tqdm
"@ | Out-File -Encoding utf8 requirements.txt
    Write-Host "Installing newly created dependencies..."
    pip install -r requirements.txt 
}

# Step 5: Done
Write-Host ""
Write-Host "Setup complete. To activate later, run:"
Write-Host ".\venv\Scripts\Activate.ps1"
