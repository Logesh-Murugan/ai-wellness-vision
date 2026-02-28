# voice_interaction_page.py - Voice interaction interface
import streamlit as st
import time
from datetime import datetime
import random

def render():
    """Render the voice interaction page"""
    
    st.title("🎤 Voice Interaction")
    st.markdown("Interact with the AI assistant using voice commands")
    
    # Initialize session state for voice interactions
    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []
    
    # Voice configuration
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        language = st.selectbox(
            "Voice Language",
            ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Gujarati", "Marathi"],
            help="Select language for voice recognition and synthesis"
        )
    
    with col_config2:
        voice_type = st.selectbox(
            "Voice Type",
            ["Female", "Male", "Child"],
            help="Select preferred voice type for responses"
        )
    
    # Voice interaction area
    st.subheader("🎙️ Voice Commands")
    
    col_record, col_play = st.columns(2)
    
    with col_record:
        if st.button("🔴 Start Recording", type="primary", use_container_width=True):
            with st.spinner("Recording... Speak now!"):
                time.sleep(3)  # Simulate recording time
                
                # Mock transcription
                sample_transcriptions = [
                    "Hello, I have a headache and feel tired",
                    "What are some healthy food options?",
                    "I need advice about exercise",
                    "How can I improve my sleep?",
                    "I'm feeling stressed lately"
                ]
                
                transcription = random.choice(sample_transcriptions)
                
                st.success("✅ Recording complete!")
                st.info(f"**Transcription:** {transcription}")
                
                # Generate AI response
                with st.spinner("AI is processing your request..."):
                    time.sleep(2)
                    
                    # Mock AI responses
                    responses = {
                        "Hello, I have a headache and feel tired": "I understand you're experiencing a headache and fatigue. These symptoms can be caused by dehydration, lack of sleep, stress, or eye strain. Try drinking water, resting in a quiet dark room, and consider gentle neck stretches. If symptoms persist, please consult a healthcare provider.",
                        "What are some healthy food options?": "Great question! Healthy food options include leafy greens like spinach and kale, lean proteins such as chicken and fish, whole grains like quinoa and brown rice, fruits like berries and apples, nuts and seeds, and plenty of water. Focus on colorful, minimally processed foods.",
                        "I need advice about exercise": "Exercise is wonderful for your health! For beginners, I recommend starting with 20-30 minutes of walking daily, adding bodyweight exercises like squats and push-ups, and trying activities you enjoy like dancing or swimming. Always start slowly and gradually increase intensity.",
                        "How can I improve my sleep?": "Good sleep is crucial for health! Try maintaining a consistent bedtime, creating a relaxing pre-sleep routine, keeping your bedroom cool and dark, avoiding screens before bed, and limiting caffeine after 2 PM. Regular exercise and stress management also help improve sleep quality.",
                        "I'm feeling stressed lately": "I'm sorry you're feeling stressed. Stress management techniques include deep breathing exercises, regular physical activity, meditation, talking to friends or family, engaging in hobbies, and ensuring adequate rest. If stress becomes overwhelming, consider speaking with a mental health professional."
                    }
                    
                    ai_response = responses.get(transcription, "Thank you for your question. I'm here to help with your health and wellness concerns. Could you please provide more specific details so I can give you better guidance?")
                    
                    st.success("🤖 AI Response:")
                    st.write(ai_response)
                    
                    # Add to voice history
                    st.session_state.voice_history.append({
                        "timestamp": datetime.now(),
                        "user_message": transcription,
                        "ai_response": ai_response,
                        "language": language,
                        "voice_type": voice_type
                    })
    
    with col_play:
        if st.button("🔊 Play Last Response", use_container_width=True):
            st.info("🎵 Playing AI response... (Text-to-speech simulation)")
            with st.spinner("Converting text to speech..."):
                time.sleep(2)
            st.success("✅ Audio playback complete!")
    
    # Voice interaction history
    st.subheader("📜 Voice Interaction History")
    
    if st.session_state.voice_history:
        for i, conv in enumerate(reversed(st.session_state.voice_history[-5:]), 1):  # Show last 5
            with st.expander(f"Conversation {i} - {conv['timestamp'].strftime('%H:%M:%S')}"):
                st.markdown(f"**🎤 You said:** {conv['user_message']}")
                st.markdown(f"**🤖 AI responded:** {conv['ai_response']}")
                st.markdown(f"**Language:** {conv['language']} | **Voice:** {conv['voice_type']}")
    else:
        st.info("No voice interactions yet. Start by recording a voice message!")
    
    # Clear history button
    if st.session_state.voice_history:
        if st.button("🗑️ Clear Voice History"):
            st.session_state.voice_history = []
            st.rerun()
    
    # Voice commands help
    st.subheader("💡 Voice Command Examples")
    
    col_examples1, col_examples2 = st.columns(2)
    
    with col_examples1:
        st.markdown("""
        **Health Questions:**
        - "What should I eat for breakfast?"
        - "How much water should I drink daily?"
        - "What are symptoms of dehydration?"
        - "How can I reduce stress?"
        """)
    
    with col_examples2:
        st.markdown("""
        **Wellness Queries:**
        - "What exercises are good for beginners?"
        - "How can I improve my sleep?"
        - "What are healthy snack options?"
        - "How do I manage anxiety?"
        """)
    
    # Technical information
    st.subheader("🔧 Voice Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        **Speech Recognition:**
        - Multi-language support
        - Real-time transcription
        - Noise cancellation
        - High accuracy processing
        """)
    
    with feature_col2:
        st.markdown("""
        **Text-to-Speech:**
        - Natural voice synthesis
        - Multiple voice options
        - Adjustable speech rate
        - Clear pronunciation
        """)
    
    # Disclaimer
    st.markdown("---")
    st.warning("⚠️ **Privacy Note:** Voice recordings are processed securely and not stored permanently. All interactions are for informational purposes only and not a substitute for professional medical advice.")