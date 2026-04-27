import asyncio
from src.services.speech_service import speech_service
import os

async def test_pipeline():
    print("--- Testing Edge TTS (Text-to-Speech) ---")
    test_text = "Hello! This is a test of the completely free voice pipeline."
    print(f"Original Text: '{test_text}'")
    
    try:
        # 1. Test Synthesis
        mp3_bytes = await speech_service.synthesize(test_text, language="en")
        test_file = "test_audio.mp3"
        with open(test_file, "wb") as f:
            f.write(mp3_bytes)
        print(f"✅ Success! Generated '{test_file}' ({len(mp3_bytes)} bytes)")

        # 2. Test Transcription
        print("\n--- Testing Whisper STT (Speech-to-Text) ---")
        print("Loading local Whisper model (this takes a few seconds the first time)...")
        
        result = await speech_service.transcribe(mp3_bytes, language="en")
        
        print(f"✅ Success! Transcribed Text: '{result['text']}'")
        print(f"   Duration: {result['duration_seconds']} seconds")
        print(f"   Detected Language: {result['language']}")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print("\nCleaned up test file.")
            
    except Exception as e:
        print(f"❌ Pipeline Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
