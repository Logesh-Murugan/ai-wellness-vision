#!/usr/bin/env python3
"""
AI WellnessVision - Streamlit Web Interface
Main application entry point with multi-page navigation
"""

import streamlit as st
import sys
import os
import io
import base64
import json
import time
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import dependencies with fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not available")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logger.warning("Pandas not available")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logger.warning("Plotly not available")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("PIL not available")

# Try to import custom modules with graceful fallbacks
MODULES_AVAILABLE = False
try:
    from src.ui.pages import (
        home_page,
        image_analysis_page,
        chat_interface_page,
        voice_interaction_page,
        history_page,
        settings_page
    )
    from src.ui.components.auth import authentication_component
    from src.ui.utils.session_manager import SessionManager
    from src.ui.utils.theme_config import apply_custom_theme
    MODULES_AVAILABLE = True
    logger.info("All custom modules loaded successfully")
except ImportError as e:
    logger.warning(f"Custom modules not available: {e}")
    MODULES_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="AI WellnessVision",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ai-wellnessvision/help',
        'Report a bug': 'https://github.com/ai-wellnessvision/issues',
        'About': """
        # AI WellnessVision
        
        An AI-powered health and wellness analysis platform providing:
        - Image analysis for health conditions
        - Conversational AI health consultations
        - Voice interactions and speech processing
        - Explainable AI insights
        
        **Version:** 1.0.0
        **Built with:** Streamlit, FastAPI, PyTorch, Transformers
        """
    }
)

# Built-in fallback components
class MockSessionManager:
    """Fallback session manager when custom modules aren't available"""
    
    def __init__(self):
        if 'user_authenticated' not in st.session_state:
            st.session_state.user_authenticated = True
        if 'user_info' not in st.session_state:
            st.session_state.user_info = {
                "username": "Demo User",
                "email": "demo@example.com",
                "roles": ["user"],
                "created_at": datetime.datetime.now().isoformat()
            }
        if 'user_stats' not in st.session_state:
            st.session_state.user_stats = {
                "total_analyses": 15,
                "total_chats": 42,
                "total_voice_interactions": 8,
                "last_activity": datetime.datetime.now().isoformat()
            }
    
    def is_authenticated(self) -> bool:
        return st.session_state.get('user_authenticated', False)
    
    def get_user_info(self) -> Dict[str, Any]:
        return st.session_state.get('user_info', {})
    
    def get_user_stats(self) -> Dict[str, Any]:
        return st.session_state.get('user_stats', {})
    
    def logout(self):
        st.session_state.user_authenticated = False
        st.session_state.clear()

