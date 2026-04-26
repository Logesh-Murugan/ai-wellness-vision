# settings_page.py - User settings and preferences
import streamlit as st
from datetime import datetime

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
    """Render the settings page"""
    
    # Initialize session manager
    if UTILS_AVAILABLE:
        session_manager = SessionManager()
    else:
        # Mock session manager
        class MockSessionManager:
            def get_preferences(self): return {"language": "en", "theme": "light", "voice_enabled": True, "notifications": True}
            def update_preferences(self, prefs): pass
            def get_user_info(self): return {"username": "demo_user", "email": "demo@example.com"}
            def export_data(self): return {"message": "Demo data export"}
            def clear_history(self, history_type): pass
        session_manager = MockSessionManager()
    
    st.title("⚙️ Settings & Preferences")
    st.markdown("Customize your AI WellnessVision experience")
    
    # Get current preferences
    preferences = session_manager.get_preferences()
    user_info = session_manager.get_user_info()
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🌐 General", "🎨 Appearance", "🔒 Privacy", "📊 Data"])
    
    with tab1:
        render_general_settings(session_manager, preferences)
    
    with tab2:
        render_appearance_settings(session_manager, preferences)
    
    with tab3:
        render_privacy_settings(session_manager, preferences)
    
    with tab4:
        render_data_settings(session_manager, user_info)

def render_general_settings(session_manager, preferences):
    """Render general settings"""
    
    st.subheader("🌐 General Settings")
    
    # Language settings
    st.markdown("#### Language Preferences")
    
    language = st.selectbox(
        "Interface Language",
        ["en", "hi", "ta", "te", "bn", "gu", "mr"],
        index=["en", "hi", "ta", "te", "bn", "gu", "mr"].index(preferences.get("language", "en")),
        format_func=lambda x: {
            "en": "🇺🇸 English",
            "hi": "🇮🇳 Hindi - हिंदी",
            "ta": "🇮🇳 Tamil - தமிழ்",
            "te": "🇮🇳 Telugu - తెలుగు",
            "bn": "🇮🇳 Bengali - বাংলা",
            "gu": "🇮🇳 Gujarati - ગુજરાતી",
            "mr": "🇮🇳 Marathi - मराठी"
        }.get(x, x)
    )
    
    # Voice settings
    st.markdown("#### Voice & Audio")
    
    voice_enabled = st.checkbox(
        "Enable Voice Features",
        value=preferences.get("voice_enabled", True),
        help="Enable speech-to-text and text-to-speech features"
    )
    
    if voice_enabled:
        voice_speed = st.slider(
            "Voice Speed",
            min_value=0.5,
            max_value=2.0,
            value=preferences.get("voice_speed", 1.0),
            step=0.1,
            help="Adjust the speed of text-to-speech output"
        )
        
        voice_type = st.selectbox(
            "Preferred Voice",
            ["female", "male", "child"],
            index=["female", "male", "child"].index(preferences.get("voice_type", "female")),
            format_func=lambda x: x.title()
        )
    
    # Notification settings
    st.markdown("#### Notifications")
    
    notifications = st.checkbox(
        "Enable Notifications",
        value=preferences.get("notifications", True),
        help="Receive notifications about analysis results and health tips"
    )
    
    if notifications:
        health_tips = st.checkbox(
            "Daily Health Tips",
            value=preferences.get("health_tips", True)
        )
        
        analysis_alerts = st.checkbox(
            "Analysis Completion Alerts",
            value=preferences.get("analysis_alerts", True)
        )
    
    # Save settings
    if st.button("💾 Save General Settings", type="primary"):
        new_preferences = {
            "language": language,
            "voice_enabled": voice_enabled,
            "notifications": notifications
        }
        
        if voice_enabled:
            new_preferences.update({
                "voice_speed": voice_speed,
                "voice_type": voice_type
            })
        
        if notifications:
            new_preferences.update({
                "health_tips": health_tips,
                "analysis_alerts": analysis_alerts
            })
        
        session_manager.update_preferences(new_preferences)
        st.success("✅ General settings saved successfully!")

def render_appearance_settings(session_manager, preferences):
    """Render appearance settings"""
    
    st.subheader("🎨 Appearance Settings")
    
    # Theme settings
    st.markdown("#### Theme")
    
    theme = st.selectbox(
        "Color Theme",
        ["light", "dark", "auto"],
        index=["light", "dark", "auto"].index(preferences.get("theme", "light")),
        format_func=lambda x: {
            "light": "☀️ Light Mode",
            "dark": "🌙 Dark Mode", 
            "auto": "🔄 Auto (System)"
        }.get(x, x)
    )
    
    # Layout settings
    st.markdown("#### Layout")
    
    sidebar_expanded = st.checkbox(
        "Expand Sidebar by Default",
        value=preferences.get("sidebar_expanded", True)
    )
    
    show_tips = st.checkbox(
        "Show Helpful Tips",
        value=preferences.get("show_tips", True),
        help="Display helpful tips and guidance throughout the interface"
    )
    
    # Display settings
    st.markdown("#### Display")
    
    results_per_page = st.number_input(
        "Results per Page",
        min_value=5,
        max_value=50,
        value=preferences.get("results_per_page", 10),
        step=5,
        help="Number of results to show per page in history views"
    )
    
    show_confidence = st.checkbox(
        "Always Show Confidence Scores",
        value=preferences.get("show_confidence", True),
        help="Display AI confidence scores with all predictions"
    )
    
    # Save appearance settings
    if st.button("💾 Save Appearance Settings", type="primary"):
        new_preferences = {
            "theme": theme,
            "sidebar_expanded": sidebar_expanded,
            "show_tips": show_tips,
            "results_per_page": results_per_page,
            "show_confidence": show_confidence
        }
        
        session_manager.update_preferences(new_preferences)
        st.success("✅ Appearance settings saved successfully!")
        st.info("🔄 Some changes may require refreshing the page to take effect.")

