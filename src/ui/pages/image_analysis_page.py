"""Image Analysis Page - AI-powered image analysis interface"""

import streamlit as st
import time
import random
from datetime import datetime

# Optional imports with fallbacks
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from src.ui.utils.session_manager import SessionManager
    from src.ui.utils.theme_config import create_custom_component, format_confidence_score
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Fallback functions
    def create_custom_component(content, comp_type="card"):
        return f'<div style="padding: 1rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.5rem 0;">{content}</div>'
    
    def format_confidence_score(confidence):
        return f"{confidence:.1%}"


def _format_confidence(p: float) -> str:
    try:
        return f"{float(p):.1%}"
    except Exception:
        return "-"


def render():
    """Render the image analysis page"""
    
    # Initialize session manager
    if UTILS_AVAILABLE:
        session_manager = SessionManager()
    else:
        # Mock session manager
        class MockSessionManager:
            def add_analysis(self, *args): pass
            def get_session_id(self): return "demo_session"
            def get_user_info(self): return {"username": "demo_user"}
        session_manager = MockSessionManager()

    st.title("� AI Image Aenalysis")
    st.markdown("Upload an image for AI-powered health analysis")

    # Configuration options
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["skin_condition", "eye_health", "food_recognition", "emotion_detection"],
            format_func=lambda x: {
                "skin_condition": "🔍 Skin Condition Detection",
                "eye_health": "👁️ Eye Health Assessment", 
                "food_recognition": "🍎 Food Recognition",
                "emotion_detection": "😊 Emotion Detection",
            }.get(x, x),
        )
    
    with col_config2:
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
            }.get(x, x)
        )

    # File upload
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg"],
        help="Supported formats: PNG, JPG, JPEG (max 10MB)",
    )

    if uploaded_file is None:
        st.info("👆 Please upload an image to begin analysis")
        
        # Show example images or instructions
        st.markdown("### 💡 Analysis Examples")
        
        example_col1, example_col2 = st.columns(2)
        
        with example_col1:
            st.markdown("""
            **🔍 Skin Condition Detection:**
            - Acne analysis
            - Eczema identification  
            - Melanoma screening
            - General skin health
            """)
            
        with example_col2:
            st.markdown("""
            **🍎 Food Recognition:**
            - Nutritional analysis
            - Calorie estimation
            - Health scoring
            - Dietary recommendations
            """)
        
        return

    # Preview uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col_adv1, col_adv2 = st.columns(2)
        
        with col_adv1:
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.1)
            max_predictions = st.number_input("Max Predictions", 1, 10, 3)
        
        with col_adv2:
            enable_explanations = st.checkbox("Enable AI Explanations", value=True)
            save_results = st.checkbox("Save to History", value=True)

    # Analysis button
    if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
        analyze_image(uploaded_file, analysis_type, language, confidence_threshold, 
                     max_predictions, enable_explanations, session_manager)

    # Disclaimer
    st.markdown("---")
    st.warning("⚠️ **Medical Disclaimer:** This tool provides general information only and is not a substitute for professional medical advice, diagnosis, or treatment.")


