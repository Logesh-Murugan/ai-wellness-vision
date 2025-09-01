# theme_config.py - Custom theme configuration for Streamlit
import streamlit as st

def apply_custom_theme():
    """Apply custom CSS theme to the Streamlit app"""
    
    custom_css = """
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --warning-color: #ff9800;
        --error-color: #d62728;
        --background-color: #ffffff;
        --surface-color: #f8f9fa;
        --text-color: #333333;
        --text-secondary: #666666;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .custom-card {
        background: var(--surface-color);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Metric styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Chat message styling */
    .user-message {
        background: var(--primary-color);
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        margin-left: 2rem;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .ai-message {
        background: var(--surface-color);
        color: var(--text-color);
        padding: 0.8rem 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        margin-right: 2rem;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid #e0e0e0;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #1565c0;
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.3);
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed var(--primary-color);
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--surface-color);
    }
    
    /* Alert styling */
    .alert-success {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .alert-error {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    /* Analysis result styling */
    .analysis-result {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .confidence-high {
        color: var(--success-color);
        font-weight: bold;
    }
    
    .confidence-medium {
        color: var(--warning-color);
        font-weight: bold;
    }
    
    .confidence-low {
        color: var(--error-color);
        font-weight: bold;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--primary-color);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 1rem auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message, .ai-message {
            max-width: 95%;
            margin-left: 0.5rem;
            margin-right: 0.5rem;
        }
        
        .custom-card {
            padding: 1rem;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #1e1e1e;
            --surface-color: #2d2d2d;
            --text-color: #ffffff;
            --text-secondary: #cccccc;
        }
        
        .custom-card {
            background: var(--surface-color);
            border-color: #404040;
        }
        
        .ai-message {
            background: var(--surface-color);
            color: var(--text-color);
            border-color: #404040;
        }
    }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)

def create_custom_component(content: str, component_type: str = "card") -> str:
    """Create a custom styled component"""
    
    if component_type == "card":
        return f'<div class="custom-card">{content}</div>'
    elif component_type == "alert-success":
        return f'<div class="alert-success">✅ {content}</div>'
    elif component_type == "alert-warning":
        return f'<div class="alert-warning">⚠️ {content}</div>'
    elif component_type == "alert-error":
        return f'<div class="alert-error">❌ {content}</div>'
    elif component_type == "metric":
        return f'<div class="metric-card">{content}</div>'
    else:
        return content

def format_confidence_score(confidence: float) -> str:
    """Format confidence score with appropriate styling"""
    if confidence >= 0.8:
        return f'<span class="confidence-high">{confidence:.1%}</span>'
    elif confidence >= 0.6:
        return f'<span class="confidence-medium">{confidence:.1%}</span>'
    else:
        return f'<span class="confidence-low">{confidence:.1%}</span>'