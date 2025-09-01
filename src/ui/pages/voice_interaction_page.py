# voice_interaction_page.py - Voice interaction interface
import streamlit as st
import time
import asyncio
from datetime import datetime
from ui.utils.session_manager import SessionManager
from ui.utils.theme_config import create_custom_component

def render():
    """Render the voice interaction page"""
    
    st.title("🎤 Voice Interaction")
    st.markdown("Hands-free health consultations with voice input and audio responses")
    
    session_manager = SessionManager()
    
    # Voice settings
    render_voice_settings()
    
    # Main voice interface
    render_voice_interface(session_manager)
    
    # Voice conversation history
    render_voice_history(session_manager)
    
    # Voice controls
    render_voice_controls(session_manager)

def render_voice_settings():
    """Render voice configuration settings"""
    
    st.markdown("### 🔧 Voice Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        language = st.selectbox(
            "Language",
            options=["en", "hi", "ta", "te", "bn", "gu", "mr"],
            format_func=lambda x: {
                "en": "🇺🇸 English",
                "hi": "🇮🇳 Hindi", 
                "ta": "🇮🇳 Tamil",
                "te": "🇮🇳 Telugu",
                "bn": "🇮🇳 Bengali",
                "gu": "🇮🇳 Gujarati",
                "mr": "🇮🇳 Marathi"
            }[x],
            key="voice_language"
        )
    
    with col2:
        voice_type = st.selectbox(
            "Voice Type",
            options=["female", "male", "neutral"],
            format_func=lambda x: {
                "female": "👩 Female Voice",
                "male": "👨 Male Voice",
                "neutral": "🤖 Neutral Voice"
            }[x],
            key="voice_type"
        )
    
    with col3:
        auto_play = st.checkbox(
            "Auto-play Responses",
            value=True,
            help="Automatically play AI responses as audio",
            key="auto_play"
        )
    
    # Advanced voice settings
    with st.expander("🎛️ Advanced Voice Settings"):
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            speech_rate = st.slider(
                "Speech Rate",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1,
                help="Speed of speech synthesis",
                key="speech_rate"
            )
            
            volume = st.slider(
                "Volume",
                min_value=0.1,
                max_value=1.0,
                value=0.8,
                step=0.1,
                help="Audio output volume",
                key="volume"
            )
        
        with col_adv2:
            pitch = st.slider(
                "Pitch",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1,
                help="Voice pitch adjustment",
                key="pitch"
            )
            
            noise_reduction = st.checkbox(
                "Noise Reduction",
                value=True,
                help="Enable background noise reduction",
                key="noise_reduction"
            )

