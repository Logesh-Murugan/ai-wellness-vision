#!/usr/bin/env python3
"""
AI WellnessVision - Streamlit Web Interface
Main application entry point with multi-page navigation
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import page modules
from ui.pages import (
    home_page,
    image_analysis_page,
    chat_interface_page,
    voice_interaction_page,
    history_page,
    settings_page
)
from ui.components.auth import authentication_component
from ui.utils.session_manager import SessionManager
from ui.utils.theme_config import apply_custom_theme

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

def main():
    """Main application function"""
    
    # Apply custom theme
    apply_custom_theme()
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Authentication check
    if not session_manager.is_authenticated():
        authentication_component()
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
        
        # Navigation menu
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
        
        st.markdown("---")
        
        # Quick stats
        stats = session_manager.get_user_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Analyses", stats.get('total_analyses', 0))
        with col2:
            st.metric("Chats", stats.get('total_chats', 0))
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            session_manager.logout()
            st.rerun()
    
    # Main content area
    if selected_page == "Home":
        home_page.render()
    elif selected_page == "Image Analysis":
        image_analysis_page.render()
    elif selected_page == "Chat Assistant":
        chat_interface_page.render()
    elif selected_page == "Voice Interaction":
        voice_interaction_page.render()
    elif selected_page == "History & Reports":
        history_page.render()
    elif selected_page == "Settings":
        settings_page.render()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 12px;'>
            AI WellnessVision v1.0.0 | Built with ❤️ using Streamlit<br>
            <em>This tool is for informational purposes only and is not a substitute for professional medical advice.</em>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()