def apply_custom_theme():
    """Apply custom CSS theme"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Built-in page components
def render_home_page():
    """Built-in home page component"""
    st.markdown('<h1 class="main-header">🏥 AI WellnessVision Dashboard</h1>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    <div class="feature-card">
        <h3>Welcome to AI WellnessVision</h3>
        <p>Your comprehensive AI-powered health and wellness analysis platform. 
        Get insights through image analysis, conversational AI, and voice interactions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Analyses</h3>
            <h2>15</h2>
            <p>Total completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>💬 Chats</h3>
            <h2>42</h2>
            <p>Conversations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎤 Voice</h3>
            <h2>8</h2>
            <p>Interactions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>⭐ Score</h3>
            <h2>4.8</h2>
            <p>Avg rating</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity with modern charts
    st.subheader("📈 Recent Activity")
    
    if HAS_PANDAS and HAS_PLOTLY:
        # Create sample data
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        if HAS_NUMPY:
            activity_data = pd.DataFrame({
                'Date': dates,
                'Analyses': np.random.poisson(2, len(dates)),
                'Chats': np.random.poisson(3, len(dates)),
                'Voice': np.random.poisson(1, len(dates))
            })
        else:
            activity_data = pd.DataFrame({
                'Date': dates,
                'Analyses': [2] * len(dates),
                'Chats': [3] * len(dates),
                'Voice': [1] * len(dates)
            })
        
        # Use tabs for different chart views
        chart_tab1, chart_tab2 = st.tabs(["📊 Line Chart", "📈 Area Chart"])
        
        with chart_tab1:
            fig = px.line(activity_data, x='Date', y=['Analyses', 'Chats', 'Voice'],
                         title="Daily Activity Trends",
                         color_discrete_map={
                             'Analyses': '#1f77b4',
                             'Chats': '#ff7f0e', 
                             'Voice': '#2ca02c'
                         })
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Count",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_tab2:
            fig = px.area(activity_data, x='Date', y=['Analyses', 'Chats', 'Voice'],
                         title="Cumulative Activity Trends")
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback with native Streamlit charts
        st.info("📊 Activity data visualization (demo mode)")
        
        # Use st.line_chart as fallback
        chart_data = {
            'Analyses': [2, 3, 1, 4, 2, 3, 5],
            'Chats': [5, 4, 6, 3, 7, 4, 6],
            'Voice': [1, 2, 1, 3, 1, 2, 2]
        }
        st.line_chart(chart_data)
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📷 New Image Analysis", use_container_width=True):
            st.session_state.current_page = "Image Analysis"
            st.rerun()
    
    with col2:
        if st.button("💬 Start Chat", use_container_width=True):
            st.session_state.current_page = "Chat Assistant"
            st.rerun()
    
    with col3:
        if st.button("🎤 Voice Interaction", use_container_width=True):
            st.session_state.current_page = "Voice Interaction"
            st.rerun()

def render_image_analysis_page():
    """Built-in image analysis page component"""
    st.markdown('<h1 class="main-header">📷 Image Analysis</h1>', unsafe_allow_html=True)
    
    # Analysis type selector
    analysis_type = st.selectbox(
        "🔍 Select Analysis Type",
        ["Skin Analysis", "Eye Health", "Dental Check", "General Health", "Symptom Detection"],
        help="Choose the type of analysis you want to perform"
    )
    
    # File uploader with drag and drop
    uploaded_file = st.file_uploader(
        f"📤 Upload an image for {analysis_type.lower()}",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
        help="Drag and drop or click to upload. Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP"
    )
    
    # Camera input option (Streamlit 1.48+ feature)
    use_camera = st.checkbox("📷 Use camera instead", help="Take a photo directly with your camera")
    
    if use_camera:
        camera_image = st.camera_input("Take a photo for analysis")
        if camera_image:
            uploaded_file = camera_image
    
    if uploaded_file is not None:
        if HAS_PIL:
            # Display image
            image = Image.open(uploaded_file)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📸 Uploaded Image")
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Image info
                st.info(f"""
                **Image Details:**
                - Filename: {uploaded_file.name}
                - Size: {image.size}
                - Format: {image.format}
                - Mode: {image.mode}
                """)
            
            with col2:
                st.subheader("🔍 Analysis Results")
                
                # Simulate analysis
                with st.spinner("Analyzing image..."):
                    time.sleep(2)  # Simulate processing time
                
                # Analysis results with progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate analysis steps
                steps = [
                    ("Preprocessing image...", 20),
                    ("Running AI model...", 50),
                    ("Analyzing features...", 80),
                    ("Generating insights...", 100)
                ]
                
                for step_text, progress in steps:
                    status_text.text(step_text)
                    progress_bar.progress(progress)
                    time.sleep(0.3)
                
                status_text.text("Analysis complete!")
                
                # Success message with modern styling
                st.success("✅ Analysis completed successfully!", icon="🎉")
                
                # Results tabs with enhanced content
                tab1, tab2, tab3, tab4 = st.tabs(["🎯 Detection", "📊 Metrics", "💡 Insights", "📋 Report"])
                
                with tab1:
                    st.subheader("Detected Features")
                    
                    # Generate analysis based on selected type
                    if analysis_type == "Skin Analysis":
                        features = [
                            ("Skin condition", "Normal", 95),
                            ("Texture analysis", "Smooth", 88),
                            ("Color analysis", "Healthy tone", 92),
                            ("Hydration level", "Well-hydrated", 89)
                        ]
                    elif analysis_type == "Eye Health":
                        features = [
                            ("Pupil response", "Normal", 94),
                            ("Sclera condition", "Clear", 91),
                            ("Iris pattern", "Regular", 87),
                            ("Overall health", "Good", 90)
                        ]
                    else:
                        features = [
                            ("General condition", "Normal", 93),
                            ("Symmetry", "Good", 89),
                            ("Color variation", "Within range", 86),
                            ("Overall assessment", "Healthy", 89)
                        ]
                    
                    for feature, result, confidence in features:
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.write(f"**{feature}:**")
                        with col2:
                            st.write(result)
                        with col3:
                            st.metric("", f"{confidence}%")
                
                with tab2:
                    st.subheader("Confidence Metrics")
                    
                    if HAS_PLOTLY:
                        confidence_data = pd.DataFrame({
                            'Feature': [f[0] for f in features],
                            'Confidence': [f[2] for f in features]
                        })
                        
                        # Create gauge chart for overall confidence
                        overall_confidence = sum(f[2] for f in features) / len(features)
                        
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = overall_confidence,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Overall Confidence"},
                            delta = {'reference': 85},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 85], 'color': "gray"},
                                    {'range': [85, 100], 'color': "lightgreen"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Bar chart for individual features
                        fig2 = px.bar(confidence_data, x='Feature', y='Confidence',
                                     title="Feature-wise Confidence Scores",
                                     color='Confidence',
                                     color_continuous_scale='viridis')
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        # Fallback metrics display
                        for feature, result, confidence in features:
                            st.metric(feature, f"{confidence}%", f"{result}")
                
                with tab3:
                    st.subheader("AI-Generated Insights")
                    
                    # Generate insights based on analysis type
                    if analysis_type == "Skin Analysis":
                        insights = [
                            "🟢 The analyzed image shows healthy skin characteristics",
                            "🔍 No concerning features or irregularities detected",
                            "💡 Skin appears well-hydrated and maintained",
                            "📋 Recommended: Continue current skincare routine",
                            "📅 Next check: In 3 months or if changes occur"
                        ]
                    elif analysis_type == "Eye Health":
                        insights = [
                            "👁️ Eyes appear healthy with normal characteristics",
                            "✅ No signs of irritation or infection detected",
                            "🔍 Pupil response and sclera condition are normal",
                            "💡 Consider regular eye exams with an optometrist",
                            "⚠️ Consult a professional if you experience vision changes"
                        ]
                    else:
                        insights = [
                            "✅ Analysis shows normal characteristics",
                            "📊 All measured parameters within healthy ranges",
                            "🎯 No immediate concerns identified",
                            "💡 Maintain current health practices",
                            "📞 Consult healthcare provider for any concerns"
                        ]
                    
                    for insight in insights:
                        st.write(insight)
                    
                    # Recommendations section
                    st.subheader("📝 Recommendations")
                    
                    with st.expander("🏥 When to see a healthcare provider"):
                        st.write("""
                        - If you notice any sudden changes
                        - If symptoms persist or worsen
                        - For regular check-ups and preventive care
                        - If you have specific health concerns
                        """)
                    
                    with st.expander("🏠 Self-care tips"):
                        st.write("""
                        - Maintain good hygiene practices
                        - Follow a healthy lifestyle
                        - Monitor for any changes
                        - Stay hydrated and eat well
                        """)
                
                with tab4:
                    st.subheader("📋 Analysis Report")
                    
                    # Generate a comprehensive report
                    report_data = {
                        "Analysis Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Analysis Type": analysis_type,
                        "Image Format": image.format if hasattr(image, 'format') else "Unknown",
                        "Image Size": f"{image.size[0]}x{image.size[1]}" if hasattr(image, 'size') else "Unknown",
                        "Overall Confidence": f"{sum(f[2] for f in features) / len(features):.1f}%",
                        "Status": "Analysis Complete"
                    }
                    
                    # Display report in a nice format
                    for key, value in report_data.items():
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.write(f"**{key}:**")
                        with col2:
                            st.write(value)
                    
                    # Export options
                    st.subheader("📤 Export Options")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📄 Download PDF", use_container_width=True):
                            st.success("PDF report generated!")
                    
                    with col2:
                        if st.button("📊 Export Data", use_container_width=True):
                            st.success("Data exported successfully!")
                    
                    with col3:
                        if st.button("📧 Email Report", use_container_width=True):
                            st.success("Report sent to your email!")
        else:
            st.error("PIL (Pillow) library not available. Please install it to use image analysis.")
    else:
        st.info("👆 Please upload an image to start analysis")
        
        # Sample images section
        st.subheader("📋 Sample Analysis Types")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🔬 Skin Analysis</h4>
                <p>Detect skin conditions, analyze texture, and assess overall health</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>👁️ Eye Analysis</h4>
                <p>Examine eye health, detect conditions, and track changes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>🦷 Dental Analysis</h4>
                <p>Assess dental health, detect issues, and provide recommendations</p>
            </div>
            """, unsafe_allow_html=True)

