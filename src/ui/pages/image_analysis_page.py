# image_analysis_page.py - Image analysis interface
import streamlit as st
import io
import time
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from ui.utils.session_manager import SessionManager
from ui.utils.theme_config import create_custom_component, format_confidence_score

def render():
    """Render the image analysis page"""
    
    st.title("📷 AI Image Analysis")
    st.markdown("Upload an image for AI-powered health and wellness analysis")
    
    session_manager = SessionManager()
    
    # Analysis type selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_type = st.selectbox(
            "Select Analysis Type",
            options=[
                "skin_condition",
                "eye_health", 
                "food_recognition",
                "emotion_detection"
            ],
            format_func=lambda x: {
                "skin_condition": "🔍 Skin Condition Analysis",
                "eye_health": "👁️ Eye Health Assessment", 
                "food_recognition": "🍎 Food Recognition & Nutrition",
                "emotion_detection": "😊 Emotion Detection"
            }[x],
            help="Choose the type of analysis you want to perform"
        )
    
    with col2:
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
            help="Select your preferred language for results"
        )
    
    # File upload with drag and drop
    st.markdown("### 📤 Upload Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
        help="Supported formats: PNG, JPG, JPEG, WebP, BMP (Max size: 10MB)",
        label_visibility="collapsed"
    )
    
    # Alternative: Camera input
    camera_image = st.camera_input(
        "Or take a photo with your camera",
        help="Use your device camera to capture an image"
    )
    
    # Use camera image if available, otherwise uploaded file
    image_source = camera_image if camera_image else uploaded_file
    
    if image_source:
        # Display uploaded image
        col_img, col_info = st.columns([2, 1])
        
        with col_img:
            try:
                image = Image.open(image_source)
                st.image(
                    image, 
                    caption=f"Uploaded Image ({image.size[0]}x{image.size[1]})",
                    use_column_width=True
                )
                
                # Image info
                file_size = len(image_source.getvalue()) / 1024  # KB
                st.caption(f"File size: {file_size:.1f} KB | Format: {image.format}")
                
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
                return
        
        with col_info:
            st.markdown("### 🔧 Analysis Options")
            
            # Advanced options
            with st.expander("Advanced Settings", expanded=False):
                confidence_threshold = st.slider(
                    "Confidence Threshold",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.5,
                    step=0.1,
                    help="Minimum confidence score for predictions"
                )
                
                max_predictions = st.number_input(
                    "Max Predictions",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="Maximum number of predictions to return"
                )
                
                enable_explanations = st.checkbox(
                    "Generate Explanations",
                    value=True,
                    help="Generate AI explanations for the analysis"
                )
            
            # Analysis button
            if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
                analyze_image(
                    image_source, 
                    analysis_type, 
                    language,
                    confidence_threshold,
                    max_predictions,
                    enable_explanations,
                    session_manager
                )
    
    else:
        # Show example images and instructions
        st.markdown("### 📋 Instructions")
        
        instructions = {
            "skin_condition": {
                "icon": "🔍",
                "title": "Skin Condition Analysis",
                "description": "Upload a clear photo of the skin area you want to analyze. Ensure good lighting and focus.",
                "tips": [
                    "Use natural lighting when possible",
                    "Keep the camera steady for sharp images",
                    "Include some surrounding healthy skin for comparison",
                    "Avoid using flash which can alter skin appearance"
                ]
            },
            "eye_health": {
                "icon": "👁️",
                "title": "Eye Health Assessment", 
                "description": "Upload a close-up photo of the eye area. The image should be well-lit and in focus.",
                "tips": [
                    "Ensure the eye is fully open and visible",
                    "Use good lighting to show eye details clearly",
                    "Keep the camera at eye level",
                    "Avoid reflections from glasses if wearing them"
                ]
            },
            "food_recognition": {
                "icon": "🍎",
                "title": "Food Recognition & Nutrition",
                "description": "Upload a photo of food items for identification and nutritional analysis.",
                "tips": [
                    "Show the food clearly without obstructions",
                    "Include the entire portion if possible",
                    "Use good lighting to show food colors accurately",
                    "Separate different food items when possible"
                ]
            },
            "emotion_detection": {
                "icon": "😊", 
                "title": "Emotion Detection",
                "description": "Upload a photo showing facial expressions for emotion analysis.",
                "tips": [
                    "Ensure the face is clearly visible and well-lit",
                    "Face should be the main subject of the photo",
                    "Avoid sunglasses or face coverings",
                    "Natural expressions work best"
                ]
            }
        }
        
        current_instruction = instructions[analysis_type]
        
        st.markdown(
            create_custom_component(
                f"""
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">
                        {current_instruction['icon']}
                    </div>
                    <h3>{current_instruction['title']}</h3>
                    <p style="color: #666; margin-bottom: 1.5rem;">
                        {current_instruction['description']}
                    </p>
                    <div style="text-align: left; max-width: 400px; margin: 0 auto;">
                        <strong>💡 Tips for best results:</strong>
                        <ul style="margin-top: 0.5rem;">
                            {''.join([f'<li>{tip}</li>' for tip in current_instruction['tips']])}
                        </ul>
                    </div>
                </div>
                """,
                "card"
            ),
            unsafe_allow_html=True
        )

def analyze_image(image_source, analysis_type, language, confidence_threshold, 
                 max_predictions, enable_explanations, session_manager):
    """Perform image analysis"""
    
    try:
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Preparing image for analysis...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        # Import services
        from services import ImageService
        from api.gateway import ServiceOrchestrator, AnalysisRequest
        from unittest.mock import MagicMock, AsyncMock
        import asyncio
        
        status_text.text("🤖 Initializing AI models...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        # Create mock file object
        mock_file = MagicMock()
        mock_file.filename = f"uploaded_image.{image_source.type.split('/')[-1]}"
        mock_file.read = AsyncMock(return_value=image_source.getvalue())
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            analysis_type=analysis_type,
            session_id=session_manager.get_session_id(),
            user_id=session_manager.get_user_info().get('username'),
            language=language
        )
        
        status_text.text("🔍 Performing AI analysis...")
        progress_bar.progress(70)
        time.sleep(1)
        
        # Perform analysis
        orchestrator = ServiceOrchestrator()
        
        async def run_analysis():
            return await orchestrator.process_image_analysis(mock_file, analysis_request)
        
        result = asyncio.run(run_analysis())
        
        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        display_analysis_results(result, analysis_type, enable_explanations, session_manager)
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        st.exception(e)

def display_analysis_results(result, analysis_type, enable_explanations, session_manager):
    """Display analysis results"""
    
    if result['status'] == 'success':
        st.success("✅ Analysis completed successfully!")
        
        analysis_result = result['analysis_result']
        processing_time = result.get('processing_time', 0)
        
        # Add to session history
        session_manager.add_analysis(analysis_type, analysis_result)
        
        # Results header
        st.markdown("### 📊 Analysis Results")
        
        # Processing info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Processing Time", f"{processing_time:.2f}s")
        with col2:
            st.metric("Analysis Type", analysis_type.replace('_', ' ').title())
        with col3:
            confidence = analysis_result.get('confidence', 0.5)
            st.metric("Overall Confidence", f"{confidence:.1%}")
        
        # Main results
        predictions = analysis_result.get('predictions', [])
        
        if predictions:
            st.markdown("#### 🎯 Predictions")
            
            for i, prediction in enumerate(predictions[:5]):  # Show top 5
                with st.expander(f"Prediction {i+1}: {prediction.get('label', 'Unknown')}", expanded=i==0):
                    
                    col_pred, col_conf = st.columns([3, 1])
                    
                    with col_pred:
                        st.markdown(f"**Label:** {prediction.get('label', 'Unknown')}")
                        st.markdown(f"**Description:** {prediction.get('description', 'No description available')}")
                        
                        # Additional details based on analysis type
                        if analysis_type == "skin_condition":
                            severity = prediction.get('severity', 'Unknown')
                            st.markdown(f"**Severity:** {severity}")
                            recommendations = prediction.get('recommendations', [])
                            if recommendations:
                                st.markdown("**Recommendations:**")
                                for rec in recommendations:
                                    st.markdown(f"• {rec}")
                        
                        elif analysis_type == "food_recognition":
                            nutrition = prediction.get('nutrition', {})
                            if nutrition:
                                st.markdown("**Nutritional Information:**")
                                for key, value in nutrition.items():
                                    st.markdown(f"• **{key.title()}:** {value}")
                        
                        elif analysis_type == "emotion_detection":
                            intensity = prediction.get('intensity', 'Unknown')
                            st.markdown(f"**Intensity:** {intensity}")
                    
                    with col_conf:
                        confidence = prediction.get('confidence', 0.0)
                        st.markdown(
                            f"**Confidence:** {format_confidence_score(confidence)}",
                            unsafe_allow_html=True
                        )
                        
                        # Confidence gauge
                        fig_gauge = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = confidence * 100,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Confidence"},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 80], 'color': "yellow"},
                                    {'range': [80, 100], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Confidence distribution chart
            if len(predictions) > 1:
                st.markdown("#### 📈 Confidence Distribution")
                
                labels = [p.get('label', f'Prediction {i+1}') for i, p in enumerate(predictions)]
                confidences = [p.get('confidence', 0) * 100 for p in predictions]
                
                fig_bar = px.bar(
                    x=labels,
                    y=confidences,
                    title="Prediction Confidence Scores",
                    labels={'x': 'Predictions', 'y': 'Confidence (%)'},
                    color=confidences,
                    color_continuous_scale='RdYlGn'
                )
                fig_bar.update_layout(height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Explanations
        if enable_explanations:
            st.markdown("#### 🔍 AI Explanations")
            
            with st.spinner("Generating explanations..."):
                # Mock explanation generation
                time.sleep(1)
                
                explanation_tabs = st.tabs(["Decision Path", "Key Features", "Visual Analysis"])
                
                with explanation_tabs[0]:
                    st.markdown(
                        create_custom_component(
                            """
                            <h4>🧠 Decision Path</h4>
                            <p>The AI model analyzed the image through the following steps:</p>
                            <ol>
                                <li><strong>Image Preprocessing:</strong> Normalized image size and enhanced contrast</li>
                                <li><strong>Feature Extraction:</strong> Identified key visual patterns and textures</li>
                                <li><strong>Pattern Matching:</strong> Compared features against trained medical patterns</li>
                                <li><strong>Confidence Scoring:</strong> Calculated probability scores for each prediction</li>
                                <li><strong>Result Ranking:</strong> Ordered predictions by confidence and relevance</li>
                            </ol>
                            """,
                            "card"
                        ),
                        unsafe_allow_html=True
                    )
                
                with explanation_tabs[1]:
                    st.markdown("**🔑 Key Features Identified:**")
                    
                    # Mock key features
                    features = [
                        {"feature": "Color Distribution", "importance": 0.85, "description": "Analyzed color patterns and variations"},
                        {"feature": "Texture Analysis", "importance": 0.72, "description": "Examined surface texture and smoothness"},
                        {"feature": "Shape Recognition", "importance": 0.68, "description": "Identified geometric patterns and boundaries"},
                        {"feature": "Contrast Levels", "importance": 0.55, "description": "Measured light and dark area distribution"}
                    ]
                    
                    for feature in features:
                        col_feat, col_imp = st.columns([3, 1])
                        with col_feat:
                            st.markdown(f"**{feature['feature']}**")
                            st.caption(feature['description'])
                        with col_imp:
                            st.progress(feature['importance'])
                            st.caption(f"{feature['importance']:.0%}")
                
                with explanation_tabs[2]:
                    st.markdown("**👁️ Visual Analysis:**")
                    st.info("🔧 Visual heatmaps and attention maps would be displayed here in the full implementation with GradCAM integration.")
        
        # Action buttons
        st.markdown("---")
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("💾 Save Results", use_container_width=True):
                st.success("Results saved to your history!")
        
        with col_action2:
            if st.button("📤 Export Report", use_container_width=True):
                # Generate downloadable report
                report_data = {
                    'analysis_type': analysis_type,
                    'timestamp': result.get('timestamp', 'Unknown'),
                    'predictions': predictions,
                    'processing_time': processing_time
                }
                
                import json
                report_json = json.dumps(report_data, indent=2, default=str)
                
                st.download_button(
                    label="📄 Download JSON Report",
                    data=report_json,
                    file_name=f"analysis_report_{analysis_type}_{int(time.time())}.json",
                    mime="application/json"
                )
        
        with col_action3:
            if st.button("🔄 Analyze Another", use_container_width=True):
                st.rerun()
    
    else:
        st.error(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
        
        if st.button("🔄 Try Again"):
            st.rerun()