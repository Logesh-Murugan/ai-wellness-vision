# history_page.py - History and reports page
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from ui.utils.session_manager import SessionManager
from ui.utils.theme_config import create_custom_component, format_confidence_score

def render():
    """Render the history and reports page"""
    
    st.title("📊 History & Reports")
    st.markdown("View your conversation history, analysis results, and generate comprehensive reports")
    
    session_manager = SessionManager()
    
    # History navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Conversations", 
        "🔍 Analyses", 
        "📈 Analytics", 
        "📄 Reports"
    ])
    
    with tab1:
        render_conversation_history(session_manager)
    
    with tab2:
        render_analysis_history(session_manager)
    
    with tab3:
        render_analytics_dashboard(session_manager)
    
    with tab4:
        render_reports_section(session_manager)

def render_conversation_history(session_manager):
    """Render conversation history section"""
    
    st.markdown("### 💬 Conversation History")
    
    conversations = session_manager.get_conversation_history()
    
    if not conversations:
        st.info("No conversations yet. Start chatting with the AI assistant to see your history here!")
        return
    
    # Conversation filters
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        message_type_filter = st.selectbox(
            "Message Type",
            options=["all", "text", "voice"],
            format_func=lambda x: {
                "all": "📝 All Messages",
                "text": "📝 Text Only",
                "voice": "🎤 Voice Only"
            }[x]
        )
    
    with col_filter2:
        date_filter = st.selectbox(
            "Time Period",
            options=["all", "today", "week", "month"],
            format_func=lambda x: {
                "all": "🗓️ All Time",
                "today": "📅 Today",
                "week": "📅 This Week", 
                "month": "📅 This Month"
            }[x]
        )
    
    with col_filter3:
        search_term = st.text_input(
            "Search Conversations",
            placeholder="Search in messages...",
            help="Search for specific topics or keywords"
        )
    
    # Filter conversations
    filtered_conversations = filter_conversations(
        conversations, message_type_filter, date_filter, search_term
    )
    
    if not filtered_conversations:
        st.warning("No conversations match your filters.")
        return
    
    # Display conversations
    st.markdown(f"**Found {len(filtered_conversations)} conversations**")
    
    for i, conv in enumerate(reversed(filtered_conversations)):
        with st.expander(
            f"💬 {conv['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
            f"{conv['user_message'][:50]}{'...' if len(conv['user_message']) > 50 else ''}",
            expanded=i < 3  # Expand first 3
        ):
            
            col_conv1, col_conv2 = st.columns([4, 1])
            
            with col_conv1:
                # User message
                st.markdown(
                    create_custom_component(
                        f"""
                        <div style="margin-bottom: 1rem;">
                            <strong>👤 You:</strong><br>
                            {conv['user_message']}
                        </div>
                        """,
                        "card"
                    ),
                    unsafe_allow_html=True
                )
                
                # AI response
                st.markdown(
                    create_custom_component(
                        f"""
                        <div>
                            <strong>🤖 AI Assistant:</strong><br>
                            {conv['ai_response']}
                        </div>
                        """,
                        "card"
                    ),
                    unsafe_allow_html=True
                )
            
            with col_conv2:
                # Conversation metadata
                st.markdown("**📊 Details:**")
                st.caption(f"🕒 {conv['timestamp'].strftime('%H:%M:%S')}")
                st.caption(f"📝 {conv.get('message_type', 'text').title()}")
                
                metadata = conv.get('metadata', {})
                if metadata:
                    if 'language' in metadata:
                        st.caption(f"🌐 {metadata['language'].upper()}")
                    if 'confidence' in metadata:
                        st.caption(f"🎯 {metadata['confidence']:.1%} confidence")
                    if 'sentiment' in metadata:
                        sentiment = metadata['sentiment']
                        if isinstance(sentiment, dict):
                            sentiment_text = sentiment.get('sentiment', 'neutral')
                            st.caption(f"😊 {sentiment_text.title()}")
                
                # Action buttons
                if st.button(f"🔄 Continue", key=f"continue_{i}"):
                    # Navigate to chat with this context
                    st.switch_page("pages/chat_interface.py")
                
                if st.button(f"📤 Export", key=f"export_conv_{i}"):
                    export_single_conversation(conv)