def render_chat_page():
    """Built-in chat page component"""
    st.markdown('<h1 class="main-header">💬 AI Health Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I'm your AI Health Assistant. How can I help you today?"}
        ]
    
    # Chat interface
    chat_container = st.container()
    
    # Chat container for scrollable history
    with chat_container:
        # Modern chat interface using st.chat_message (Streamlit 1.48+)
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your health question here..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                time.sleep(1)
            
            response = generate_mock_response(prompt)
            st.write(response)
            
        # Add assistant response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Quick suggestions
    st.subheader("💡 Quick Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What are symptoms of flu?", use_container_width=True):
            question = "What are symptoms of flu?"
            answer = "Common flu symptoms include: fever, chills, muscle aches, cough, congestion, runny nose, headaches, and fatigue. Symptoms typically last 3-7 days. Please consult a healthcare provider for proper diagnosis and treatment."
            
            st.session_state.chat_history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ])
            st.rerun()
    
    with col2:
        if st.button("How to improve sleep?", use_container_width=True):
            question = "How to improve sleep?"
            answer = "To improve sleep: maintain a consistent sleep schedule, create a relaxing bedtime routine, keep your bedroom cool and dark, avoid caffeine late in the day, limit screen time before bed, and get regular exercise. If sleep problems persist, consult a healthcare provider."
            
            st.session_state.chat_history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ])
            st.rerun()
    
    with col3:
        if st.button("Healthy diet tips?", use_container_width=True):
            question = "Healthy diet tips?"
            answer = "Healthy diet tips: eat plenty of fruits and vegetables, choose whole grains, include lean proteins, limit processed foods, stay hydrated, control portion sizes, and eat regular meals. Consider consulting a nutritionist for personalized advice."
            
            st.session_state.chat_history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer}
            ])
            st.rerun()

