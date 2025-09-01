# chat_interface_page.py - Chat interface with text and voice support
import streamlit as st
import time
import asyncio
from datetime import datetime
from ui.utils.session_manager import SessionManager
from ui.utils.theme_config import create_custom_component

def render():
    """Render the chat interface page"""
    
    st.title("💬 AI Health Assistant")
    st.markdown("Chat with our AI assistant for health guidance and support")
    
    session_manager = SessionManager()
    
    # Chat configuration
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
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
            help="Select your preferred language"
        )
    
    with col_config2:
        chat_mode = st.selectbox(
            "Chat Mode",
            options=["text", "voice", "mixed"],
            format_func=lambda x: {
                "text": "📝 Text Only",
                "voice": "🎤 Voice Only",
                "mixed": "🔄 Text & Voice"
            }[x],
            help="Choose your interaction mode"
        )
    
    # Chat container
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        display_chat_history(session_manager)
    
    # Input area
    st.markdown("---")
    
    if chat_mode in ["text", "mixed"]:
        render_text_input(session_manager, language)
    
    if chat_mode in ["voice", "mixed"]:
        render_voice_input(session_manager, language)
    
    # Quick action buttons
    render_quick_actions(session_manager, language)
    
    # Chat controls
    render_chat_controls(session_manager)

def display_chat_history(session_manager):
    """Display chat conversation history"""
    
    conversations = session_manager.get_conversation_history()
    
    if not conversations:
        # Welcome message
        st.markdown(
            create_custom_component(
                """
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
                    <h3>Hello! I'm your AI Health Assistant</h3>
                    <p style="color: #666;">
                        I'm here to help you with health questions, symptom analysis, 
                        and wellness guidance. How can I assist you today?
                    </p>
                    <div style="margin-top: 1.5rem;">
                        <strong>💡 You can ask me about:</strong>
                        <ul style="text-align: left; max-width: 400px; margin: 1rem auto;">
                            <li>Symptoms and health concerns</li>
                            <li>Wellness tips and advice</li>
                            <li>Medication information</li>
                            <li>Healthy lifestyle recommendations</li>
                            <li>Mental health support</li>
                        </ul>
                    </div>
                </div>
                """,
                "card"
            ),
            unsafe_allow_html=True
        )
        return
    
    # Display conversations
    for conversation in conversations:
        timestamp = conversation['timestamp']
        user_message = conversation['user_message']
        ai_response = conversation['ai_response']
        message_type = conversation.get('message_type', 'text')
        
        # Format timestamp
        time_str = timestamp.strftime("%H:%M")
        
        # User message
        st.markdown(
            f"""
            <div class="user-message">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="margin-right: 0.5rem;">
                        {'🎤' if message_type == 'voice' else '👤'}
                    </span>
                    <small style="opacity: 0.8;">{time_str}</small>
                </div>
                {user_message}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # AI response
        st.markdown(
            f"""
            <div class="ai-message">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="margin-right: 0.5rem;">🤖</span>
                    <small style="opacity: 0.8;">{time_str}</small>
                </div>
                {ai_response}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)

def render_text_input(session_manager, language):
    """Render text input interface"""
    
    st.markdown("### 📝 Type your message")
    
    # Text input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your message:",
            placeholder="Type your health question or concern here...",
            height=100,
            label_visibility="collapsed"
        )
        
        col_send, col_clear = st.columns([3, 1])
        
        with col_send:
            send_clicked = st.form_submit_button(
                "💬 Send Message",
                type="primary",
                use_container_width=True
            )
        
        with col_clear:
            clear_clicked = st.form_submit_button(
                "🗑️ Clear",
                use_container_width=True
            )
    
    if send_clicked and user_input.strip():
        process_text_message(user_input.strip(), session_manager, language)
        st.rerun()
    
    if clear_clicked:
        st.rerun()

def render_voice_input(session_manager, language):
    """Render voice input interface"""
    
    st.markdown("### 🎤 Voice Input")
    
    col_voice1, col_voice2 = st.columns(2)
    
    with col_voice1:
        # Audio recorder (placeholder - would need streamlit-audio-recorder)
        st.info("🔧 Voice recording feature would be implemented here using streamlit-audio-recorder or similar component")
        
        # Mock voice input button
        if st.button("🎤 Start Recording", use_container_width=True):
            with st.spinner("Recording... (Mock)"):
                time.sleep(2)
            
            # Mock transcription
            mock_transcription = "I have been feeling tired lately and have a headache."
            st.success(f"Transcribed: '{mock_transcription}'")
            
            # Process the mock message
            process_text_message(mock_transcription, session_manager, language, message_type="voice")
            st.rerun()
    
    with col_voice2:
        # Voice settings
        with st.expander("🔧 Voice Settings"):
            voice_speed = st.slider("Speech Speed", 0.5, 2.0, 1.0, 0.1)
            voice_pitch = st.slider("Voice Pitch", 0.5, 2.0, 1.0, 0.1)
            enable_tts = st.checkbox("Enable Text-to-Speech", value=True)

def render_quick_actions(session_manager, language):
    """Render quick action buttons"""
    
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    quick_actions = [
        ("🤒 Symptoms", "I'm experiencing some symptoms and need guidance"),
        ("💊 Medications", "I have questions about medications"),
        ("🏃‍♀️ Fitness", "I want advice on fitness and exercise"),
        ("🧘‍♂️ Mental Health", "I need support with mental health and stress")
    ]
    
    for i, (label, message) in enumerate(quick_actions):
        col = [col1, col2, col3, col4][i]
        with col:
            if st.button(label, use_container_width=True):
                process_text_message(message, session_manager, language)
                st.rerun()

def render_chat_controls(session_manager):
    """Render chat control buttons"""
    
    st.markdown("---")
    st.markdown("### 🔧 Chat Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Chat Summary", use_container_width=True):
            generate_chat_summary(session_manager)
    
    with col2:
        if st.button("📤 Export Chat", use_container_width=True):
            export_chat_history(session_manager)
    
    with col3:
        if st.button("🔄 New Conversation", use_container_width=True):
            if st.session_state.get('confirm_new_chat', False):
                session_manager.clear_history("conversations")
                st.session_state.confirm_new_chat = False
                st.success("Started new conversation!")
                st.rerun()
            else:
                st.session_state.confirm_new_chat = True
                st.warning("Click again to confirm starting a new conversation")
    
    with col4:
        if st.button("❓ Help", use_container_width=True):
            show_chat_help()

def process_text_message(user_input, session_manager, language, message_type="text"):
    """Process user text message and get AI response"""
    
    try:
        # Show typing indicator
        with st.spinner("🤖 AI is thinking..."):
            # Import services
            from api.gateway import ServiceOrchestrator, ChatRequest
            import asyncio
            
            # Create chat request
            chat_request = ChatRequest(
                message=user_input,
                session_id=session_manager.get_session_id(),
                user_id=session_manager.get_user_info().get('username'),
                language=language,
                message_type=message_type
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
                    user_input,
                    ai_response,
                    message_type,
                    {
                        'language': language,
                        'sentiment': result.get('sentiment'),
                        'confidence': result.get('confidence'),
                        'processing_time': result.get('processing_time')
                    }
                )
                
                # Show success message briefly
                st.success("✅ Message sent!")
                
            else:
                st.error(f"❌ Failed to get response: {result.get('message', 'Unknown error')}")
                
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")