def render_analysis_history(session_manager):
    """Render analysis history section"""
    
    st.markdown("### 🔍 Analysis History")
    
    analyses = session_manager.get_analysis_history()
    
    if not analyses:
        st.info("No analyses yet. Upload an image for analysis to see your history here!")
        return
    
    # Analysis filters
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        analysis_type_filter = st.selectbox(
            "Analysis Type",
            options=["all", "skin_condition", "eye_health", "food_recognition", "emotion_detection"],
            format_func=lambda x: {
                "all": "🔍 All Analyses",
                "skin_condition": "🔍 Skin Condition",
                "eye_health": "👁️ Eye Health",
                "food_recognition": "🍎 Food Recognition",
                "emotion_detection": "😊 Emotion Detection"
            }[x]
        )
    
    with col_filter2:
        confidence_filter = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            help="Filter analyses by minimum confidence score"
        )
    
    # Filter analyses
    filtered_analyses = [
        analysis for analysis in analyses
        if (analysis_type_filter == "all" or analysis['analysis_type'] == analysis_type_filter)
        and analysis['result'].get('confidence', 0) >= confidence_filter
    ]
    
    if not filtered_analyses:
        st.warning("No analyses match your filters.")
        return
    
    # Display analyses
    st.markdown(f"**Found {len(filtered_analyses)} analyses**")
    
    for i, analysis in enumerate(reversed(filtered_analyses)):
        result = analysis['result']
        
        with st.expander(
            f"🔍 {analysis['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
            f"{analysis['analysis_type'].replace('_', ' ').title()}",
            expanded=i < 2  # Expand first 2
        ):
            
            col_analysis1, col_analysis2 = st.columns([3, 1])
            
            with col_analysis1:
                # Analysis details
                st.markdown(f"**Analysis Type:** {analysis['analysis_type'].replace('_', ' ').title()}")
                st.markdown(f"**Overall Confidence:** {format_confidence_score(result.get('confidence', 0))}", unsafe_allow_html=True)
                
                # Predictions
                predictions = result.get('predictions', [])
                if predictions:
                    st.markdown("**🎯 Top Predictions:**")
                    
                    for j, pred in enumerate(predictions[:3]):  # Show top 3
                        confidence = pred.get('confidence', 0)
                        label = pred.get('label', 'Unknown')
                        description = pred.get('description', 'No description')
                        
                        st.markdown(
                            f"**{j+1}.** {label} ({format_confidence_score(confidence)})",
                            unsafe_allow_html=True
                        )
                        st.caption(description)
                
                # Additional info based on analysis type
                if analysis['analysis_type'] == 'skin_condition':
                    if predictions and 'severity' in predictions[0]:
                        st.markdown(f"**Severity:** {predictions[0]['severity']}")
                
                elif analysis['analysis_type'] == 'food_recognition':
                    if predictions and 'nutrition' in predictions[0]:
                        nutrition = predictions[0]['nutrition']
                        st.markdown("**Nutrition Info:**")
                        for key, value in nutrition.items():
                            st.caption(f"• {key.title()}: {value}")
            
            with col_analysis2:
                # Analysis metadata
                st.markdown("**📊 Details:**")
                st.caption(f"🕒 {analysis['timestamp'].strftime('%H:%M:%S')}")
                st.caption(f"🆔 {analysis['id'][:8]}...")
                
                if analysis.get('image_path'):
                    st.caption("🖼️ Image available")
                
                # Action buttons
                if st.button(f"🔍 View Details", key=f"details_{i}"):
                    show_analysis_details(analysis)
                
                if st.button(f"📤 Export", key=f"export_analysis_{i}"):
                    export_single_analysis(analysis)
                
                if st.button(f"🔄 Re-analyze", key=f"reanalyze_{i}"):
                    st.info("Navigate to Image Analysis to upload a new image")