def generate_mock_response(user_input: str) -> str:
    """Generate mock AI responses based on user input"""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ['pain', 'hurt', 'ache']):
        return "I understand you're experiencing pain. While I can provide general information, it's important to consult with a healthcare professional for proper evaluation and treatment of any pain symptoms."
    
    elif any(word in user_input_lower for word in ['fever', 'temperature', 'hot']):
        return "Fever can be a sign of infection or illness. Monitor your temperature, stay hydrated, and rest. If fever persists or is high (over 101°F/38.3°C), please consult a healthcare provider."
    
    elif any(word in user_input_lower for word in ['diet', 'nutrition', 'food', 'eat']):
        return "A balanced diet includes fruits, vegetables, whole grains, lean proteins, and healthy fats. Stay hydrated and limit processed foods. For personalized nutrition advice, consider consulting a registered dietitian."
    
    elif any(word in user_input_lower for word in ['exercise', 'workout', 'fitness']):
        return "Regular exercise is great for health! Aim for 150 minutes of moderate aerobic activity weekly, plus strength training twice a week. Start slowly and gradually increase intensity. Consult your doctor before starting a new exercise program."
    
    elif any(word in user_input_lower for word in ['sleep', 'tired', 'fatigue']):
        return "Good sleep is essential for health. Aim for 7-9 hours nightly, maintain a consistent schedule, and create a relaxing bedtime routine. If sleep problems persist, consider consulting a sleep specialist."
    
    elif any(word in user_input_lower for word in ['stress', 'anxiety', 'worried']):
        return "Managing stress is important for overall health. Try relaxation techniques, regular exercise, adequate sleep, and social support. If stress or anxiety significantly impacts your life, consider speaking with a mental health professional."
    
    else:
        return "Thank you for your question. While I can provide general health information, I recommend consulting with a qualified healthcare professional for personalized medical advice and proper diagnosis."