def render_privacy_settings(session_manager, preferences):
    """Render privacy settings"""
    
    st.subheader("🔒 Privacy & Security")
    
    # Data collection settings
    st.markdown("#### Data Collection")
    
    analytics = st.checkbox(
        "Allow Usage Analytics",
        value=preferences.get("analytics", True),
        help="Help improve the platform by sharing anonymous usage data"
    )
    
    save_conversations = st.checkbox(
        "Save Conversation History",
        value=preferences.get("save_conversations", True),
        help="Store your conversations for future reference"
    )
    
    save_analyses = st.checkbox(
        "Save Analysis Results",
        value=preferences.get("save_analyses", True),
        help="Store your image analysis results"
    )
    
    # Security settings
    st.markdown("#### Security")
    
    auto_logout = st.number_input(
        "Auto Logout (minutes)",
        min_value=5,
        max_value=120,
        value=preferences.get("auto_logout", 30),
        step=5,
        help="Automatically log out after period of inactivity"
    )
    
    require_confirmation = st.checkbox(
        "Require Confirmation for Sensitive Actions",
        value=preferences.get("require_confirmation", True),
        help="Ask for confirmation before deleting data or changing important settings"
    )
    
    # Data retention
    st.markdown("#### Data Retention")
    
    retention_period = st.selectbox(
        "Keep Data For",
        ["1_month", "3_months", "6_months", "1_year", "indefinite"],
        index=["1_month", "3_months", "6_months", "1_year", "indefinite"].index(
            preferences.get("retention_period", "6_months")
        ),
        format_func=lambda x: {
            "1_month": "1 Month",
            "3_months": "3 Months",
            "6_months": "6 Months",
            "1_year": "1 Year",
            "indefinite": "Keep Forever"
        }.get(x, x)
    )
    
    # Save privacy settings
    if st.button("💾 Save Privacy Settings", type="primary"):
        new_preferences = {
            "analytics": analytics,
            "save_conversations": save_conversations,
            "save_analyses": save_analyses,
            "auto_logout": auto_logout,
            "require_confirmation": require_confirmation,
            "retention_period": retention_period
        }
        
        session_manager.update_preferences(new_preferences)
        st.success("✅ Privacy settings saved successfully!")

def render_data_settings(session_manager, user_info):
    """Render data management settings"""
    
    st.subheader("📊 Data Management")
    
    # Account information
    st.markdown("#### Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=user_info.get("username", ""), disabled=True)
        st.text_input("Email", value=user_info.get("email", ""), disabled=True)
    
    with col2:
        st.text_input("Account Type", value="Standard User", disabled=True)
        st.text_input("Member Since", value="Demo Account", disabled=True)
    
    # Data export
    st.markdown("#### Export Your Data")
    
    st.markdown("""
    Download all your data including conversations, analysis results, and preferences.
    This data is provided in JSON format for portability.
    """)
    
    if st.button("📥 Export All Data", use_container_width=True):
        with st.spinner("Preparing your data export..."):
            import time
            time.sleep(2)  # Simulate export preparation
            
            export_data = session_manager.export_data()
            
            import json
            export_json = json.dumps(export_data, indent=2, default=str)
            
            st.download_button(
                label="📄 Download Data Export",
                data=export_json,
                file_name=f"wellnessvision_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            st.success("✅ Data export ready for download!")
    
    # Data deletion
    st.markdown("#### Delete Your Data")
    
    st.warning("""
    ⚠️ **Warning:** These actions cannot be undone. Please make sure you have exported 
    any data you want to keep before proceeding.
    """)
    
    col_del1, col_del2 = st.columns(2)
    
    with col_del1:
        if st.button("🗑️ Clear Conversation History", use_container_width=True):
            if st.session_state.get("confirm_clear_conversations", False):
                session_manager.clear_history("conversations")
                st.success("✅ Conversation history cleared!")
                st.session_state.confirm_clear_conversations = False
            else:
                st.session_state.confirm_clear_conversations = True
                st.warning("Click again to confirm deletion of conversation history.")
    
    with col_del2:
        if st.button("🗑️ Clear Analysis History", use_container_width=True):
            if st.session_state.get("confirm_clear_analyses", False):
                session_manager.clear_history("analyses")
                st.success("✅ Analysis history cleared!")
                st.session_state.confirm_clear_analyses = False
            else:
                st.session_state.confirm_clear_analyses = True
                st.warning("Click again to confirm deletion of analysis history.")
    
    if st.button("🗑️ Clear All Data", type="primary", use_container_width=True):
        if st.session_state.get("confirm_clear_all", False):
            session_manager.clear_history("all")
            st.success("✅ All data cleared!")
            st.session_state.confirm_clear_all = False
        else:
            st.session_state.confirm_clear_all = True
            st.error("⚠️ Click again to confirm deletion of ALL your data. This cannot be undone!")
    
    # Storage usage (mock data)
    st.markdown("#### Storage Usage")
    
    col_storage1, col_storage2, col_storage3 = st.columns(3)
    
    with col_storage1:
        st.metric("Conversations", "2.3 MB")
    
    with col_storage2:
        st.metric("Analysis Results", "1.8 MB")
    
    with col_storage3:
        st.metric("Total Usage", "4.1 MB")
    
    # Progress bar for storage usage
    st.progress(0.041)  # 4.1MB out of 100MB limit
    st.caption("4.1 MB of 100 MB used (4.1%)")