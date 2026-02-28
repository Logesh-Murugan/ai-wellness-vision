# AI WellnessVision - Clean Project Structure

## 📁 Root Directory
```
ai-wellness-vision/
├── 🚀 Main Applications
│   ├── demo_app.py              # Main demo application
│   ├── streamlit_app.py         # Streamlit web interface
│   └── requirements.txt         # Python dependencies
│
├── 📦 Source Code (src/)
│   ├── api/                     # API layer
│   │   ├── auth.py             # Authentication
│   │   ├── gateway.py          # API gateway
│   │   └── middleware.py       # API middleware
│   │
│   ├── models/                  # Data models
│   │   ├── base.py             # Base model classes
│   │   ├── conversation_models.py
│   │   ├── health_models.py
│   │   └── user_models.py
│   │
│   ├── services/               # Business logic
│   │   ├── explainable_ai_service.py
│   │   ├── image_service.py    # Image analysis
│   │   ├── integration_service.py
│   │   ├── nlp_service.py      # Natural language processing
│   │   └── speech_service.py   # Speech processing
│   │
│   ├── security/               # Security features
│   │   ├── consent.py          # Consent management
│   │   ├── data_protection.py  # Data protection
│   │   ├── encryption.py       # Encryption services
│   │   ├── privacy.py          # Privacy management
│   │   ├── security_middleware.py
│   │   └── transport_security.py
│   │
│   ├── ui/                     # User interface
│   │   ├── components/
│   │   │   └── auth.py         # Auth components
│   │   ├── pages/              # Streamlit pages
│   │   │   ├── chat_interface_page.py
│   │   │   ├── history_page.py
│   │   │   ├── home_page.py
│   │   │   ├── image_analysis_page.py
│   │   │   ├── settings_page.py
│   │   │   └── voice_interaction_page.py
│   │   └── utils/
│   │       ├── session_manager.py
│   │       └── theme_config.py
│   │
│   ├── utils/                  # Utilities
│   │   ├── app_initializer.py
│   │   ├── config_manager.py
│   │   ├── error_handling.py
│   │   └── logging_config.py
│   │
│   └── config.py               # Main configuration
│
├── 🧪 Tests (tests/)
│   ├── conftest.py             # Pytest configuration
│   ├── pytest.ini             # Pytest settings
│   ├── test_accessibility.py   # Accessibility tests
│   ├── test_api_gateway.py     # API tests
│   ├── test_auth.py            # Authentication tests
│   ├── test_config.py          # Configuration tests
│   ├── test_error_handling.py  # Error handling tests
│   ├── test_explainable_ai_service.py
│   ├── test_image_service.py   # Image service tests
│   ├── test_integration_api.py # API integration tests
│   ├── test_middleware.py      # Middleware tests
│   ├── test_models.py          # Model tests
│   ├── test_multilingual.py    # Multilingual tests
│   ├── test_nlp_service.py     # NLP service tests
│   ├── test_runner.py          # Test runner
│   ├── test_security_comprehensive.py
│   ├── test_speech_service.py  # Speech service tests
│   └── test_ui.py              # UI tests
│
├── ⚙️ Configuration
│   ├── config/
│   │   ├── development.json    # Dev configuration
│   │   └── production.json     # Prod configuration
│   ├── .env.example            # Environment variables template
│   └── .gitignore              # Git ignore rules
│
├── 🐳 Deployment
│   ├── docker/                 # Docker configurations
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.streamlit
│   │   └── Dockerfile.worker
│   ├── Dockerfile              # Main Dockerfile
│   ├── docker-compose.yml      # Docker Compose
│   ├── docker-compose.dev.yml  # Dev Docker Compose
│   │
│   ├── k8s/                    # Kubernetes manifests
│   │   ├── ai-wellness-app.yaml
│   │   ├── configmap.yaml
│   │   ├── hpa.yaml            # Horizontal Pod Autoscaler
│   │   ├── namespace.yaml
│   │   ├── network-policies.yaml
│   │   ├── persistent-volumes.yaml
│   │   ├── postgres.yaml
│   │   ├── redis.yaml
│   │   └── secrets.yaml
│   │
│   ├── nginx/                  # Nginx configuration
│   │   └── nginx.conf
│   │
│   └── scripts/                # Deployment scripts
│       ├── build.sh
│       ├── deploy.sh
│       ├── init-db.sql
│       ├── validate-deployment.ps1
│       └── validate-deployment.sh
│
├── 📊 Monitoring
│   ├── monitoring/
│   │   ├── grafana/dashboards/
│   │   │   └── ai-wellness-dashboard.json
│   │   ├── alert_rules.yml
│   │   └── prometheus.yml
│   │
│   └── .github/workflows/      # CI/CD
│       ├── ci-cd.yml
│       └── staging-deploy.yml
│
├── 🤖 Models
│   └── models/
│       └── speech_model.pth    # Pre-trained speech model
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── SECURITY_IMPLEMENTATION_COMPLETE.md
│   │   └── SECURITY_PRIVACY_README.md
│   ├── README.md               # Main documentation
│   ├── CONTRIBUTING.md         # Contribution guidelines
│   ├── DEPLOYMENT.md           # Deployment instructions
│   ├── LICENSE                 # License file
│   └── Makefile                # Build automation
│
└── 🔧 Development Tools
    └── .kiro/                  # Kiro IDE configuration
        └── specs/ai-wellness-vision/
            ├── design.md
            ├── requirements.md
            └── tasks.md
```

## 🎯 Core Features

### 1. **Multi-Modal AI Services**
- **Image Analysis**: Health condition detection and analysis
- **NLP Processing**: Multilingual conversational AI (7 languages)
- **Speech Processing**: Speech-to-text and text-to-speech
- **Explainable AI**: AI decision explanations and insights

### 2. **Security & Privacy**
- **Data Encryption**: End-to-end encryption for sensitive data
- **Consent Management**: GDPR-compliant consent handling
- **Privacy Protection**: Data anonymization and protection
- **Transport Security**: HTTPS and secure communications

### 3. **User Interface**
- **Streamlit Web App**: Multi-page responsive interface
- **Authentication**: Secure user authentication system
- **Session Management**: User session and state management
- **Accessibility**: WCAG-compliant accessible design

### 4. **API & Integration**
- **RESTful API**: FastAPI-based API gateway
- **Authentication**: JWT-based API authentication
- **Middleware**: Request/response processing middleware
- **Rate Limiting**: API rate limiting and security

### 5. **Deployment & DevOps**
- **Docker**: Multi-container deployment
- **Kubernetes**: Production-ready K8s manifests
- **CI/CD**: GitHub Actions workflows
- **Monitoring**: Prometheus + Grafana monitoring

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Demo Application**
   ```bash
   python demo_app.py
   ```

3. **Launch Web Interface**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Docker Deployment**
   ```bash
   docker-compose up -d
   ```

## 📝 Notes

- **Clean Architecture**: Organized by feature and responsibility
- **Modular Design**: Each component is independently testable
- **Production Ready**: Includes security, monitoring, and deployment
- **Scalable**: Designed for horizontal scaling with K8s
- **Maintainable**: Clear separation of concerns and documentation