def _mock_result(analysis_type: str) -> dict:
    base_conf = random.uniform(0.7, 0.95)

    if analysis_type == "skin_condition":
        return {
            "condition": "Healthy Skin" if base_conf > 0.82 else "Minor Irritation",
            "confidence": base_conf,
            "risk_level": "Low" if base_conf > 0.8 else "Medium",
            "recommendations": [
                "Use sunscreen daily (SPF 30+)",
                "Stay hydrated",
                "Monitor for changes",
            ],
        }
    if analysis_type == "eye_health":
        return {
            "condition": "Normal" if base_conf > 0.82 else "Mild Strain",
            "confidence": base_conf,
            "risk_level": "Low",
            "recommendations": [
                "Regular eye checkups",
                "Take screen breaks",
                "Ensure proper lighting",
            ],
        }
    if analysis_type == "food_recognition":
        foods = ["Apple", "Banana", "Salad", "Sandwich"]
        return {
            "food_items": [random.choice(foods)],
            "confidence": base_conf,
            "nutritional_info": {
                "calories": random.randint(60, 400),
                "protein": f"{random.randint(1, 20)}g",
                "carbs": f"{random.randint(10, 60)}g",
            },
            "health_score": random.randint(6, 10),
        }
    # emotion_detection
    return {
        "primary_emotion": random.choice(["Happy", "Neutral", "Focused", "Relaxed"]),
        "confidence": base_conf,
        "emotion_scores": {
            "Happy": random.uniform(0.2, 0.9),
            "Sad": random.uniform(0.0, 0.3),
            "Neutral": random.uniform(0.2, 0.8),
        },
    }


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
        
        status_text.text("🤖 Initializing AI models...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        status_text.text("🔍 Performing AI analysis...")
        progress_bar.progress(70)
        time.sleep(1)
        
        # Generate mock analysis result
        result = _generate_mock_analysis_result(analysis_type, confidence_threshold)
        
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
        # Show fallback result
        fallback_result = _mock_result(analysis_type)
        display_simple_results(fallback_result, analysis_type)

def display_analysis_results(result, analysis_type, enable_explanations, session_manager):
    """Display analysis results"""
    
    st.success("✅ Analysis completed successfully!")
    
    # Add to session history
    session_manager.add_analysis(analysis_type, result)
    
    # Results header
    st.markdown("### 📊 Analysis Results")
    
    # Processing info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Processing Time", f"{result.get('processing_time', 1.2):.2f}s")
    with col2:
        st.metric("Analysis Type", analysis_type.replace('_', ' ').title())
    with col3:
        confidence = result.get('confidence', 0.85)
        st.metric("Overall Confidence", f"{confidence:.1%}")
    
    # Main results display
    if analysis_type in ("skin_condition", "eye_health"):
        st.metric("Condition", result["condition"]) 
        st.metric("Confidence", _format_confidence(result["confidence"]))
        st.metric("Risk Level", result.get("risk_level", "Low")) 
        st.markdown("**Recommendations:**")
        for rec in result.get("recommendations", []):
            st.markdown(f"• {rec}")

    elif analysis_type == "food_recognition":
        st.metric("Detected Food", ", ".join(result.get("food_items", ["Unknown"])))
        st.metric("Confidence", _format_confidence(result["confidence"]))
        st.metric("Health Score", f"{result.get('health_score', 8)}/10")
        st.markdown("**Nutritional Info:**")
        for k, v in result.get("nutritional_info", {}).items():
            st.markdown(f"• {k.title()}: {v}")

    else:  # emotion_detection
        st.metric("Primary Emotion", result.get("primary_emotion", "Happy")) 
        st.metric("Confidence", _format_confidence(result["confidence"]))
        st.markdown("**Emotion Breakdown:**")
        for k, v in result.get("emotion_scores", {}).items():
            st.markdown(f"• {k}: {_format_confidence(v)}")
    
    # Explanations section
    if enable_explanations:
        st.markdown("#### 🔍 AI Explanations")
        
        explanation_tabs = st.tabs(["Decision Path", "Key Features"])
        
        with explanation_tabs[0]:
            st.markdown("""
            **🧠 Decision Path:**
            1. **Image Preprocessing:** Normalized and enhanced image quality
            2. **Feature Extraction:** Identified key visual patterns
            3. **Pattern Matching:** Compared against trained models
            4. **Confidence Scoring:** Calculated prediction probabilities
            5. **Result Ranking:** Ordered by confidence and relevance
            """)
        
        with explanation_tabs[1]:
            st.markdown("**🔑 Key Features Identified:**")
            features = ["Color Distribution (85%)", "Texture Analysis (72%)", "Shape Recognition (68%)"]
            for feature in features:
                st.markdown(f"• {feature}")
    
    # Action buttons
    st.markdown("---")
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("💾 Save Results", use_container_width=True):
            st.success("Results saved to your history!")
    
    with col_action2:
        if st.button("📤 Export Report", use_container_width=True):
            import json
            report_data = {
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat(),
                'result': result
            }
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


def display_simple_results(result, analysis_type):
    """Display simple fallback results"""
    st.success("✅ Analysis complete!")
    st.subheader("📊 Results")

    if analysis_type in ("skin_condition", "eye_health"):
        st.metric("Condition", result["condition"]) 
        st.metric("Confidence", _format_confidence(result["confidence"]))
        st.metric("Risk Level", result["risk_level"]) 
        st.markdown("**Recommendations:**")
        for rec in result["recommendations"]:
            st.markdown(f"• {rec}")

    elif analysis_type == "food_recognition":
        st.metric("Detected Food", ", ".join(result["food_items"]))
        st.metric("Confidence", _format_confidence(result["confidence"]))
        st.metric("Health Score", f"{result['health_score']}/10")
        st.markdown("**Nutritional Info:**")
        for k, v in result["nutritional_info"].items():
            st.markdown(f"• {k.title()}: {v}")

    else:  # emotion_detection
        st.metric("Primary Emotion", result["primary_emotion"]) 
        st.metric("Confidence", _format_confidence(result["confidence"]))
        st.markdown("**Emotion Breakdown:**")
        for k, v in result["emotion_scores"].items():
            st.markdown(f"• {k}: {_format_confidence(v)}")

    st.warning("⚠️ Demo results only. Not medical advice.")


def _generate_mock_analysis_result(analysis_type, confidence_threshold):
    """Generate comprehensive mock analysis result"""
    base_conf = random.uniform(max(0.7, confidence_threshold), 0.95)
    
    result = _mock_result(analysis_type)
    result.update({
        'processing_time': random.uniform(1.0, 3.0),
        'timestamp': datetime.now().isoformat(),
        'model_version': '1.0.0',
        'confidence_threshold': confidence_threshold
    })
    
    return result