def render_analytics_dashboard(session_manager):
    """Render analytics dashboard"""
    
    st.markdown("### 📈 Analytics Dashboard")
    
    conversations = session_manager.get_conversation_history()
    analyses = session_manager.get_analysis_history()
    
    if not conversations and not analyses:
        st.info("No data available for analytics. Start using the platform to see insights here!")
        return
    
    # Overview metrics
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    with col_metric1:
        st.metric("Total Conversations", len(conversations))
    
    with col_metric2:
        st.metric("Total Analyses", len(analyses))
    
    with col_metric3:
        voice_count = len([c for c in conversations if c.get('message_type') == 'voice'])
        st.metric("Voice Interactions", voice_count)
    
    with col_metric4:
        if analyses:
            avg_confidence = sum(a['result'].get('confidence', 0) for a in analyses) / len(analyses)
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        else:
            st.metric("Avg Confidence", "N/A")
    
    # Charts
    if conversations or analyses:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Activity over time
            if conversations:
                # Create daily activity data
                dates = [c['timestamp'].date() for c in conversations]
                date_counts = {}
                for date in dates:
                    date_counts[date] = date_counts.get(date, 0) + 1
                
                if date_counts:
                    df_activity = pd.DataFrame([
                        {'Date': date, 'Conversations': count}
                        for date, count in date_counts.items()
                    ])
                    
                    fig_activity = px.line(
                        df_activity,
                        x='Date',
                        y='Conversations',
                        title='Daily Conversation Activity',
                        markers=True
                    )
                    fig_activity.update_layout(height=300)
                    st.plotly_chart(fig_activity, use_container_width=True)
        
        with col_chart2:
            # Message type distribution
            if conversations:
                message_types = [c.get('message_type', 'text') for c in conversations]
                type_counts = {}
                for msg_type in message_types:
                    type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
                
                fig_types = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys()),
                    title='Message Type Distribution'
                )
                fig_types.update_layout(height=300)
                st.plotly_chart(fig_types, use_container_width=True)
        
        # Analysis type distribution
        if analyses:
            st.markdown("#### 🔍 Analysis Distribution")
            
            analysis_types = [a['analysis_type'] for a in analyses]
            type_counts = {}
            for analysis_type in analysis_types:
                display_name = analysis_type.replace('_', ' ').title()
                type_counts[display_name] = type_counts.get(display_name, 0) + 1
            
            fig_analysis = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title='Analysis Types Used',
                labels={'x': 'Analysis Type', 'y': 'Count'}
            )
            fig_analysis.update_layout(height=400)
            st.plotly_chart(fig_analysis, use_container_width=True)
        
        # Confidence score distribution
        if analyses:
            st.markdown("#### 🎯 Confidence Score Distribution")
            
            confidences = [a['result'].get('confidence', 0) for a in analyses]
            
            fig_confidence = px.histogram(
                x=confidences,
                nbins=10,
                title='Analysis Confidence Scores',
                labels={'x': 'Confidence Score', 'y': 'Count'}
            )
            fig_confidence.update_layout(height=400)
            st.plotly_chart(fig_confidence, use_container_width=True)

def render_reports_section(session_manager):
    """Render reports generation section"""
    
    st.markdown("### 📄 Generate Reports")
    
    conversations = session_manager.get_conversation_history()
    analyses = session_manager.get_analysis_history()
    
    if not conversations and not analyses:
        st.info("No data available for reports. Start using the platform to generate reports!")
        return
    
    # Report configuration
    col_report1, col_report2 = st.columns(2)
    
    with col_report1:
        report_type = st.selectbox(
            "Report Type",
            options=["comprehensive", "conversations", "analyses", "summary"],
            format_func=lambda x: {
                "comprehensive": "📊 Comprehensive Report",
                "conversations": "💬 Conversations Report",
                "analyses": "🔍 Analyses Report",
                "summary": "📋 Summary Report"
            }[x]
        )
    
    with col_report2:
        report_format = st.selectbox(
            "Format",
            options=["json", "csv", "txt"],
            format_func=lambda x: {
                "json": "📄 JSON",
                "csv": "📊 CSV",
                "txt": "📝 Text"
            }[x]
        )
    
    # Report options
    with st.expander("📋 Report Options"):
        include_metadata = st.checkbox("Include Metadata", value=True)
        include_timestamps = st.checkbox("Include Timestamps", value=True)
        include_confidence = st.checkbox("Include Confidence Scores", value=True)
        anonymize_data = st.checkbox("Anonymize Personal Data", value=False)
    
    # Generate report
    if st.button("📄 Generate Report", type="primary"):
        generate_report(
            session_manager,
            report_type,
            report_format,
            {
                'include_metadata': include_metadata,
                'include_timestamps': include_timestamps,
                'include_confidence': include_confidence,
                'anonymize_data': anonymize_data
            }
        )
    
    # Quick export buttons
    st.markdown("---")
    st.markdown("#### ⚡ Quick Exports")
    
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        if st.button("💬 Export All Chats", use_container_width=True):
            export_all_conversations(session_manager)
    
    with col_export2:
        if st.button("🔍 Export All Analyses", use_container_width=True):
            export_all_analyses(session_manager)
    
    with col_export3:
        if st.button("📊 Export Analytics", use_container_width=True):
            export_analytics_data(session_manager)

