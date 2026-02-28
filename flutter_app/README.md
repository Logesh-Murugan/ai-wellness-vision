# AI WellnessVision Flutter App 🧠💚

A comprehensive Flutter mobile application for AI-powered health and wellness analysis.

## Features

### 🖼️ **Multi-Modal Image Analysis**
- **Skin Condition Detection**: Analyze skin conditions including acne, eczema, melanoma
- **Eye Health Screening**: Detect diabetic retinopathy, cataracts, glaucoma
- **Food Recognition**: Identify foods and provide nutritional information
- **Emotion Detection**: Analyze facial expressions for emotional states

### 💬 **Intelligent Conversational AI**
- **Health Knowledge Base**: Comprehensive health information and advice
- **Multilingual Support**: 7 languages including English, Hindi, Tamil, Telugu, Bengali, Gujarati, Marathi
- **Context-Aware Conversations**: Maintains conversation history and context
- **Sentiment Analysis**: Understands emotional context of user messages

### 🎤 **Advanced Speech Processing**
- **Speech-to-Text**: High-accuracy transcription
- **Text-to-Speech**: Natural voice synthesis in multiple languages
- **Real-time Processing**: Low-latency audio processing
- **Language Detection**: Automatic language identification

### 🔍 **Explainable AI**
- **Visual Explanations**: Clear reasoning for AI decisions
- **Confidence Scoring**: Transparency in AI predictions
- **Decision Paths**: Step-by-step reasoning explanations

### 📱 **Native Mobile Experience**
- **Material Design 3**: Modern, accessible UI
- **Dark/Light Theme**: System-aware theming
- **Offline Support**: Core features work offline
- **Push Notifications**: Health reminders and updates

## Getting Started

### Prerequisites
- Flutter SDK (>=3.0.0)
- Dart SDK (>=3.0.0)
- Android Studio / VS Code
- iOS development setup (for iOS builds)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-wellnessvision.git
   cd ai-wellnessvision/flutter_app
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   # Debug mode
   flutter run
   
   # Release mode
   flutter run --release
   ```

### Building for Production

```bash
# Android APK
flutter build apk --release

# Android App Bundle
flutter build appbundle --release

# iOS
flutter build ios --release
```

## Project Structure

```
flutter_app/
├── lib/
│   ├── core/                    # Core functionality
│   │   ├── app.dart            # Main app configuration
│   │   ├── constants/          # App constants
│   │   ├── providers/          # State management
│   │   ├── router/             # Navigation routing
│   │   ├── services/           # Core services
│   │   ├── theme/              # App theming
│   │   └── utils/              # Utility functions
│   ├── features/               # Feature modules
│   │   ├── auth/               # Authentication
│   │   ├── chat/               # Chat interface
│   │   ├── history/            # History & reports
│   │   ├── home/               # Home dashboard
│   │   ├── image_analysis/     # Image analysis
│   │   ├── profile/            # User profile
│   │   ├── settings/           # App settings
│   │   └── voice/              # Voice interaction
│   ├── shared/                 # Shared components
│   │   └── presentation/       # Reusable widgets
│   └── main.dart               # App entry point
├── assets/                     # Static assets
├── android/                    # Android configuration
├── ios/                        # iOS configuration
└── pubspec.yaml               # Dependencies
```

## Architecture

The app follows **Clean Architecture** principles with **Feature-First** organization:

- **Features**: Self-contained modules (auth, chat, etc.)
- **Layers**: Presentation → Domain → Data
- **State Management**: Riverpod for reactive state
- **Navigation**: GoRouter for declarative routing
- **Dependency Injection**: Riverpod providers

## Key Technologies

- **Flutter**: Cross-platform mobile framework
- **Riverpod**: State management and dependency injection
- **GoRouter**: Declarative routing
- **Material Design 3**: Modern UI components
- **Shared Preferences**: Local data persistence
- **Image Picker**: Camera and gallery access
- **Speech Recognition**: Voice input processing
- **HTTP**: API communication

## Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
API_BASE_URL=http://localhost:8000/api/v1
WEBSOCKET_URL=ws://localhost:8000/ws
```

### API Integration
The app connects to the Python backend API. Ensure the backend is running:

```bash
# In the main project directory
python main.py
```

## Features Implementation

### 🏠 Home Dashboard
- Activity overview and statistics
- Quick action buttons
- Recent activity feed
- Health tips and system status

### 📸 Image Analysis
- Camera and gallery image selection
- Multiple analysis types (skin, food, emotion, eye)
- Real-time processing with progress indicators
- Detailed results with explanations

### 💬 Chat Interface
- Real-time messaging with AI
- Multiple chat modes (general, symptoms, wellness, mental health)
- Message history and context
- Quick suggestion buttons

### 🎤 Voice Interaction
- Press-and-hold recording
- Real-time transcription
- Voice playback of responses
- Multiple language support

### 📊 History & Reports
- Comprehensive activity tracking
- Filterable history views
- Detailed interaction records
- Data export capabilities

### ⚙️ Settings
- User preferences management
- Theme and language selection
- Privacy and security controls
- Account management

## Testing

```bash
# Run unit tests
flutter test

# Run integration tests
flutter test integration_test/

# Run with coverage
flutter test --coverage
```

## Deployment

### Android Play Store
1. Build signed APK/AAB
2. Upload to Play Console
3. Configure store listing
4. Submit for review

### iOS App Store
1. Build for iOS
2. Archive in Xcode
3. Upload to App Store Connect
4. Configure app metadata
5. Submit for review

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Medical Disclaimer

⚠️ **Important**: This application provides general health information and is not intended to replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Support

- 📖 **Documentation**: Check the inline code documentation
- 🐛 **Bug Reports**: Create an issue on GitHub
- 💡 **Feature Requests**: Start a discussion
- 💬 **Questions**: Use GitHub Discussions

---

Built with ❤️ using Flutter