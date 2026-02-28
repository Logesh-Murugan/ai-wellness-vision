# auth.py - Authentication component for Streamlit
import streamlit as st
from src.ui.utils.session_manager import SessionManager
from src.ui.utils.theme_config import create_custom_component

def authentication_component():
    """Render authentication interface"""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h1>🏥 AI WellnessVision</h1>
                <p style='color: #666; font-size: 18px;'>
                    Your AI-powered health and wellness companion
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Login form
        with st.container():
            st.markdown(
                create_custom_component(
                    """
                    <h3 style='text-align: center; margin-bottom: 1.5rem;'>
                        Sign In to Continue
                    </h3>
                    """,
                    "card"
                ),
                unsafe_allow_html=True
            )
            
            # Login form
            with st.form("login_form"):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    help="Use 'admin' or 'testuser' for demo"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Use 'admin123' for admin or 'user123' for testuser"
                )
                
                col_login, col_demo = st.columns(2)
                
                with col_login:
                    login_clicked = st.form_submit_button(
                        "🔐 Sign In",
                        use_container_width=True
                    )
                
                with col_demo:
                    demo_clicked = st.form_submit_button(
                        "🎯 Demo Mode",
                        use_container_width=True
                    )
            
            # Handle login
            if login_clicked:
                if username and password:
                    session_manager = SessionManager()
                    
                    with st.spinner("Authenticating..."):
                        if session_manager.authenticate(username, password):
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please try again.")
                else:
                    st.warning("⚠️ Please enter both username and password.")
            
            # Handle demo mode
            if demo_clicked:
                session_manager = SessionManager()
                
                # Authenticate with demo user
                if session_manager.authenticate("testuser", "user123"):
                    st.success("✅ Demo mode activated! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Demo mode unavailable. Please try manual login.")
        
        # Demo credentials info
        with st.expander("🔍 Demo Credentials", expanded=False):
            st.markdown(
                """
                **Available Demo Accounts:**
                
                **Admin Account:**
                - Username: `admin`
                - Password: `admin123`
                - Access: Full system access including admin features
                
                **User Account:**
                - Username: `testuser`
                - Password: `user123`
                - Access: Standard user features
                
                **Note:** These are demo credentials for testing purposes only.
                """
            )
        
        # Features overview
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>🌟 Platform Features</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        feature_col1, feature_col2 = st.columns(2)
        
        with feature_col1:
            st.markdown(
                """
                **🖼️ Image Analysis**
                - Skin condition detection
                - Eye health assessment
                - Food recognition
                - Emotion analysis
                
                **💬 AI Chat Assistant**
                - Health consultations
                - Symptom analysis
                - Medical information
                - Multi-language support
                """
            )
        
        with feature_col2:
            st.markdown(
                """
                **🎤 Voice Interactions**
                - Speech-to-text
                - Text-to-speech
                - Voice consultations
                - Hands-free operation
                
                **🔍 Explainable AI**
                - Decision explanations
                - Visual insights
                - Confidence scores
                - Transparent recommendations
                """
            )
        
        # Disclaimer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; font-size: 12px; font-style: italic;'>
                ⚠️ This platform is for informational purposes only and is not a substitute 
                for professional medical advice, diagnosis, or treatment.
            </div>
            """,
            unsafe_allow_html=True
        )