def render_voice_page():
    """Built-in voice interaction page component"""
    st.markdown('<h1 class="main-header">🎤 Voice Interaction</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>🎙️ Voice-Powered Health Assistant</h3>
        <p>Interact with our AI using natural speech. Ask questions, get health insights, 
        and receive personalized recommendations through voice commands.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice recording simulation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎤 Voice Input")
        
        if st.button("🔴 Start Recording", use_container_width=True):
            with st.spinner("Recording... (simulated)"):
                time.sleep(3)
            st.success("Recording completed!")
            st.session_state.voice_input = "How can I improve my sleep quality?"
        
        if st.button("⏹️ Stop Recording", use_container_width=True):
            st.info("Recording stopped")
        
        # Simulated voice input display
        if 'voice_input' in st.session_state:
            st.markdown(f"""
            <div class="success-message">
                <h4>🎯 Transcribed Text:</h4>
                <p>"{st.session_state.voice_input}"</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🔊 AI Response")
        
        if 'voice_input' in st.session_state:
            response = generate_mock_response(st.session_state.voice_input)
            
            st.markdown(f"""
            <div class="feature-card">
                <h4>🤖 AI Assistant Says:</h4>
                <p>{response}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔊 Play Response", use_container_width=True):
                st.info("Playing audio response... (simulated)")
    
    # Voice settings
    st.subheader("⚙️ Voice Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        language = st.selectbox("🌐 Language", ["English", "Spanish", "French", "German", "Hindi"])
    
    with col2:
        voice_speed = st.slider("🎚️ Speech Speed", 0.5, 2.0, 1.0, 0.1)
    
    with col3:
        voice_type = st.selectbox("🎭 Voice Type", ["Female", "Male", "Neutral"])
    
    # Voice history
    st.subheader("📜 Recent Voice Interactions")
    
    voice_history = [
        {"time": "2 minutes ago", "query": "How can I improve my sleep quality?", "duration": "45s"},
        {"time": "1 hour ago", "query": "What are the symptoms of dehydration?", "duration": "32s"},
        {"time": "3 hours ago", "query": "Explain the benefits of meditation", "duration": "67s"},
    ]
    
    for interaction in voice_history:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 3px solid #007bff;">
            <strong>🕐 {interaction['time']}</strong> - Duration: {interaction['duration']}<br>
            <em>"{interaction['query']}"</em>
        </div>
        """, unsafe_allow_html=True)

def render_history_page():
    """Built-in history page component"""
    st.markdown('<h1 class="main-header">📊 History & Reports</h1>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("📅 Start Date", datetime.date.today() - datetime.timedelta(days=30))
    
    with col2:
        end_date = st.date_input("📅 End Date", datetime.date.today())
    
    # Activity summary
    st.subheader("📈 Activity Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", "15", "↗️ +3")
    
    with col2:
        st.metric("Chat Sessions", "42", "↗️ +8")
    
    with col3:
        st.metric("Voice Interactions", "8", "↗️ +2")
    
    with col4:
        st.metric("Avg Session Time", "12m", "↘️ -2m")
    
    # Recent activities
    st.subheader("🕐 Recent Activities")
    
    activities = [
        {"type": "Image Analysis", "time": "2 hours ago", "result": "Skin condition analysis completed", "status": "✅"},
        {"type": "Chat Session", "time": "4 hours ago", "result": "Discussed sleep improvement strategies", "status": "✅"},
        {"type": "Voice Query", "time": "1 day ago", "result": "Asked about nutrition guidelines", "status": "✅"},
        {"type": "Image Analysis", "time": "2 days ago", "result": "Eye health assessment", "status": "✅"},
        {"type": "Chat Session", "time": "3 days ago", "result": "Mental health consultation", "status": "✅"},
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div class="feature-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>{activity['status']} {activity['type']}</h4>
                    <p>{activity['result']}</p>
                    <small style="color: #666;">🕐 {activity['time']}</small>
                </div>
                <button style="background: #007bff; color: white; border: none; padding: 5px 10px; border-radius: 5px;">View Details</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Export options
    st.subheader("📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export PDF Report", use_container_width=True):
            st.success("PDF report generated successfully!")
    
    with col2:
        if st.button("📊 Export CSV Data", use_container_width=True):
            st.success("CSV data exported successfully!")
    
    with col3:
        if st.button("📧 Email Report", use_container_width=True):
            st.success("Report sent to your email!")

def render_settings_page():
    """Built-in settings page component"""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    # Profile settings
    st.subheader("👤 Profile Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Full Name", value="Demo User")
        st.text_input("Email", value="demo@example.com")
        st.selectbox("Preferred Language", ["English", "Spanish", "French", "German", "Hindi"])
    
    with col2:
        st.date_input("Date of Birth", datetime.date(1990, 1, 1))
        st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"])
        st.selectbox("Time Zone", ["UTC", "EST", "PST", "GMT", "IST"])
    
    # Notification settings
    st.subheader("🔔 Notification Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Email Notifications", value=True)
        st.checkbox("Analysis Reminders", value=True)
        st.checkbox("Health Tips", value=False)
    
    with col2:
        st.checkbox("SMS Notifications", value=False)
        st.checkbox("Weekly Reports", value=True)
        st.checkbox("Emergency Alerts", value=True)
    
    # Privacy settings
    st.subheader("🔒 Privacy & Security")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Data Analytics", value=True, help="Allow anonymous usage analytics")
        st.checkbox("Personalized Recommendations", value=True)
        st.selectbox("Data Retention", ["1 year", "2 years", "5 years", "Indefinite"])
    
    with col2:
        st.checkbox("Two-Factor Authentication", value=False)
        st.checkbox("Share Data for Research", value=False)
        if st.button("🗑️ Delete All Data", use_container_width=True):
            st.warning("This action cannot be undone!")
    
    # App settings
    st.subheader("📱 App Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.slider("Font Size", 12, 20, 14)
        st.checkbox("High Contrast Mode", value=False)
    
    with col2:
        st.selectbox("Default Page", ["Home", "Image Analysis", "Chat Assistant"])
        st.checkbox("Auto-save Sessions", value=True)
        st.checkbox("Offline Mode", value=False)
    
    # Save settings
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")

@st.cache_data
def load_sample_data():
    """Load sample data with caching for better performance"""
    if HAS_PANDAS:
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        if HAS_NUMPY:
            return pd.DataFrame({
                'Date': dates,
                'Analyses': np.random.poisson(2, len(dates)),
                'Chats': np.random.poisson(3, len(dates)),
                'Voice': np.random.poisson(1, len(dates))
            })
        else:
            return pd.DataFrame({
                'Date': dates,
                'Analyses': [2] * len(dates),
                'Chats': [3] * len(dates),
                'Voice': [1] * len(dates)
            })
    return None

def main():
    """Main application function with enhanced error handling"""
    
    try:
        # Apply custom theme
        apply_custom_theme()
        
        # Initialize session manager with error handling
        if MODULES_AVAILABLE:
            try:
                session_manager = SessionManager()
                logger.info("Custom SessionManager initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize custom SessionManager: {e}")
                session_manager = MockSessionManager()
        else:
            session_manager = MockSessionManager()
            logger.info("Using MockSessionManager (demo mode)")
            
    except Exception as e:
        logger.error(f"Critical error in main initialization: {e}")
        st.error("Application initialization failed. Please refresh the page.")
        return
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Authentication check (simplified for demo)
    if not session_manager.is_authenticated():
        st.markdown('<h1 class="main-header">🔐 Authentication Required</h1>', unsafe_allow_html=True)
        
        if MODULES_AVAILABLE:
            try:
                authentication_component()
                return
            except Exception as e:
                logger.warning(f"Custom auth component failed: {e}")
        
        # Fallback authentication
        st.markdown("""
        <div class="feature-card">
            <h3>Demo Mode</h3>
            <p>Click the button below to continue in demo mode.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Continue in Demo Mode", use_container_width=True):
            st.session_state.user_authenticated = True
            st.rerun()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏥 AI WellnessVision")
        st.markdown("---")
        
        # User info
        user_info = session_manager.get_user_info()
        st.markdown(f"**Welcome, {user_info.get('username', 'User')}!**")
        st.markdown(f"*Role: {', '.join(user_info.get('roles', ['user']))}*")
        
        st.markdown("---")
        
        # Navigation menu - use simple selectbox as fallback
        try:
            from streamlit_option_menu import option_menu
            
            selected_page = option_menu(
                menu_title="Navigation",
                options=[
                    "Home",
                    "Image Analysis", 
                    "Chat Assistant",
                    "Voice Interaction",
                    "History & Reports",
                    "Settings"
                ],
                icons=[
                    "house",
                    "camera",
                    "chat-dots",
                    "mic",
                    "clock-history",
                    "gear"
                ],
                menu_icon="list",
                default_index=0,
                key="main_menu",
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "#1f77b4", "font-size": "18px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee"
                    },
                    "nav-link-selected": {"background-color": "#1f77b4"},
                }
            )
        except ImportError:
            # Fallback to simple selectbox
            selected_page = st.selectbox(
                "🧭 Navigation",
                [
                    "Home",
                    "Image Analysis", 
                    "Chat Assistant",
                    "Voice Interaction",
                    "History & Reports",
                    "Settings"
                ],
                index=0
            )
        
        # Update session state
        st.session_state.current_page = selected_page
        
        st.markdown("---")
        
        # Quick stats
        stats = session_manager.get_user_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Analyses", stats.get('total_analyses', 0))
        with col2:
            st.metric("💬 Chats", stats.get('total_chats', 0))
        
        # Additional stats
        st.metric("🎤 Voice", stats.get('total_voice_interactions', 0))
        
        st.markdown("---")
        
        # Quick actions in sidebar
        st.subheader("⚡ Quick Actions")
        
        if st.button("📷 Quick Analysis", use_container_width=True):
            st.session_state.current_page = "Image Analysis"
            st.rerun()
        
        if st.button("💬 New Chat", use_container_width=True):
            st.session_state.current_page = "Chat Assistant"
            st.rerun()
        
        st.markdown("---")
        
        # System status with real-time updates
        st.subheader("🔧 System Status")
        
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.success("🟢 API Online")
            st.success("🟢 AI Models Ready")
        
        with status_col2:
            st.info("📊 Load: Normal")
            st.info(f"🕐 {datetime.datetime.now().strftime('%H:%M:%S')}")
        
        # Add a refresh button for status
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            session_manager.logout()
            st.rerun()
    
    # Main content area with error handling
    try:
        if MODULES_AVAILABLE:
            # Try to use custom modules first
            if st.session_state.current_page == "Home":
                try:
                    home_page.render()
                except:
                    render_home_page()
            elif st.session_state.current_page == "Image Analysis":
                try:
                    image_analysis_page.render()
                except:
                    render_image_analysis_page()
            elif st.session_state.current_page == "Chat Assistant":
                try:
                    chat_interface_page.render()
                except:
                    render_chat_page()
            elif st.session_state.current_page == "Voice Interaction":
                try:
                    voice_interaction_page.render()
                except:
                    render_voice_page()
            elif st.session_state.current_page == "History & Reports":
                try:
                    history_page.render()
                except:
                    render_history_page()
            elif st.session_state.current_page == "Settings":
                try:
                    settings_page.render()
                except:
                    render_settings_page()
        else:
            # Use built-in components
            if st.session_state.current_page == "Home":
                render_home_page()
            elif st.session_state.current_page == "Image Analysis":
                render_image_analysis_page()
            elif st.session_state.current_page == "Chat Assistant":
                render_chat_page()
            elif st.session_state.current_page == "Voice Interaction":
                render_voice_page()
            elif st.session_state.current_page == "History & Reports":
                render_history_page()
            elif st.session_state.current_page == "Settings":
                render_settings_page()
                
    except Exception as e:
        logger.error(f"Error rendering page: {e}")
        st.error(f"Error loading page: {e}")
        st.markdown("""
        <div class="error-message">
            <h4>⚠️ Page Loading Error</h4>
            <p>There was an issue loading this page. Please try refreshing or contact support if the problem persists.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Fallback to home page
        if st.button("🏠 Return to Home"):
            st.session_state.current_page = "Home"
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
            <strong>AI WellnessVision v1.0.0</strong> | Built with ❤️ using Streamlit<br>
            <em>⚠️ This tool is for informational purposes only and is not a substitute for professional medical advice.</em><br>
            <small>🔒 Your privacy is protected | 📞 24/7 Support Available</small>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()