def filter_conversations(conversations, message_type_filter, date_filter, search_term):
    """Filter conversations based on criteria"""
    
    filtered = conversations
    
    # Filter by message type
    if message_type_filter != "all":
        filtered = [c for c in filtered if c.get('message_type', 'text') == message_type_filter]
    
    # Filter by date
    if date_filter != "all":
        now = datetime.now()
        if date_filter == "today":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "week":
            cutoff = now - timedelta(days=7)
        elif date_filter == "month":
            cutoff = now - timedelta(days=30)
        
        filtered = [c for c in filtered if c['timestamp'] >= cutoff]
    
    # Filter by search term
    if search_term:
        search_lower = search_term.lower()
        filtered = [
            c for c in filtered
            if search_lower in c['user_message'].lower() or search_lower in c['ai_response'].lower()
        ]
    
    return filtered

def show_analysis_details(analysis):
    """Show detailed analysis information"""
    
    st.markdown(
        create_custom_component(
            f"""
            <h4>🔍 Analysis Details</h4>
            <p><strong>ID:</strong> {analysis['id']}</p>
            <p><strong>Type:</strong> {analysis['analysis_type'].replace('_', ' ').title()}</p>
            <p><strong>Timestamp:</strong> {analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Confidence:</strong> {analysis['result'].get('confidence', 0):.1%}</p>
            """,
            "card"
        ),
        unsafe_allow_html=True
    )

def export_single_conversation(conversation):
    """Export a single conversation"""
    
    export_data = {
        'conversation_id': conversation.get('id', 'unknown'),
        'timestamp': conversation['timestamp'].isoformat(),
        'user_message': conversation['user_message'],
        'ai_response': conversation['ai_response'],
        'message_type': conversation.get('message_type', 'text'),
        'metadata': conversation.get('metadata', {})
    }
    
    export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📄 Download Conversation",
        data=export_json,
        file_name=f"conversation_{int(conversation['timestamp'].timestamp())}.json",
        mime="application/json"
    )

def export_single_analysis(analysis):
    """Export a single analysis"""
    
    export_data = {
        'analysis_id': analysis['id'],
        'timestamp': analysis['timestamp'].isoformat(),
        'analysis_type': analysis['analysis_type'],
        'result': analysis['result'],
        'image_path': analysis.get('image_path')
    }
    
    export_json = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
    
    st.download_button(
        label="📄 Download Analysis",
        data=export_json,
        file_name=f"analysis_{analysis['analysis_type']}_{int(analysis['timestamp'].timestamp())}.json",
        mime="application/json"
    )

