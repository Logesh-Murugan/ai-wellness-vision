# history_page.py - History and reports page
import streamlit as st
import time
from datetime import datetime, timedelta
import random

def render():
    """Render the history and reports page"""
    
    st.title("📊 History & Reports")
    st.markdown("View your interaction history and generate health reports")
    
    # Initialize session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    
    # Summary metrics
    st.subheader("📈 Activity Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        chat_count = len([msg for msg in st.session_state.chat_messages if msg.get("role") == "user"])
        st.metric("Chat Messages", chat_count)
    
    with col2:
        voice_count = len(st.session_state.voice_history)
        st.metric("Voice Interactions", voice_count)
    
    with col3:
        analysis_count = len(st.session_state.analysis_history)
        st.metric("Image Analyses", analysis_count)
    
    with col4:
        total_interactions = chat_count + voice_count + analysis_count
        st.metric("Total Interactions", total_interactions)
    
    # History tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat History", "🎤 Voice History", "📸 Analysis History", "📋 Reports"])
    
    with tab1:
        render_chat_history()
    
    with tab2:
        render_voice_history()
    
    with tab3:
        render_analysis_history()
    
    with tab4:
        render_reports()

def render_chat_history():
    """Render chat conversation history"""
    
    st.subheader("💬 Chat Conversations")
    
    if not st.session_state.chat_messages:
        st.info("No chat history available. Start a conversation in the Chat Assistant page!")
        return
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        show_count = st.selectbox("Show last", [10, 25, 50, 100], index=0)
    
    with col_filter2:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = []
            st.rerun()
    
    # Display chat messages
    messages = st.session_state.chat_messages[-show_count:]
    
    for i, message in enumerate(messages):
        if message["role"] == "user":
            st.markdown(f"**👤 You:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**🤖 AI:** {message['content']}")
        
        if i < len(messages) - 1:
            st.markdown("---")

def render_voice_history():
    """Render voice interaction history"""
    
    st.subheader("🎤 Voice Interactions")
    
    if not st.session_state.voice_history:
        st.info("No voice history available. Try the Voice Interaction page!")
        return
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        show_count = st.selectbox("Show last", [5, 10, 20], index=0, key="voice_count")
    
    with col_filter2:
        if st.button("🗑️ Clear Voice History"):
            st.session_state.voice_history = []
            st.rerun()
    
    # Display voice interactions
    interactions = st.session_state.voice_history[-show_count:]
    
    for i, interaction in enumerate(reversed(interactions), 1):
        with st.expander(f"🎤 Voice Interaction {len(interactions) - i + 1} - {interaction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
            st.markdown(f"**🎤 You said:** {interaction['user_message']}")
            st.markdown(f"**🤖 AI responded:** {interaction['ai_response']}")
            st.markdown(f"**Language:** {interaction['language']} | **Voice Type:** {interaction['voice_type']}")

def render_analysis_history():
    """Render image analysis history"""
    
    st.subheader("📸 Image Analysis History")
    
    if not st.session_state.analysis_history:
        st.info("No analysis history available. Try uploading an image in the Image Analysis page!")
        
        # Show sample analysis for demonstration
        st.markdown("### 📋 Sample Analysis Results")
        
        sample_analyses = [
            {
                "timestamp": datetime.now() - timedelta(hours=2),
                "type": "Skin Condition Detection",
                "result": "Healthy Skin",
                "confidence": 0.87,
                "recommendations": ["Continue current skincare routine", "Use sunscreen daily"]
            },
            {
                "timestamp": datetime.now() - timedelta(days=1),
                "type": "Food Recognition",
                "result": "Apple",
                "confidence": 0.94,
                "recommendations": ["Great choice for healthy snacking", "Rich in fiber and vitamins"]
            }
        ]
        
        for analysis in sample_analyses:
            with st.expander(f"📊 {analysis['type']} - {analysis['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Result", analysis['result'])
                    st.metric("Confidence", f"{analysis['confidence']:.1%}")
                
                with col2:
                    st.markdown("**Recommendations:**")
                    for rec in analysis['recommendations']:
                        st.write(f"• {rec}")
        
        return
    
    # Display actual analysis history
    for i, analysis in enumerate(reversed(st.session_state.analysis_history), 1):
        with st.expander(f"📊 Analysis {i} - {analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
            st.markdown(f"**Type:** {analysis['type']}")
            st.markdown(f"**Result:** {analysis['result']}")
            st.markdown(f"**Confidence:** {analysis.get('confidence', 'N/A')}")

def render_reports():
    """Render health reports section"""
    
    st.subheader("📋 Health Reports")
    
    # Report generation options
    col_report1, col_report2 = st.columns(2)
    
    with col_report1:
        report_type = st.selectbox(
            "Report Type",
            ["Weekly Summary", "Monthly Overview", "Activity Analysis", "Health Insights"]
        )
    
    with col_report2:
        date_range = st.selectbox(
            "Time Period",
            ["Last 7 days", "Last 30 days", "Last 3 months", "All time"]
        )
    
    if st.button("📊 Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            time.sleep(2)  # Simulate report generation
            
            generate_sample_report(report_type, date_range)

def generate_sample_report(report_type, date_range):
    """Generate a sample health report"""
    
    st.success("✅ Report generated successfully!")
    
    # Report header
    st.markdown(f"## 📋 {report_type} - {date_range}")
    st.markdown(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sample report content based on type
    if report_type == "Weekly Summary":
        st.markdown("""
        ### 📊 Weekly Activity Summary
        
        **Interaction Overview:**
        - Total conversations: 12
        - Voice interactions: 5
        - Image analyses: 3
        - Most active day: Wednesday
        
        **Health Topics Discussed:**
        - Sleep improvement (3 conversations)
        - Nutrition advice (4 conversations)
        - Exercise guidance (2 conversations)
        - Stress management (3 conversations)
        
        **Key Insights:**
        - You're most active in health discussions during midweek
        - Sleep and nutrition are your primary concerns
        - Voice interactions show 85% satisfaction rate
        """)
    
    elif report_type == "Monthly Overview":
        st.markdown("""
        ### 📈 Monthly Health Overview
        
        **Activity Trends:**
        - 45 total interactions this month
        - 20% increase from last month
        - Average 1.5 interactions per day
        
        **Health Focus Areas:**
        - Physical wellness: 60%
        - Mental health: 25%
        - Nutrition: 15%
        
        **Progress Indicators:**
        - Consistent engagement with health topics
        - Improved question specificity over time
        - Regular use of multiple interaction modes
        """)
    
    elif report_type == "Activity Analysis":
        st.markdown("""
        ### 🔍 Activity Analysis
        
        **Usage Patterns:**
        - Peak usage: 2-4 PM and 8-10 PM
        - Preferred interaction: Text chat (60%)
        - Voice usage increasing by 15% weekly
        
        **Content Analysis:**
        - Most common queries: Symptom checking
        - Average conversation length: 3.2 exchanges
        - Response satisfaction: 4.2/5.0
        
        **Recommendations:**
        - Continue regular health check-ins
        - Explore voice features for hands-free use
        - Consider setting daily health reminders
        """)
    
    else:  # Health Insights
        st.markdown("""
        ### 💡 Health Insights
        
        **Behavioral Patterns:**
        - Consistent interest in preventive health
        - Proactive approach to wellness
        - Good engagement with AI recommendations
        
        **Health Journey:**
        - Started with basic questions
        - Progressed to specific health concerns
        - Now seeking comprehensive wellness advice
        
        **Personalized Recommendations:**
        - Continue current health monitoring habits
        - Consider scheduling regular health checkups
        - Explore stress management techniques
        - Maintain balanced nutrition focus
        """)
    
    # Download report option
    st.markdown("---")
    
    report_content = f"""
    {report_type} - {date_range}
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    This is a sample health report from AI WellnessVision.
    In a real implementation, this would contain your actual health interaction data.
    """
    
    st.download_button(
        label="📄 Download Report (TXT)",
        data=report_content,
        file_name=f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
    
    # Disclaimer
    st.warning("⚠️ **Note:** This is a sample report for demonstration purposes. Actual reports would be based on your real interaction data and should not be used for medical decision-making without consulting healthcare professionals.")