def render_voice_interface(session_manager):
    """Render main voice interaction interface"""
    
    st.markdown("### 🎙️ Voice Interaction")
    
    # Voice status indicator
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    
    if 'last_transcription' not in st.session_state:
        st.session_state.last_transcription = ""
    
    # Main voice interface
    col_main1, col_main2 = st.columns([2, 1])
    
    with col_main1:
        # Voice visualization area
        if st.session_state.recording:
            st.markdown(
                create_custom_component(
                    """
                    <div style="text-align: center; padding: 3rem;">
                        <div class="loading-spinner"></div>
                        <h3 style="color: #1f77b4; margin-top: 1rem;">🎤 Listening...</h3>
                        <p>Speak clearly into your microphone</p>
                        <div style="margin-top: 1rem;">
                            <div style="display: inline-block; width: 10px; height: 30px; background: #1f77b4; margin: 0 2px; animation: pulse 1s infinite;"></div>
                            <div style="display: inline-block; width: 10px; height: 40px; background: #1f77b4; margin: 0 2px; animation: pulse 1s infinite 0.1s;"></div>
                            <div style="display: inline-block; width: 10px; height: 35px; background: #1f77b4; margin: 0 2px; animation: pulse 1s infinite 0.2s;"></div>
                            <div style="display: inline-block; width: 10px; height: 45px; background: #1f77b4; margin: 0 2px; animation: pulse 1s infinite 0.3s;"></div>
                            <div style="display: inline-block; width: 10px; height: 30px; background: #1f77b4; margin: 0 2px; animation: pulse 1s infinite 0.4s;"></div>
                        </div>
                    </div>
                    <style>
                        @keyframes pulse {
                            0%, 100% { transform: scaleY(1); }
                            50% { transform: scaleY(1.5); }
                        }
                    </style>
                    """,
                    "card"
                ),
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                create_custom_component(
                    """
                    <div style="text-align: center; padding: 3rem;">
                        <div style="font-size: 4rem; margin-bottom: 1rem;">🎤</div>
                        <h3>Ready to Listen</h3>
                        <p style="color: #666;">Click the microphone button to start voice interaction</p>
                        <div style="margin-top: 1.5rem;">
                            <p><strong>💡 Voice Tips:</strong></p>
                            <ul style="text-align: left; max-width: 300px; margin: 0 auto;">
                                <li>Speak clearly and at normal pace</li>
                                <li>Minimize background noise</li>
                                <li>Wait for the beep before speaking</li>
                                <li>Click stop when finished</li>
                            </ul>
                        </div>
                    </div>
                    """,
                    "card"
                ),
                unsafe_allow_html=True
            )
    
    with col_main2:
        # Voice controls
        st.markdown("#### 🎛️ Voice Controls")
        
        if not st.session_state.recording:
            if st.button("🎤 Start Recording", type="primary", use_container_width=True):
                start_recording(session_manager)
        else:
            if st.button("⏹️ Stop Recording", type="secondary", use_container_width=True):
                stop_recording(session_manager)
        
        # Quick voice commands
        st.markdown("#### ⚡ Quick Commands")
        
        quick_commands = [
            ("🤒 Symptoms", "Tell me about my symptoms"),
            ("💊 Medication", "I have medication questions"),
            ("🏃‍♀️ Exercise", "Give me exercise advice"),
            ("😴 Sleep", "I have sleep problems")
        ]
        
        for label, command in quick_commands:
            if st.button(label, use_container_width=True):
                process_voice_command(command, session_manager)
        
        # Audio playback controls
        st.markdown("---")
        st.markdown("#### 🔊 Audio Controls")
        
        if st.button("🔊 Test Audio", use_container_width=True):
            test_audio_playback()
        
        if st.button("🔇 Mute/Unmute", use_container_width=True):
            toggle_audio()
    
    # Transcription display
    if st.session_state.last_transcription:
        st.markdown("### 📝 Last Transcription")
        st.markdown(
            create_custom_component(
                f"""
                <div style="padding: 1rem; background: #f8f9ff; border-left: 4px solid #1f77b4;">
                    <strong>You said:</strong><br>
                    "{st.session_state.last_transcription}"
                </div>
                """,
                "card"
            ),
            unsafe_allow_html=True
        )

def render_voice_history(session_manager):
    """Render voice conversation history"""
    
    st.markdown("### 🗣️ Voice Conversation History")
    
    # Get voice conversations
    conversations = session_manager.get_conversation_history()
    voice_conversations = [c for c in conversations if c.get('message_type') == 'voice']
    
    if not voice_conversations:
        st.info("No voice conversations yet. Start by recording a voice message!")
        return
    
    # Display voice conversations
    for i, conv in enumerate(reversed(voice_conversations[-5:])):  # Show last 5
        with st.expander(f"🎤 Voice Conversation {len(voice_conversations) - i}", expanded=i==0):
            
            col_conv1, col_conv2 = st.columns([3, 1])
            
            with col_conv1:
                # User message
                st.markdown(f"**👤 You said:** {conv['user_message']}")
                
                # AI response
                st.markdown(f"**🤖 AI Response:** {conv['ai_response']}")
                
                # Metadata
                metadata = conv.get('metadata', {})
                if metadata:
                    st.caption(f"Language: {metadata.get('language', 'Unknown')} | "
                             f"Confidence: {metadata.get('confidence', 0):.1%} | "
                             f"Processing: {metadata.get('processing_time', 0):.2f}s")
            
            with col_conv2:
                timestamp = conv['timestamp'].strftime("%H:%M:%S")
                st.caption(f"🕒 {timestamp}")
                
                # Audio playback buttons (mock)
                if st.button(f"🔊 Play Original", key=f"play_orig_{i}"):
                    st.info("🔧 Would play original audio recording")
                
                if st.button(f"🎵 Play Response", key=f"play_resp_{i}"):
                    st.info("🔧 Would play AI response audio")