def generate_report(session_manager, report_type, report_format, options):
    """Generate comprehensive report"""
    
    conversations = session_manager.get_conversation_history()
    analyses = session_manager.get_analysis_history()
    
    # Prepare report data
    report_data = {
        'report_type': report_type,
        'generated_at': datetime.now().isoformat(),
        'user_info': session_manager.get_user_info() if not options['anonymize_data'] else {'username': 'anonymous'},
        'summary': {
            'total_conversations': len(conversations),
            'total_analyses': len(analyses),
            'date_range': {
                'start': min([c['timestamp'] for c in conversations + analyses]).isoformat() if conversations or analyses else None,
                'end': max([c['timestamp'] for c in conversations + analyses]).isoformat() if conversations or analyses else None
            }
        }
    }
    
    # Add data based on report type
    if report_type in ['comprehensive', 'conversations']:
        report_data['conversations'] = []
        for conv in conversations:
            conv_data = {
                'user_message': conv['user_message'],
                'ai_response': conv['ai_response'],
                'message_type': conv.get('message_type', 'text')
            }
            
            if options['include_timestamps']:
                conv_data['timestamp'] = conv['timestamp'].isoformat()
            
            if options['include_metadata']:
                conv_data['metadata'] = conv.get('metadata', {})
            
            report_data['conversations'].append(conv_data)
    
    if report_type in ['comprehensive', 'analyses']:
        report_data['analyses'] = []
        for analysis in analyses:
            analysis_data = {
                'analysis_type': analysis['analysis_type'],
                'result': analysis['result']
            }
            
            if options['include_timestamps']:
                analysis_data['timestamp'] = analysis['timestamp'].isoformat()
            
            if not options['include_confidence']:
                if 'confidence' in analysis_data['result']:
                    del analysis_data['result']['confidence']
            
            report_data['analyses'].append(analysis_data)
    
    # Generate file based on format
    if report_format == 'json':
        file_data = json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
        mime_type = "application/json"
        file_extension = "json"
    
    elif report_format == 'csv':
        # Convert to CSV format (simplified)
        import io
        output = io.StringIO()
        
        if report_type in ['comprehensive', 'conversations'] and conversations:
            output.write("Conversation Data\n")
            output.write("Timestamp,Message Type,User Message,AI Response\n")
            for conv in conversations:
                timestamp = conv['timestamp'].isoformat() if options['include_timestamps'] else ''
                output.write(f'"{timestamp}","{conv.get("message_type", "text")}","{conv["user_message"]}","{conv["ai_response"]}"\n')
        
        if report_type in ['comprehensive', 'analyses'] and analyses:
            output.write("\nAnalysis Data\n")
            output.write("Timestamp,Analysis Type,Confidence,Predictions\n")
            for analysis in analyses:
                timestamp = analysis['timestamp'].isoformat() if options['include_timestamps'] else ''
                confidence = analysis['result'].get('confidence', 0) if options['include_confidence'] else ''
                predictions = str(analysis['result'].get('predictions', []))
                output.write(f'"{timestamp}","{analysis["analysis_type"]}","{confidence}","{predictions}"\n')
        
        file_data = output.getvalue()
        mime_type = "text/csv"
        file_extension = "csv"
    
    else:  # txt format
        file_data = f"AI WellnessVision Report\n"
        file_data += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        file_data += f"Report Type: {report_type.title()}\n"
        file_data += "=" * 50 + "\n\n"
        
        if report_type in ['comprehensive', 'conversations'] and conversations:
            file_data += "CONVERSATIONS\n" + "-" * 20 + "\n"
            for i, conv in enumerate(conversations, 1):
                if options['include_timestamps']:
                    file_data += f"[{conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}]\n"
                file_data += f"User: {conv['user_message']}\n"
                file_data += f"AI: {conv['ai_response']}\n\n"
        
        if report_type in ['comprehensive', 'analyses'] and analyses:
            file_data += "ANALYSES\n" + "-" * 20 + "\n"
            for i, analysis in enumerate(analyses, 1):
                if options['include_timestamps']:
                    file_data += f"[{analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}]\n"
                file_data += f"Type: {analysis['analysis_type'].replace('_', ' ').title()}\n"
                if options['include_confidence']:
                    file_data += f"Confidence: {analysis['result'].get('confidence', 0):.1%}\n"
                file_data += f"Predictions: {len(analysis['result'].get('predictions', []))}\n\n"
        
        mime_type = "text/plain"
        file_extension = "txt"
    
    # Offer download
    st.download_button(
        label=f"📄 Download {report_type.title()} Report ({file_extension.upper()})",
        data=file_data,
        file_name=f"wellness_report_{report_type}_{int(datetime.now().timestamp())}.{file_extension}",
        mime=mime_type
    )
    
    st.success(f"✅ {report_type.title()} report generated successfully!")

def export_all_conversations(session_manager):
    """Export all conversations"""
    
    conversations = session_manager.get_conversation_history()
    
    if not conversations:
        st.info("No conversations to export.")
        return
    
    export_data = {
        'export_timestamp': datetime.now().isoformat(),
        'total_conversations': len(conversations),
        'conversations': [
            {
                'timestamp': conv['timestamp'].isoformat(),
                'user_message': conv['user_message'],
                'ai_response': conv['ai_response'],
                'message_type': conv.get('message_type', 'text'),
                'metadata': conv.get('metadata', {})
            }
            for conv in conversations
        ]
    }
    
    export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="💬 Download All Conversations",
        data=export_json,
        file_name=f"all_conversations_{int(datetime.now().timestamp())}.json",
        mime="application/json"
    )

def export_all_analyses(session_manager):
    """Export all analyses"""
    
    analyses = session_manager.get_analysis_history()
    
    if not analyses:
        st.info("No analyses to export.")
        return
    
    export_data = {
        'export_timestamp': datetime.now().isoformat(),
        'total_analyses': len(analyses),
        'analyses': [
            {
                'timestamp': analysis['timestamp'].isoformat(),
                'analysis_type': analysis['analysis_type'],
                'result': analysis['result'],
                'image_path': analysis.get('image_path')
            }
            for analysis in analyses
        ]
    }
    
    export_json = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
    
    st.download_button(
        label="🔍 Download All Analyses",
        data=export_json,
        file_name=f"all_analyses_{int(datetime.now().timestamp())}.json",
        mime="application/json"
    )

def export_analytics_data(session_manager):
    """Export analytics data"""
    
    conversations = session_manager.get_conversation_history()
    analyses = session_manager.get_analysis_history()
    stats = session_manager.get_user_stats()
    
    analytics_data = {
        'export_timestamp': datetime.now().isoformat(),
        'user_statistics': stats,
        'conversation_analytics': {
            'total_conversations': len(conversations),
            'message_types': {},
            'daily_activity': {},
            'languages_used': {}
        },
        'analysis_analytics': {
            'total_analyses': len(analyses),
            'analysis_types': {},
            'confidence_distribution': {},
            'success_rate': 0
        }
    }
    
    # Conversation analytics
    for conv in conversations:
        msg_type = conv.get('message_type', 'text')
        analytics_data['conversation_analytics']['message_types'][msg_type] = \
            analytics_data['conversation_analytics']['message_types'].get(msg_type, 0) + 1
        
        date_str = conv['timestamp'].date().isoformat()
        analytics_data['conversation_analytics']['daily_activity'][date_str] = \
            analytics_data['conversation_analytics']['daily_activity'].get(date_str, 0) + 1
        
        metadata = conv.get('metadata', {})
        if 'language' in metadata:
            lang = metadata['language']
            analytics_data['conversation_analytics']['languages_used'][lang] = \
                analytics_data['conversation_analytics']['languages_used'].get(lang, 0) + 1
    
    # Analysis analytics
    for analysis in analyses:
        analysis_type = analysis['analysis_type']
        analytics_data['analysis_analytics']['analysis_types'][analysis_type] = \
            analytics_data['analysis_analytics']['analysis_types'].get(analysis_type, 0) + 1
        
        confidence = analysis['result'].get('confidence', 0)
        confidence_bucket = f"{int(confidence * 10) * 10}-{int(confidence * 10) * 10 + 10}%"
        analytics_data['analysis_analytics']['confidence_distribution'][confidence_bucket] = \
            analytics_data['analysis_analytics']['confidence_distribution'].get(confidence_bucket, 0) + 1
    
    export_json = json.dumps(analytics_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📊 Download Analytics Data",
        data=export_json,
        file_name=f"analytics_data_{int(datetime.now().timestamp())}.json",
        mime="application/json"
    )