# settings_page.py - Settings and preferences page
import streamlit as st
from ui.utils.session_manager import SessionManager
from ui.utils.theme_config import create_custom_component

def render():
    """Render the settings page"""
    
    st.title("⚙️ Settings & Preferences")
    st.markdown("Customize your AI WellnessVision experience")
    
    session_manager = SessionManager()
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Profile",
        "🌐 Language", 
        "🎨 Interface",
        "🔔 Notifications",
        "🔒 Privacy"
    ])
    
    with tab1:
        render_profile_settings(session_manager)
    
    with tab2:
        render_language_settings(session_manager)
    
    with tab3:
        render_interface_settings(session_manager)
    
    with tab4:
        render_notification_settings(session_manager)
    
    with tab5:
        render_privacy_settings(session_manager)

def render_profile_settings(session_manager):
    """Render profile settings"""
    
    st.markdown("### 👤 Profile Settings")
    
    user_info = session_manager.get_user_info()
    
    # User information display
    st.markdown(
        create_custom_component(
            f"""
            <h4>📋 Account Information</h4>
            <p><strong>Username:</strong> {user_info.get('username', 'Unknown')}</p>
            <p><strong>Email:</strong> {user_info.get('email', 'Not provided')}</p>
            <p><strong>Roles:</strong> {', '.join(user_info.get('roles', ['user']))}</p>
            <p><strong>Session ID:</strong> {session_manager.get_session_id()[:16]}...</p>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )
    
    # Profile preferences
    st.markdown("#### 🎯 Profile Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_name = st.text_input(
            "Display Name",
            value=user_info.get('username', ''),
            help="How you'd like to be addressed"
        )
        
        preferred_language = st.selectbox(
            "Preferred Language",
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
            help="Default language for interactions"
        )
    
    with col2:
        timezone = st.selectbox(
            "Timezone",
            options=[
                "UTC",
                "Asia/Kolkata",
                "America/New_York",
                "Europe/London",
                "Asia/Tokyo"
            ],
            index=1,  # Default to India
            help="Your local timezone"
        )
        
        date_format = st.selectbox(
            "Date Format",
            options=["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"],
            help="Preferred date display format"
        )
    
    # Health profile
    st.markdown("#### 🏥 Health Profile (Optional)")
    
    with st.expander("Health Information", expanded=False):
        st.info("This information helps provide more personalized health guidance. All data is kept private and secure.")
        
        col_health1, col_health2 = st.columns(2)
        
        with col_health1:
            age_range = st.selectbox(
                "Age Range",
                options=["Prefer not to say", "18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
                help="Age range for age-appropriate advice"
            )
            
            gender = st.selectbox(
                "Gender",
                options=["Prefer not to say", "Male", "Female", "Non-binary", "Other"],
                help="For gender-specific health information"
            )
        
        with col_health2:
            health_conditions = st.multiselect(
                "Known Health Conditions",
                options=[
                    "Diabetes",
                    "Hypertension", 
                    "Heart Disease",
                    "Asthma",
                    "Allergies",
                    "Arthritis",
                    "Other"
                ],
                help="Select any known conditions"
            )
            
            medications = st.text_area(
                "Current Medications",
                placeholder="List any medications you're taking (optional)",
                help="This helps avoid drug interactions in advice"
            )
    
    # Save profile settings
    if st.button("💾 Save Profile Settings", type="primary"):
        # Update preferences
        preferences = session_manager.get_preferences()
        preferences.update({
            'display_name': display_name,
            'language': preferred_language,
            'timezone': timezone,
            'date_format': date_format,
            'health_profile': {
                'age_range': age_range,
                'gender': gender,
                'health_conditions': health_conditions,
                'medications': medications
            }
        })
        session_manager.update_preferences(preferences)
        st.success("✅ Profile settings saved!")

def render_language_settings(session_manager):
    """Render language settings"""
    
    st.markdown("### 🌐 Language & Localization")
    
    preferences = session_manager.get_preferences()
    
    # Primary language
    col1, col2 = st.columns(2)
    
    with col1:
        primary_language = st.selectbox(
            "Primary Language",
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
            index=0,
            help="Main language for the interface and AI responses"
        )
    
    with col2:
        auto_detect = st.checkbox(
            "Auto-detect Language",
            value=preferences.get('auto_detect_language', True),
            help="Automatically detect language from your messages"
        )
    
    # Secondary languages
    st.markdown("#### 🔄 Secondary Languages")
    
    secondary_languages = st.multiselect(
        "Additional Languages",
        options=["hi", "ta", "te", "bn", "gu", "mr"],
        format_func=lambda x: {
            "hi": "🇮🇳 Hindi", 
            "ta": "🇮🇳 Tamil",
            "te": "🇮🇳 Telugu",
            "bn": "🇮🇳 Bengali",
            "gu": "🇮🇳 Gujarati",
            "mr": "🇮🇳 Marathi"
        }[x],
        help="Languages you might use occasionally"
    )
    
    # Translation settings
    st.markdown("#### 🔄 Translation Settings")
    
    col_trans1, col_trans2 = st.columns(2)
    
    with col_trans1:
        enable_translation = st.checkbox(
            "Enable Translation",
            value=preferences.get('enable_translation', True),
            help="Translate responses to your preferred language"
        )
        
        show_original = st.checkbox(
            "Show Original Text",
            value=preferences.get('show_original', False),
            help="Show original text alongside translations"
        )
    
    with col_trans2:
        translation_confidence = st.slider(
            "Translation Confidence Threshold",
            min_value=0.5,
            max_value=1.0,
            value=preferences.get('translation_confidence', 0.8),
            step=0.1,
            help="Minimum confidence for automatic translation"
        )
    
    # Regional settings
    st.markdown("#### 🌍 Regional Settings")
    
    col_region1, col_region2 = st.columns(2)
    
    with col_region1:
        region = st.selectbox(
            "Region",
            options=["India", "United States", "United Kingdom", "Canada", "Australia"],
            help="Your region for localized health information"
        )
    
    with col_region2:
        measurement_system = st.selectbox(
            "Measurement System",
            options=["Metric", "Imperial"],
            help="Preferred system for measurements"
        )
    
    # Save language settings
    if st.button("💾 Save Language Settings", type="primary"):
        preferences.update({
            'language': primary_language,
            'auto_detect_language': auto_detect,
            'secondary_languages': secondary_languages,
            'enable_translation': enable_translation,
            'show_original': show_original,
            'translation_confidence': translation_confidence,
            'region': region,
            'measurement_system': measurement_system
        })
        session_manager.update_preferences(preferences)
        st.success("✅ Language settings saved!")

def render_interface_settings(session_manager):
    """Render interface settings"""
    
    st.markdown("### 🎨 Interface & Display")
    
    preferences = session_manager.get_preferences()
    
    # Theme settings
    st.markdown("#### 🎨 Theme")
    
    col_theme1, col_theme2 = st.columns(2)
    
    with col_theme1:
        theme = st.selectbox(
            "Color Theme",
            options=["light", "dark", "auto"],
            format_func=lambda x: {
                "light": "☀️ Light Theme",
                "dark": "🌙 Dark Theme",
                "auto": "🔄 Auto (System)"
            }[x],
            index=0,
            help="Choose your preferred color scheme"
        )
    
    with col_theme2:
        accent_color = st.selectbox(
            "Accent Color",
            options=["blue", "green", "purple", "orange", "red"],
            format_func=lambda x: {
                "blue": "🔵 Blue",
                "green": "🟢 Green", 
                "purple": "🟣 Purple",
                "orange": "🟠 Orange",
                "red": "🔴 Red"
            }[x],
            help="Primary accent color for the interface"
        )
    
    # Layout settings
    st.markdown("#### 📐 Layout")
    
    col_layout1, col_layout2 = st.columns(2)
    
    with col_layout1:
        sidebar_position = st.selectbox(
            "Sidebar Position",
            options=["left", "right"],
            format_func=lambda x: {
                "left": "⬅️ Left Side",
                "right": "➡️ Right Side"
            }[x],
            help="Position of the navigation sidebar"
        )
        
        compact_mode = st.checkbox(
            "Compact Mode",
            value=preferences.get('compact_mode', False),
            help="Use more compact spacing for better screen utilization"
        )
    
    with col_layout2:
        font_size = st.selectbox(
            "Font Size",
            options=["small", "medium", "large"],
            format_func=lambda x: {
                "small": "🔤 Small",
                "medium": "🔤 Medium",
                "large": "🔤 Large"
            }[x],
            index=1,
            help="Base font size for the interface"
        )
        
        high_contrast = st.checkbox(
            "High Contrast",
            value=preferences.get('high_contrast', False),
            help="Increase contrast for better accessibility"
        )
    
    # Chat interface settings
    st.markdown("#### 💬 Chat Interface")
    
    col_chat1, col_chat2 = st.columns(2)
    
    with col_chat1:
        message_animation = st.checkbox(
            "Message Animations",
            value=preferences.get('message_animation', True),
            help="Animate message appearance"
        )
        
        typing_indicator = st.checkbox(
            "Typing Indicator",
            value=preferences.get('typing_indicator', True),
            help="Show when AI is generating response"
        )
    
    with col_chat2:
        message_timestamps = st.checkbox(
            "Show Timestamps",
            value=preferences.get('message_timestamps', True),
            help="Display timestamps on messages"
        )
        
        message_grouping = st.checkbox(
            "Group Messages",
            value=preferences.get('message_grouping', True),
            help="Group consecutive messages from same sender"
        )
    
    # Accessibility settings
    st.markdown("#### ♿ Accessibility")
    
    col_access1, col_access2 = st.columns(2)
    
    with col_access1:
        screen_reader = st.checkbox(
            "Screen Reader Support",
            value=preferences.get('screen_reader', False),
            help="Enhanced support for screen readers"
        )
        
        keyboard_navigation = st.checkbox(
            "Enhanced Keyboard Navigation",
            value=preferences.get('keyboard_navigation', False),
            help="Improved keyboard-only navigation"
        )
    
    with col_access2:
        reduce_motion = st.checkbox(
            "Reduce Motion",
            value=preferences.get('reduce_motion', False),
            help="Minimize animations and transitions"
        )
        
        focus_indicators = st.checkbox(
            "Enhanced Focus Indicators",
            value=preferences.get('focus_indicators', False),
            help="More visible focus indicators"
        )
    
    # Save interface settings
    if st.button("💾 Save Interface Settings", type="primary"):
        preferences.update({
            'theme': theme,
            'accent_color': accent_color,
            'sidebar_position': sidebar_position,
            'compact_mode': compact_mode,
            'font_size': font_size,
            'high_contrast': high_contrast,
            'message_animation': message_animation,
            'typing_indicator': typing_indicator,
            'message_timestamps': message_timestamps,
            'message_grouping': message_grouping,
            'screen_reader': screen_reader,
            'keyboard_navigation': keyboard_navigation,
            'reduce_motion': reduce_motion,
            'focus_indicators': focus_indicators
        })
        session_manager.update_preferences(preferences)
        st.success("✅ Interface settings saved!")

def render_notification_settings(session_manager):
    """Render notification settings"""
    
    st.markdown("### 🔔 Notifications & Alerts")
    
    preferences = session_manager.get_preferences()
    
    # General notification settings
    st.markdown("#### 🔔 General Notifications")
    
    col_notif1, col_notif2 = st.columns(2)
    
    with col_notif1:
        enable_notifications = st.checkbox(
            "Enable Notifications",
            value=preferences.get('notifications', True),
            help="Receive notifications from the application"
        )
        
        browser_notifications = st.checkbox(
            "Browser Notifications",
            value=preferences.get('browser_notifications', False),
            help="Show notifications in your browser"
        )
    
    with col_notif2:
        sound_notifications = st.checkbox(
            "Sound Notifications",
            value=preferences.get('sound_notifications', True),
            help="Play sounds for notifications"
        )
        
        notification_volume = st.slider(
            "Notification Volume",
            min_value=0.0,
            max_value=1.0,
            value=preferences.get('notification_volume', 0.5),
            step=0.1,
            help="Volume level for notification sounds"
        )
    
    # Health alerts
    st.markdown("#### 🏥 Health Alerts")
    
    col_health1, col_health2 = st.columns(2)
    
    with col_health1:
        urgent_alerts = st.checkbox(
            "Urgent Health Alerts",
            value=preferences.get('urgent_alerts', True),
            help="Receive alerts for urgent health concerns"
        )
        
        medication_reminders = st.checkbox(
            "Medication Reminders",
            value=preferences.get('medication_reminders', False),
            help="Reminders for medication schedules"
        )
    
    with col_health2:
        wellness_tips = st.checkbox(
            "Daily Wellness Tips",
            value=preferences.get('wellness_tips', True),
            help="Receive daily health and wellness tips"
        )
        
        checkup_reminders = st.checkbox(
            "Checkup Reminders",
            value=preferences.get('checkup_reminders', False),
            help="Reminders for regular health checkups"
        )
    
    # System notifications
    st.markdown("#### ⚙️ System Notifications")
    
    col_system1, col_system2 = st.columns(2)
    
    with col_system1:
        system_updates = st.checkbox(
            "System Updates",
            value=preferences.get('system_updates', True),
            help="Notifications about system updates and maintenance"
        )
        
        feature_announcements = st.checkbox(
            "Feature Announcements",
            value=preferences.get('feature_announcements', True),
            help="Notifications about new features"
        )
    
    with col_system2:
        security_alerts = st.checkbox(
            "Security Alerts",
            value=preferences.get('security_alerts', True),
            help="Important security-related notifications"
        )
        
        usage_reports = st.checkbox(
            "Usage Reports",
            value=preferences.get('usage_reports', False),
            help="Weekly/monthly usage summary reports"
        )
    
    # Notification schedule
    st.markdown("#### ⏰ Notification Schedule")
    
    col_schedule1, col_schedule2 = st.columns(2)
    
    with col_schedule1:
        quiet_hours_start = st.time_input(
            "Quiet Hours Start",
            value=preferences.get('quiet_hours_start', None),
            help="Start time for quiet hours (no notifications)"
        )
    
    with col_schedule2:
        quiet_hours_end = st.time_input(
            "Quiet Hours End", 
            value=preferences.get('quiet_hours_end', None),
            help="End time for quiet hours"
        )
    
    # Save notification settings
    if st.button("💾 Save Notification Settings", type="primary"):
        preferences.update({
            'notifications': enable_notifications,
            'browser_notifications': browser_notifications,
            'sound_notifications': sound_notifications,
            'notification_volume': notification_volume,
            'urgent_alerts': urgent_alerts,
            'medication_reminders': medication_reminders,
            'wellness_tips': wellness_tips,
            'checkup_reminders': checkup_reminders,
            'system_updates': system_updates,
            'feature_announcements': feature_announcements,
            'security_alerts': security_alerts,
            'usage_reports': usage_reports,
            'quiet_hours_start': quiet_hours_start,
            'quiet_hours_end': quiet_hours_end
        })
        session_manager.update_preferences(preferences)
        st.success("✅ Notification settings saved!")

def render_privacy_settings(session_manager):
    """Render privacy and security settings"""
    
    st.markdown("### 🔒 Privacy & Security")
    
    preferences = session_manager.get_preferences()
    
    # Data privacy
    st.markdown("#### 🛡️ Data Privacy")
    
    col_privacy1, col_privacy2 = st.columns(2)
    
    with col_privacy1:
        data_collection = st.selectbox(
            "Data Collection Level",
            options=["minimal", "standard", "enhanced"],
            format_func=lambda x: {
                "minimal": "🔒 Minimal (Essential only)",
                "standard": "⚖️ Standard (Recommended)",
                "enhanced": "📊 Enhanced (Full analytics)"
            }[x],
            index=1,
            help="Level of data collection for service improvement"
        )
        
        anonymize_data = st.checkbox(
            "Anonymize Personal Data",
            value=preferences.get('anonymize_data', False),
            help="Remove personal identifiers from stored data"
        )
    
    with col_privacy2:
        share_analytics = st.checkbox(
            "Share Anonymous Analytics",
            value=preferences.get('share_analytics', True),
            help="Help improve the service by sharing anonymous usage data"
        )
        
        marketing_communications = st.checkbox(
            "Marketing Communications",
            value=preferences.get('marketing_communications', False),
            help="Receive marketing emails and updates"
        )
    
    # Data retention
    st.markdown("#### 🗄️ Data Retention")
    
    col_retention1, col_retention2 = st.columns(2)
    
    with col_retention1:
        conversation_retention = st.selectbox(
            "Conversation History Retention",
            options=["1_week", "1_month", "3_months", "1_year", "indefinite"],
            format_func=lambda x: {
                "1_week": "1 Week",
                "1_month": "1 Month",
                "3_months": "3 Months",
                "1_year": "1 Year",
                "indefinite": "Keep Indefinitely"
            }[x],
            index=2,
            help="How long to keep conversation history"
        )
    
    with col_retention2:
        analysis_retention = st.selectbox(
            "Analysis Results Retention",
            options=["1_month", "3_months", "6_months", "1_year", "indefinite"],
            format_func=lambda x: {
                "1_month": "1 Month",
                "3_months": "3 Months", 
                "6_months": "6 Months",
                "1_year": "1 Year",
                "indefinite": "Keep Indefinitely"
            }[x],
            index=3,
            help="How long to keep analysis results"
        )
    
    # Security settings
    st.markdown("#### 🔐 Security Settings")
    
    col_security1, col_security2 = st.columns(2)
    
    with col_security1:
        session_timeout = st.selectbox(
            "Session Timeout",
            options=[15, 30, 60, 120, 240],
            format_func=lambda x: f"{x} minutes",
            index=1,
            help="Automatic logout after inactivity"
        )
        
        require_reauth = st.checkbox(
            "Require Re-authentication",
            value=preferences.get('require_reauth', False),
            help="Require password for sensitive operations"
        )
    
    with col_security2:
        login_notifications = st.checkbox(
            "Login Notifications",
            value=preferences.get('login_notifications', True),
            help="Notify about new login sessions"
        )
        
        suspicious_activity = st.checkbox(
            "Suspicious Activity Alerts",
            value=preferences.get('suspicious_activity', True),
            help="Alert about unusual account activity"
        )
    
    # Data export and deletion
    st.markdown("#### 📤 Data Management")
    
    col_data1, col_data2, col_data3 = st.columns(3)
    
    with col_data1:
        if st.button("📥 Export My Data", use_container_width=True):
            export_user_data(session_manager)
    
    with col_data2:
        if st.button("🗑️ Clear History", use_container_width=True):
            clear_user_data(session_manager)
    
    with col_data3:
        if st.button("❌ Delete Account", use_container_width=True):
            delete_account_request(session_manager)
    
    # Privacy policy and terms
    st.markdown("---")
    st.markdown("#### 📋 Legal & Compliance")
    
    col_legal1, col_legal2 = st.columns(2)
    
    with col_legal1:
        if st.button("📄 Privacy Policy", use_container_width=True):
            show_privacy_policy()
    
    with col_legal2:
        if st.button("📜 Terms of Service", use_container_width=True):
            show_terms_of_service()
    
    # Save privacy settings
    if st.button("💾 Save Privacy Settings", type="primary"):
        preferences.update({
            'data_collection': data_collection,
            'anonymize_data': anonymize_data,
            'share_analytics': share_analytics,
            'marketing_communications': marketing_communications,
            'conversation_retention': conversation_retention,
            'analysis_retention': analysis_retention,
            'session_timeout': session_timeout,
            'require_reauth': require_reauth,
            'login_notifications': login_notifications,
            'suspicious_activity': suspicious_activity
        })
        session_manager.update_preferences(preferences)
        st.success("✅ Privacy settings saved!")

def export_user_data(session_manager):
    """Export all user data"""
    
    user_data = session_manager.export_data()
    
    import json
    export_json = json.dumps(user_data, indent=2, ensure_ascii=False, default=str)
    
    st.download_button(
        label="📥 Download My Data (JSON)",
        data=export_json,
        file_name=f"my_data_export_{int(datetime.now().timestamp())}.json",
        mime="application/json"
    )
    
    st.success("✅ Data export prepared! Click the download button above.")

def clear_user_data(session_manager):
    """Clear user data with confirmation"""
    
    if 'confirm_clear_data' not in st.session_state:
        st.session_state.confirm_clear_data = False
    
    if not st.session_state.confirm_clear_data:
        st.warning("⚠️ This will permanently delete all your conversation and analysis history.")
        if st.button("⚠️ Confirm Clear All Data"):
            st.session_state.confirm_clear_data = True
            st.rerun()
    else:
        col_clear1, col_clear2 = st.columns(2)
        
        with col_clear1:
            if st.button("✅ Yes, Clear All Data", type="primary"):
                session_manager.clear_history("all")
                st.session_state.confirm_clear_data = False
                st.success("✅ All data cleared successfully!")
                st.rerun()
        
        with col_clear2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_clear_data = False
                st.rerun()

def delete_account_request(session_manager):
    """Handle account deletion request"""
    
    st.error("⚠️ Account deletion is a permanent action that cannot be undone.")
    st.markdown(
        """
        **What will be deleted:**
        - All conversation history
        - All analysis results
        - User preferences and settings
        - Account information
        
        **This action cannot be reversed.**
        """
    )
    
    if st.text_input("Type 'DELETE' to confirm account deletion") == "DELETE":
        if st.button("🗑️ Permanently Delete Account", type="primary"):
            st.error("Account deletion would be processed here in a real implementation.")
            st.info("For demo purposes, account deletion is not actually performed.")

def show_privacy_policy():
    """Show privacy policy"""
    
    st.markdown(
        create_custom_component(
            """
            <h4>📄 Privacy Policy</h4>
            
            <h5>Data Collection</h5>
            <p>We collect only the data necessary to provide our AI health services, including:</p>
            <ul>
                <li>Messages and conversations for AI processing</li>
                <li>Images uploaded for analysis</li>
                <li>Usage analytics for service improvement</li>
                <li>Account information for authentication</li>
            </ul>
            
            <h5>Data Usage</h5>
            <p>Your data is used to:</p>
            <ul>
                <li>Provide AI-powered health insights</li>
                <li>Improve our AI models and services</li>
                <li>Ensure system security and reliability</li>
                <li>Comply with legal requirements</li>
            </ul>
            
            <h5>Data Protection</h5>
            <p>We protect your data through:</p>
            <ul>
                <li>Encryption in transit and at rest</li>
                <li>Access controls and authentication</li>
                <li>Regular security audits</li>
                <li>Compliance with privacy regulations</li>
            </ul>
            
            <h5>Your Rights</h5>
            <p>You have the right to:</p>
            <ul>
                <li>Access your personal data</li>
                <li>Correct inaccurate information</li>
                <li>Delete your data</li>
                <li>Export your data</li>
                <li>Opt out of data processing</li>
            </ul>
            
            <p><em>Last updated: January 2024</em></p>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )

def show_terms_of_service():
    """Show terms of service"""
    
    st.markdown(
        create_custom_component(
            """
            <h4>📜 Terms of Service</h4>
            
            <h5>Service Description</h5>
            <p>AI WellnessVision provides AI-powered health and wellness analysis tools for informational purposes only.</p>
            
            <h5>Medical Disclaimer</h5>
            <p><strong>Important:</strong> This service is not a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.</p>
            
            <h5>User Responsibilities</h5>
            <p>Users agree to:</p>
            <ul>
                <li>Provide accurate information</li>
                <li>Use the service responsibly</li>
                <li>Not share account credentials</li>
                <li>Respect intellectual property rights</li>
                <li>Comply with applicable laws</li>
            </ul>
            
            <h5>Service Limitations</h5>
            <p>We strive to provide accurate information, but:</p>
            <ul>
                <li>AI predictions may not be 100% accurate</li>
                <li>Service availability is not guaranteed</li>
                <li>Features may change or be discontinued</li>
                <li>Technical issues may occur</li>
            </ul>
            
            <h5>Liability</h5>
            <p>Our liability is limited to the maximum extent permitted by law. We are not responsible for:</p>
            <ul>
                <li>Medical decisions based on our service</li>
                <li>Damages from service interruptions</li>
                <li>Third-party content or services</li>
                <li>Data loss or security breaches</li>
            </ul>
            
            <p><em>Last updated: January 2024</em></p>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )