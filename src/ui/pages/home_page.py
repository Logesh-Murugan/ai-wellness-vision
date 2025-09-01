# home_page.py - Home page for AI WellnessVision
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from ui.utils.session_manager import SessionManager
from ui.utils.theme_config import create_custom_component, format_confidence_score

def render():
    """Render the home page"""
    
    session_manager = SessionManager()
    user_info = session_manager.get_user_info()
    user_stats = session_manager.get_user_stats()
    
    # Welcome header
    st.markdown(
        f"""
        <div class="main-header">
            <h1>Welcome back, {user_info.get('username', 'User')}! 👋</h1>
            <p>Your AI-powered health and wellness dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Quick stats overview
    st.subheader("📊 Your Activity Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Analyses",
            value=user_stats['total_analyses'],
            delta=f"+{user_stats['total_analyses']} this session"
        )
    
    with col2:
        st.metric(
            label="Chat Messages",
            value=user_stats['total_chats'],
            delta=f"+{user_stats['total_chats']} this session"
        )
    
    with col3:
        st.metric(
            label="Voice Interactions",
            value=user_stats['total_voice_interactions'],
            delta=f"+{user_stats['total_voice_interactions']} this session"
        )
    
    with col4:
        st.metric(
            label="Total Conversations",
            value=user_stats['total_conversations'],
            delta=f"+{user_stats['total_conversations']} this session"
        )
    
    # Recent activity and quick actions
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🕒 Recent Activity")
        
        # Get recent conversations and analyses
        recent_conversations = session_manager.get_conversation_history(limit=5)
        recent_analyses = session_manager.get_analysis_history(limit=5)
        
        if recent_conversations or recent_analyses:
            # Combine and sort by timestamp
            all_activities = []
            
            for conv in recent_conversations:
                all_activities.append({
                    'timestamp': conv['timestamp'],
                    'type': 'Chat',
                    'description': conv['user_message'][:50] + "..." if len(conv['user_message']) > 50 else conv['user_message'],
                    'icon': '💬'
                })
            
            for analysis in recent_analyses:
                all_activities.append({
                    'timestamp': analysis['timestamp'],
                    'type': 'Analysis',
                    'description': f"{analysis['analysis_type'].replace('_', ' ').title()} Analysis",
                    'icon': '🔍'
                })
            
            # Sort by timestamp (most recent first)
            all_activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Display recent activities
            for activity in all_activities[:8]:  # Show last 8 activities
                time_ago = datetime.now() - activity['timestamp']
                if time_ago.days > 0:
                    time_str = f"{time_ago.days} days ago"
                elif time_ago.seconds > 3600:
                    time_str = f"{time_ago.seconds // 3600} hours ago"
                elif time_ago.seconds > 60:
                    time_str = f"{time_ago.seconds // 60} minutes ago"
                else:
                    time_str = "Just now"
                
                st.markdown(
                    create_custom_component(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2em; margin-right: 0.5rem;">{activity['icon']}</span>
                            <div>
                                <strong>{activity['type']}</strong><br>
                                <small style="color: #666;">{activity['description']}</small><br>
                                <small style="color: #999;">{time_str}</small>
                            </div>
                        </div>
                        """,
                        "card"
                    ),
                    unsafe_allow_html=True
                )
        else:
            st.info("No recent activity. Start by uploading an image or chatting with the AI assistant!")
    
    with col_right:
        st.subheader("🚀 Quick Actions")
        
        # Quick action buttons
        if st.button("📷 Analyze Image", use_container_width=True):
            st.switch_page("pages/image_analysis.py")
        
        if st.button("💬 Start Chat", use_container_width=True):
            st.switch_page("pages/chat_interface.py")
        
        if st.button("🎤 Voice Interaction", use_container_width=True):
            st.switch_page("pages/voice_interaction.py")
        
        if st.button("📊 View History", use_container_width=True):
            st.switch_page("pages/history.py")
        
        st.markdown("---")
        
        # System status
        st.subheader("🔧 System Status")
        
        # Mock system status (in real implementation, this would check actual services)
        services_status = {
            "Image Analysis": "🟢 Online",
            "NLP Service": "🟢 Online", 
            "Speech Service": "🟢 Online",
            "Explainable AI": "🟢 Online"
        }
        
        for service, status in services_status.items():
            st.markdown(f"**{service}:** {status}")
    
    # Usage analytics (if user has data)
    if user_stats['total_conversations'] > 0 or user_stats['total_analyses'] > 0:
        st.subheader("📈 Usage Analytics")
        
        # Create sample data for visualization
        dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
        
        # Mock data based on current session (in real app, this would be from database)
        daily_chats = [0, 0, 0, 0, 0, 0, user_stats['total_chats']]
        daily_analyses = [0, 0, 0, 0, 0, 0, user_stats['total_analyses']]
        
        df = pd.DataFrame({
            'Date': dates,
            'Chats': daily_chats,
            'Analyses': daily_analyses
        })
        
        # Create charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_line = px.line(
                df, 
                x='Date', 
                y=['Chats', 'Analyses'],
                title='Daily Activity Trend',
                color_discrete_map={'Chats': '#1f77b4', 'Analyses': '#ff7f0e'}
            )
            fig_line.update_layout(height=300)
            st.plotly_chart(fig_line, use_container_width=True)
        
        with col_chart2:
            # Pie chart of activity types
            activity_data = {
                'Activity Type': ['Chats', 'Analyses', 'Voice Interactions'],
                'Count': [
                    user_stats['total_chats'],
                    user_stats['total_analyses'], 
                    user_stats['total_voice_interactions']
                ]
            }
            
            fig_pie = px.pie(
                values=activity_data['Count'],
                names=activity_data['Activity Type'],
                title='Activity Distribution'
            )
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Health tips and information
    st.subheader("💡 Daily Health Tips")
    
    health_tips = [
        "🥤 Stay hydrated! Aim for 8 glasses of water daily.",
        "🚶‍♀️ Take regular breaks to walk and stretch, especially if you work at a desk.",
        "😴 Maintain a consistent sleep schedule for better health.",
        "🥗 Include colorful fruits and vegetables in your meals.",
        "🧘‍♂️ Practice mindfulness or meditation for mental well-being.",
        "☀️ Get some sunlight exposure for vitamin D.",
        "🤝 Stay connected with friends and family for emotional health."
    ]
    
    import random
    daily_tip = random.choice(health_tips)
    
    st.info(daily_tip)
    
    # Disclaimer
    st.markdown("---")
    st.markdown(
        create_custom_component(
            """
            <div style='text-align: center;'>
                <strong>⚠️ Medical Disclaimer</strong><br>
                This platform provides general health information and is not intended to replace 
                professional medical advice, diagnosis, or treatment. Always consult with qualified 
                healthcare providers for medical concerns.
            </div>
            """,
            "alert-warning"
        ),
        unsafe_allow_html=True
    )