def generate_chat_summary(session_manager):
    """Generate and display chat summary"""
    
    conversations = session_manager.get_conversation_history()
    
    if not conversations:
        st.info("No conversations to summarize yet.")
        return
    
    # Mock summary generation
    with st.spinner("Generating chat summary..."):
        time.sleep(1)
    
    summary_data = {
        'total_messages': len(conversations),
        'conversation_duration': 'This session',
        'main_topics': ['Health symptoms', 'Wellness advice', 'General questions'],
        'sentiment_analysis': 'Mostly positive and seeking help',
        'key_recommendations': [
            'Consult healthcare provider for persistent symptoms',
            'Maintain regular exercise routine',
            'Consider stress management techniques'
        ]
    }
    
    st.markdown(
        create_custom_component(
            f"""
            <h4>📊 Conversation Summary</h4>
            <p><strong>Total Messages:</strong> {summary_data['total_messages']}</p>
            <p><strong>Duration:</strong> {summary_data['conversation_duration']}</p>
            <p><strong>Main Topics:</strong> {', '.join(summary_data['main_topics'])}</p>
            <p><strong>Overall Sentiment:</strong> {summary_data['sentiment_analysis']}</p>
            
            <h5>🎯 Key Recommendations:</h5>
            <ul>
                {''.join([f'<li>{rec}</li>' for rec in summary_data['key_recommendations']])}
            </ul>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )

def export_chat_history(session_manager):
    """Export chat history for download"""
    
    conversations = session_manager.get_conversation_history()
    
    if not conversations:
        st.info("No conversations to export yet.")
        return
    
    # Prepare export data
    export_data = {
        'export_timestamp': datetime.now().isoformat(),
        'user_info': session_manager.get_user_info(),
        'total_conversations': len(conversations),
        'conversations': []
    }
    
    for conv in conversations:
        export_data['conversations'].append({
            'timestamp': conv['timestamp'].isoformat(),
            'user_message': conv['user_message'],
            'ai_response': conv['ai_response'],
            'message_type': conv.get('message_type', 'text'),
            'metadata': conv.get('metadata', {})
        })
    
    # Create downloadable file
    import json
    export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📄 Download Chat History (JSON)",
        data=export_json,
        file_name=f"chat_history_{int(time.time())}.json",
        mime="application/json"
    )
    
    # Also offer text format
    text_export = f"AI WellnessVision Chat History\n"
    text_export += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    text_export += f"Total Conversations: {len(conversations)}\n"
    text_export += "=" * 50 + "\n\n"
    
    for conv in conversations:
        text_export += f"[{conv['timestamp'].strftime('%H:%M:%S')}] User: {conv['user_message']}\n"
        text_export += f"[{conv['timestamp'].strftime('%H:%M:%S')}] AI: {conv['ai_response']}\n\n"
    
    st.download_button(
        label="📝 Download Chat History (Text)",
        data=text_export,
        file_name=f"chat_history_{int(time.time())}.txt",
        mime="text/plain"
    )

def show_chat_help():
    """Show chat help information"""
    
    st.markdown(
        create_custom_component(
            """
            <h4>❓ Chat Help & Tips</h4>
            
            <h5>🗣️ How to Chat Effectively:</h5>
            <ul>
                <li><strong>Be specific:</strong> Describe your symptoms or concerns in detail</li>
                <li><strong>Provide context:</strong> Mention duration, severity, and related factors</li>
                <li><strong>Ask follow-up questions:</strong> Don't hesitate to ask for clarification</li>
                <li><strong>Use natural language:</strong> Speak as you would to a healthcare provider</li>
            </ul>
            
            <h5>🎤 Voice Features:</h5>
            <ul>
                <li>Click the microphone button to start voice recording</li>
                <li>Speak clearly and at a normal pace</li>
                <li>Voice messages are automatically transcribed</li>
                <li>Enable text-to-speech to hear AI responses</li>
            </ul>
            
            <h5>⚡ Quick Actions:</h5>
            <ul>
                <li>Use quick action buttons for common topics</li>
                <li>Export your chat history for your records</li>
                <li>Generate summaries to review key points</li>
                <li>Start new conversations when needed</li>
            </ul>
            
            <h5>⚠️ Important Reminders:</h5>
            <ul>
                <li>This AI assistant provides general information only</li>
                <li>Always consult healthcare professionals for medical advice</li>
                <li>In emergencies, contact emergency services immediately</li>
                <li>Your privacy and data security are protected</li>
            </ul>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )