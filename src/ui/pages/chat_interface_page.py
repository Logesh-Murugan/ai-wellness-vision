# chat_interface_page.py - Chat interface with text and voice support
import streamlit as st
import time
from datetime import datetime
import random

# Optional imports with fallbacks
try:
    from src.ui.utils.session_manager import SessionManager
    from src.ui.utils.theme_config import create_custom_component
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Fallback functions
    def create_custom_component(content, comp_type="card"):
        return f'<div style="padding: 1rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.5rem 0;">{content}</div>'

def render():
    """Render the chat interface page"""
    
    # Initialize session manager
    if UTILS_AVAILABLE:
        session_manager = SessionManager()
    else:
        # Mock session manager
        class MockSessionManager:
            def add_conversation(self, *args, **kwargs): pass
            def get_session_id(self): return "demo_session"
            def get_user_info(self): return {"username": "demo_user"}
        session_manager = MockSessionManager()
    
    st.title("💬 AI Health Assistant")
    st.markdown("Chat with our AI assistant for health guidance and support")
    
    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your AI health assistant. How can I help you today?"}
        ]
    
    # Chat configuration
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        language = st.selectbox(
            "Language",
            ["en", "hi", "ta", "te", "bn", "gu", "mr"],
            format_func=lambda x: {
                "en": "🇺🇸 English",
                "hi": "🇮🇳 Hindi",
                "ta": "🇮🇳 Tamil",
                "te": "🇮🇳 Telugu", 
                "bn": "🇮🇳 Bengali",
                "gu": "🇮🇳 Gujarati",
                "mr": "🇮🇳 Marathi"
            }.get(x, x),
            help="Select your preferred language"
        )
    
    with col_config2:
        chat_mode = st.selectbox(
            "Chat Mode",
            ["general", "symptom_checker", "wellness", "mental_health"],
            format_func=lambda x: {
                "general": "💬 General Health",
                "symptom_checker": "🩺 Symptom Analysis", 
                "wellness": "🌟 Wellness Tips",
                "mental_health": "🧠 Mental Health"
            }.get(x, x),
            help="Choose the type of assistance you need"
        )
    
    # Display chat messages
    st.subheader("💭 Conversation")
    
    # Chat container with scrollable area
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                        <div style="background-color: #1f77b4; color: white; padding: 12px 16px; 
                                    border-radius: 18px 18px 4px 18px; max-width: 70%; word-wrap: break-word;">
                            <strong>You:</strong> {message["content"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                        <div style="background-color: #f0f2f6; color: #333; padding: 12px 16px; 
                                    border-radius: 18px 18px 18px 4px; max-width: 70%; word-wrap: break-word;
                                    border: 1px solid #e0e0e0;">
                            <strong>🤖 AI Assistant:</strong> {message["content"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # Chat input section
    st.markdown("---")
    st.subheader("✍️ Send a Message")
    
    # Create input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your message here:",
            placeholder="Ask me about your health concerns, symptoms, or wellness tips...",
            height=100,
            key="chat_input"
        )
        
        # Form buttons
        col_send, col_voice, col_clear = st.columns(3)
        
        with col_send:
            send_clicked = st.form_submit_button("📤 Send Message", type="primary", use_container_width=True)
        
        with col_voice:
            voice_clicked = st.form_submit_button("🎤 Voice Input", use_container_width=True)
        
        with col_clear:
            clear_clicked = st.form_submit_button("🗑️ Clear Chat", use_container_width=True)
    
    # Handle form submissions
    if send_clicked and user_input.strip():
        process_user_message(user_input.strip(), chat_mode, language, session_manager)
        st.rerun()
    elif send_clicked and not user_input.strip():
        st.warning("Please enter a message before sending.")
    
    if voice_clicked:
        st.info("🎤 Voice input feature coming soon! For now, please use text input.")
    
    if clear_clicked:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your AI health assistant. How can I help you today?"}
        ]
        st.success("Chat cleared!")
        st.rerun()
    
    # Quick suggestions
    st.markdown("---")
    st.subheader("💡 Quick Questions")
    
    suggestions = [
        "What are some healthy breakfast options?",
        "How can I improve my sleep quality?", 
        "What exercises are good for beginners?",
        "How do I manage stress effectively?",
        "What are signs of dehydration?",
        "How often should I have health checkups?"
    ]
    
    # Display suggestions in columns
    col1, col2, col3 = st.columns(3)
    
    for i, suggestion in enumerate(suggestions):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                process_user_message(suggestion, chat_mode, language, session_manager)
                st.rerun()
    
    # Chat statistics
    if len(st.session_state.chat_messages) > 1:
        st.markdown("---")
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            user_messages = len([m for m in st.session_state.chat_messages if m["role"] == "user"])
            st.metric("Your Messages", user_messages)
        
        with col_stats2:
            ai_messages = len([m for m in st.session_state.chat_messages if m["role"] == "assistant"]) - 1  # Exclude welcome message
            st.metric("AI Responses", ai_messages)
        
        with col_stats3:
            st.metric("Total Exchange", user_messages)
    
    # Disclaimer
    st.markdown("---")
    st.warning("⚠️ **Medical Disclaimer:** This AI assistant provides general health information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.")


def process_user_message(user_input, chat_mode, language, session_manager):
    """Process user message and generate AI response"""
    
    # Add user message to chat
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    
    # Generate AI response
    with st.spinner("AI is thinking..."):
        time.sleep(1)  # Simulate processing time
        ai_response = generate_ai_response(user_input, chat_mode, language)
    
    # Add AI response to chat
    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
    
    # Save to session manager
    session_manager.add_conversation(
        user_message=user_input,
        ai_response=ai_response,
        message_type="text",
        metadata={"language": language, "mode": chat_mode}
    )


def generate_ai_response(user_input, chat_mode, language):
    """Generate AI response based on user input and mode"""
    
    user_lower = user_input.lower()
    
    # Specific responses for common questions
    specific_responses = {
        "what are some healthy breakfast options?": "Great breakfast options include: oatmeal with fruits and nuts, Greek yogurt with berries, whole grain toast with avocado, smoothies with spinach and banana, or eggs with vegetables. These provide sustained energy and essential nutrients.",
        "how can i improve my sleep quality?": "To improve sleep quality: maintain a consistent sleep schedule, create a relaxing bedtime routine, keep your bedroom cool and dark, avoid screens before bed, limit caffeine after 2 PM, and try relaxation techniques like deep breathing.",
        "what exercises are good for beginners?": "Beginner-friendly exercises include: walking, swimming, bodyweight exercises (push-ups, squats), yoga, cycling, and light strength training. Start with 20-30 minutes, 3 times per week, and gradually increase intensity.",
        "how do i manage stress effectively?": "Effective stress management techniques: deep breathing exercises, regular physical activity, meditation or mindfulness, adequate sleep, time management, social support, and engaging in hobbies you enjoy.",
        "what are signs of dehydration?": "Signs of dehydration include: thirst, dry mouth, fatigue, dizziness, dark yellow urine, headache, and decreased urination. Drink water regularly throughout the day to prevent dehydration.",
        "how often should i have health checkups?": "Generally, healthy adults should have annual checkups. However, frequency may vary based on age, health conditions, and risk factors. Consult your healthcare provider for personalized recommendations."
    }
    
    # Check for specific responses first
    if user_lower in specific_responses:
        return specific_responses[user_lower]
    
    # Mode-based responses
    if chat_mode == "symptom_checker":
        if any(word in user_lower for word in ["headache", "pain", "hurt", "ache"]):
            return "I understand you're experiencing pain. For headaches, try: 1) Stay hydrated 2) Rest in a quiet, dark room 3) Apply a cold compress. If symptoms persist or worsen, please consult a healthcare professional."
        elif any(word in user_lower for word in ["fever", "temperature", "hot", "chills"]):
            return "Fever can indicate your body is fighting an infection. Monitor your temperature, stay hydrated, rest, and consider over-the-counter fever reducers if appropriate. Seek medical attention if fever is high or persistent."
        elif any(word in user_lower for word in ["cough", "cold", "sore throat"]):
            return "For cold symptoms: get plenty of rest, stay hydrated, use a humidifier, and consider warm salt water gargles for sore throat. If symptoms worsen or persist beyond a week, consult a healthcare provider."
        else:
            return "I'd be happy to help with your symptoms. Can you describe what you're experiencing? Remember, for serious or persistent symptoms, it's important to consult with a healthcare professional for proper evaluation."
    
    elif chat_mode == "wellness":
        if any(word in user_lower for word in ["diet", "eat", "food", "nutrition"]):
            return "For healthy nutrition, focus on: 1) Variety of colorful fruits and vegetables 2) Whole grains 3) Lean proteins 4) Healthy fats 5) Adequate hydration. Limit processed foods, excess sugar, and sodium."
        elif any(word in user_lower for word in ["exercise", "workout", "fitness"]):
            return "Regular exercise is crucial for health! Aim for 150 minutes of moderate aerobic activity weekly, plus strength training twice a week. Start slowly and gradually increase intensity. Find activities you enjoy to stay motivated."
        elif any(word in user_lower for word in ["weight", "lose", "gain"]):
            return "Weight management involves balancing calories in vs. calories out. Focus on sustainable lifestyle changes: regular physical activity, portion control, and nutritious food choices. Consult a nutritionist for personalized advice."
        else:
            return "I'm here to help with wellness questions! Whether it's about healthy eating, exercise, sleep, or lifestyle habits, feel free to ask. What aspect of wellness would you like to focus on?"
    
    elif chat_mode == "mental_health":
        if any(word in user_lower for word in ["stress", "anxious", "worried", "anxiety"]):
            return "Stress and anxiety are common experiences. Try these techniques: 1) Deep breathing exercises 2) Regular physical activity 3) Adequate sleep 4) Mindfulness or meditation 5) Talk to someone you trust. If feelings persist, consider speaking with a mental health professional."
        elif any(word in user_lower for word in ["sad", "depressed", "down", "depression"]):
            return "I'm sorry you're feeling this way. It's important to reach out for support. Consider: 1) Talking to friends/family 2) Regular exercise 3) Maintaining routines 4) Professional counseling if needed. Remember, seeking help is a sign of strength."
        elif any(word in user_lower for word in ["sleep", "insomnia", "tired"]):
            return "Sleep issues can affect mental health significantly. Try: consistent sleep schedule, relaxing bedtime routine, limiting screen time before bed, and creating a comfortable sleep environment. If problems persist, consult a healthcare provider."
        else:
            return "Mental health is just as important as physical health. I'm here to provide general support and information. For serious concerns, please reach out to a mental health professional or crisis helpline. You're not alone."
    
    else:  # general mode
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if any(greeting in user_lower for greeting in greetings):
            return "Hello! I'm your AI health assistant. I'm here to help with general health information, symptom guidance, nutrition advice, and mental health support. How can I assist you today?"
        
        health_keywords = ["health", "medical", "doctor", "medicine", "wellness"]
        if any(keyword in user_lower for keyword in health_keywords):
            return "I can help with general health information! I can assist with symptom checking, nutrition advice, mental health support, and general wellness tips. What specific area would you like to explore?"
        
        return "I'm here to help with your health and wellness questions! You can ask me about symptoms, nutrition, mental health, exercise, or general wellness. What would you like to know?"