def render_voice_controls(session_manager):
    """Render voice control buttons"""
    
    st.markdown("---")
    st.markdown("### 🎛️ Voice Session Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Voice Analytics", use_container_width=True):
            show_voice_analytics(session_manager)
    
    with col2:
        if st.button("🎵 Audio Settings", use_container_width=True):
            show_audio_settings()
    
    with col3:
        if st.button("📤 Export Audio", use_container_width=True):
            export_voice_data(session_manager)
    
    with col4:
        if st.button("🔄 Clear Voice History", use_container_width=True):
            clear_voice_history(session_manager)

def start_recording(session_manager):
    """Start voice recording"""
    
    st.session_state.recording = True
    
    # Mock recording process
    with st.spinner("🎤 Starting recording..."):
        time.sleep(1)
    
    st.success("🎤 Recording started! Speak now...")
    st.rerun()

def stop_recording(session_manager):
    """Stop voice recording and process"""
    
    st.session_state.recording = False
    
    with st.spinner("🔄 Processing audio..."):
        time.sleep(2)
        
        # Mock transcription
        mock_transcriptions = [
            "I have been feeling tired and have a headache for the past few days.",
            "Can you help me understand what might be causing my back pain?",
            "I'm looking for advice on improving my sleep quality.",
            "What are some healthy meal options for someone with diabetes?",
            "I've been feeling anxious lately and need some guidance."
        ]
        
        import random
        transcription = random.choice(mock_transcriptions)
        st.session_state.last_transcription = transcription
        
        # Process the transcribed message
        process_voice_command(transcription, session_manager)
    
    st.success("✅ Recording processed!")
    st.rerun()

def process_voice_command(command, session_manager):
    """Process voice command and generate response"""
    
    try:
        with st.spinner("🤖 Generating AI response..."):
            # Import services
            from api.gateway import ServiceOrchestrator, ChatRequest
            import asyncio
            
            # Create chat request
            chat_request = ChatRequest(
                message=command,
                session_id=session_manager.get_session_id(),
                user_id=session_manager.get_user_info().get('username'),
                language=st.session_state.get('voice_language', 'en'),
                message_type='voice'
            )
            
            # Process with orchestrator
            orchestrator = ServiceOrchestrator()
            
            async def run_chat():
                return await orchestrator.process_chat_message(chat_request)
            
            result = asyncio.run(run_chat())
            
            if result['status'] == 'success':
                ai_response = result['response']
                
                # Add to conversation history
                session_manager.add_conversation(
                    command,
                    ai_response,
                    'voice',
                    {
                        'language': st.session_state.get('voice_language', 'en'),
                        'voice_type': st.session_state.get('voice_type', 'female'),
                        'sentiment': result.get('sentiment'),
                        'confidence': result.get('confidence'),
                        'processing_time': result.get('processing_time')
                    }
                )
                
                # Auto-play response if enabled
                if st.session_state.get('auto_play', True):
                    with st.spinner("🎵 Playing AI response..."):
                        time.sleep(2)  # Mock audio playback
                    st.success("🎵 Response played!")
                
                st.success("✅ Voice interaction completed!")
                
            else:
                st.error(f"❌ Failed to process voice command: {result.get('message', 'Unknown error')}")
                
    except Exception as e:
        st.error(f"Error processing voice command: {str(e)}")

def test_audio_playback():
    """Test audio playback functionality"""
    
    with st.spinner("🔊 Testing audio playback..."):
        time.sleep(1)
    
    st.success("🔊 Audio test completed! If you can't hear anything, check your device volume and audio settings.")

def toggle_audio():
    """Toggle audio mute/unmute"""
    
    if 'audio_muted' not in st.session_state:
        st.session_state.audio_muted = False
    
    st.session_state.audio_muted = not st.session_state.audio_muted
    
    if st.session_state.audio_muted:
        st.info("🔇 Audio muted")
    else:
        st.success("🔊 Audio unmuted")

def show_voice_analytics(session_manager):
    """Show voice interaction analytics"""
    
    conversations = session_manager.get_conversation_history()
    voice_conversations = [c for c in conversations if c.get('message_type') == 'voice']
    
    if not voice_conversations:
        st.info("No voice data available for analytics.")
        return
    
    # Voice analytics
    total_voice = len(voice_conversations)
    avg_length = sum(len(c['user_message']) for c in voice_conversations) / total_voice if total_voice > 0 else 0
    
    # Languages used
    languages = {}
    for conv in voice_conversations:
        lang = conv.get('metadata', {}).get('language', 'unknown')
        languages[lang] = languages.get(lang, 0) + 1
    
    st.markdown(
        create_custom_component(
            f"""
            <h4>📊 Voice Interaction Analytics</h4>
            <p><strong>Total Voice Interactions:</strong> {total_voice}</p>
            <p><strong>Average Message Length:</strong> {avg_length:.0f} characters</p>
            <p><strong>Languages Used:</strong> {', '.join(languages.keys())}</p>
            <p><strong>Most Used Language:</strong> {max(languages.keys(), key=languages.get) if languages else 'None'}</p>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )

def show_audio_settings():
    """Show detailed audio settings"""
    
    st.markdown(
        create_custom_component(
            """
            <h4>🎵 Audio Settings Guide</h4>
            
            <h5>🎤 Microphone Settings:</h5>
            <ul>
                <li>Ensure microphone permissions are granted</li>
                <li>Use a quiet environment for best results</li>
                <li>Speak 6-12 inches from the microphone</li>
                <li>Test microphone before important conversations</li>
            </ul>
            
            <h5>🔊 Speaker Settings:</h5>
            <ul>
                <li>Adjust system volume to comfortable level</li>
                <li>Use headphones to prevent audio feedback</li>
                <li>Check audio output device selection</li>
                <li>Enable auto-play for seamless experience</li>
            </ul>
            
            <h5>🌐 Language Support:</h5>
            <ul>
                <li>Voice recognition supports multiple languages</li>
                <li>Switch languages in voice settings</li>
                <li>Pronunciation may vary by accent</li>
                <li>Use clear speech for better accuracy</li>
            </ul>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )

def export_voice_data(session_manager):
    """Export voice interaction data"""
    
    conversations = session_manager.get_conversation_history()
    voice_conversations = [c for c in conversations if c.get('message_type') == 'voice']
    
    if not voice_conversations:
        st.info("No voice data to export.")
        return
    
    # Prepare export data
    export_data = {
        'export_timestamp': datetime.now().isoformat(),
        'total_voice_interactions': len(voice_conversations),
        'voice_conversations': []
    }
    
    for conv in voice_conversations:
        export_data['voice_conversations'].append({
            'timestamp': conv['timestamp'].isoformat(),
            'user_message': conv['user_message'],
            'ai_response': conv['ai_response'],
            'metadata': conv.get('metadata', {})
        })
    
    # Create downloadable file
    import json
    export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📄 Download Voice Data (JSON)",
        data=export_json,
        file_name=f"voice_interactions_{int(time.time())}.json",
        mime="application/json"
    )

def clear_voice_history(session_manager):
    """Clear voice conversation history"""
    
    if st.button("⚠️ Confirm Clear Voice History"):
        # Remove only voice conversations
        all_conversations = session_manager.get_conversation_history()
        text_conversations = [c for c in all_conversations if c.get('message_type') != 'voice']
        
        # Update session state
        st.session_state.conversation_history = text_conversations
        
        st.success("🗑️ Voice history cleared!")
        st.rerun()
    else:
        st.warning("Click the button above to confirm clearing voice history.")