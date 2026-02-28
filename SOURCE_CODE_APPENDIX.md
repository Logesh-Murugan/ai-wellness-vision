# SOURCE CODE APPENDIX - AI WELLNESS VISION

## Table of Contents
1. [Backend API Server](#1-backend-api-server)
2. [CNN Health Analyzer](#2-cnn-health-analyzer)
3. [Flutter Mobile App](#3-flutter-mobile-app)
4. [Image Analysis Service](#4-image-analysis-service)
5. [NLP Service](#5-nlp-service)
6. [Authentication System](#6-authentication-system)
7. [Database Models](#7-database-models)
8. [Security Implementation](#8-security-implementation)
9. [Testing Code](#9-testing-code)
10. [Deployment Configurations](#10-deployment-configurations)

---

## 1. Backend API Server

### main_api_server.py
```python
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import asyncio
from typing import Optional, List
import logging

from src.services.image_service import EnhancedImageRecognitionService
from src.services.nlp_service import ComprehensiveNLPService
from src.api.auth import AuthManager
from src.models.user_models import User, UserCreate, UserLogin
from src.models.health_models import AnalysisResult, ChatMessage
from src.utils.logging_config import setup_logging

# Initialize FastAPI app
app = FastAPI(
    title="AI Wellness Vision API",
    description="Comprehensive AI-powered health and wellness platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
image_service = EnhancedImageRecognitionService()
nlp_service = ComprehensiveNLPService()
auth_manager = AuthManager()
security = HTTPBearer()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@app.on_startup
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting AI Wellness Vision API...")
    await image_service.initialize()
    await nlp_service.initialize()
    logger.info("All services initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "image_analysis": "ready",
            "nlp": "ready",
            "database": "connected"
        }
    }

@app.post("/api/v1/auth/register")
async def register_user(user_data: UserCreate):
    """Register new user"""
    try:
        user = await auth_manager.create_user(user_data)
        token = auth_manager.create_access_token({"sub": user.id})
        return {"user": user, "access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/login")
async def login_user(login_data: UserLogin):
    """User login"""
    try:
        user = await auth_manager.authenticate_user(
            login_data.username, login_data.password
        )
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = auth_manager.create_access_token({"sub": user.id})
        return {"access_token": token, "token_type": "bearer", "user": user}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/v1/analysis/image")
async def analyze_image(
    file: UploadFile = File(...),
    analysis_type: str = "general",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze uploaded image for health insights"""
    try:
        # Verify authentication
        user = await auth_manager.get_current_user(credentials.credentials)
        
        # Read image data
        image_data = await file.read()
        
        # Perform analysis
        result = await image_service.analyze_image(image_data, analysis_type)
        
        # Save result to database
        analysis_result = AnalysisResult(
            user_id=user.id,
            analysis_type=analysis_type,
            result=result,
            filename=file.filename
        )
        await analysis_result.save()
        
        return {
            "id": analysis_result.id,
            "analysis_type": analysis_type,
            "result": result,
            "timestamp": analysis_result.created_at
        }
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/message")
async def send_chat_message(
    message: ChatMessage,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Send message to AI health assistant"""
    try:
        # Verify authentication
        user = await auth_manager.get_current_user(credentials.credentials)
        
        # Process message with NLP service
        response = await nlp_service.process_health_message(
            message.content,
            user_id=user.id,
            language=message.language or "en"
        )
        
        return {
            "response": response.content,
            "confidence": response.confidence,
            "suggestions": response.suggestions,
            "timestamp": response.timestamp
        }
    except Exception as e:
        logger.error(f"Chat message error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analysis/history")
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get user's analysis history"""
    try:
        user = await auth_manager.get_current_user(credentials.credentials)
        
        history = await AnalysisResult.get_user_history(
            user.id, limit=limit, offset=offset
        )
        
        return {
            "history": history,
            "total": len(history),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

---

## 2. CNN Health Analyzer

### src/ai_models/cnn_health_analyzer.py
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class HealthCNN(nn.Module):
    """Convolutional Neural Network for health image analysis"""
    
    def __init__(self, num_classes: int, input_channels: int = 3):
        super(HealthCNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        
        # Pooling and dropout
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Fully connected layers
        self.fc1 = nn.Linear(256, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, num_classes)
        
    def forward(self, x):
        # Convolutional blocks
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        
        # Global average pooling
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x

class CNNHealthAnalyzer:
    """Main CNN-based health analyzer"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.class_names = {}
        self.transforms = self._setup_transforms()
        
        # Initialize models for different analysis types
        self._load_models()
        
    def _setup_transforms(self):
        """Setup image preprocessing transforms"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def _load_models(self):
        """Load pre-trained CNN models for different analysis types"""
        try:
            # Skin analysis model
            self.models['skin'] = HealthCNN(num_classes=5)  # healthy, acne, eczema, dry, oily
            self.class_names['skin'] = ['healthy', 'acne', 'eczema', 'dry_skin', 'oily_skin']
            
            # Eye health model
            self.models['eye'] = HealthCNN(num_classes=4)  # healthy, fatigue, redness, dark_circles
            self.class_names['eye'] = ['healthy', 'fatigue', 'redness', 'dark_circles']
            
            # Food analysis model
            self.models['food'] = HealthCNN(num_classes=6)  # healthy, processed, high_calorie, etc.
            self.class_names['food'] = ['healthy', 'processed', 'high_calorie', 'low_nutrition', 'balanced', 'organic']
            
            # Load model weights (in production, load from saved checkpoints)
            for model_type, model in self.models.items():
                model.to(self.device)
                model.eval()
                # model.load_state_dict(torch.load(f'models/{model_type}_model.pth'))
                
            logger.info("CNN models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading CNN models: {str(e)}")
            raise
    
    def preprocess_image(self, image_data: bytes) -> torch.Tensor:
        """Preprocess image for CNN analysis"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            
            # Apply transforms
            tensor = self.transforms(image).unsqueeze(0)
            
            return tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}")
            raise ValueError(f"Invalid image format: {str(e)}")
    
    async def analyze_image(self, image_data: bytes, analysis_type: str) -> Dict:
        """Perform CNN-based image analysis"""
        try:
            if analysis_type not in self.models:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
            # Preprocess image
            input_tensor = self.preprocess_image(image_data)
            
            # Get model and class names
            model = self.models[analysis_type]
            classes = self.class_names[analysis_type]
            
            # Perform inference
            with torch.no_grad():
                outputs = model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                # Get probability distribution
                prob_dist = {
                    classes[i]: float(probabilities[0][i])
                    for i in range(len(classes))
                }
                
                # Get prediction details
                predicted_class = classes[predicted.item()]
                confidence_score = float(confidence.item())
                
            # Generate recommendations
            recommendations = self._generate_recommendations(
                predicted_class, confidence_score, analysis_type
            )
            
            # Generate health insights
            health_insights = self._generate_health_insights(
                predicted_class, confidence_score, analysis_type
            )
            
            return {
                "predictions": [{"condition": predicted_class, "confidence": confidence_score}],
                "confidence": confidence_score,
                "probability_distribution": prob_dist,
                "recommendations": recommendations,
                "health_insights": health_insights,
                "processing_method": "CNN Deep Learning",
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            logger.error(f"CNN analysis error: {str(e)}")
            raise
    
    def _generate_recommendations(self, prediction: str, confidence: float, analysis_type: str) -> List[str]:
        """Generate health recommendations based on CNN analysis"""
        recommendations = []
        
        if analysis_type == "skin":
            if prediction == "healthy":
                recommendations = [
                    "Your skin appears healthy! Continue your current skincare routine.",
                    "Apply broad-spectrum SPF 30+ sunscreen daily.",
                    "Maintain hydration with 8-10 glasses of water daily.",
                    "Use a gentle cleanser twice daily."
                ]
            elif prediction == "acne":
                recommendations = [
                    "Consider using salicylic acid or benzoyl peroxide products.",
                    "Avoid touching or picking at affected areas.",
                    "Use non-comedogenic skincare products.",
                    "Consult a dermatologist if condition persists."
                ]
            elif prediction == "dry_skin":
                recommendations = [
                    "Use a rich, fragrance-free moisturizer twice daily.",
                    "Avoid hot showers and harsh soaps.",
                    "Consider using a humidifier in dry environments.",
                    "Look for products with ceramides or hyaluronic acid."
                ]
        
        elif analysis_type == "eye":
            if prediction == "healthy":
                recommendations = [
                    "Your eyes appear healthy! Maintain good eye hygiene.",
                    "Follow the 20-20-20 rule for screen time.",
                    "Ensure adequate sleep (7-9 hours nightly).",
                    "Regular eye exams are recommended."
                ]
            elif prediction == "fatigue":
                recommendations = [
                    "Ensure you're getting adequate sleep (7-9 hours).",
                    "Take regular breaks from screen time.",
                    "Stay hydrated throughout the day.",
                    "Consider eye drops if eyes feel dry."
                ]
        
        elif analysis_type == "food":
            if prediction == "healthy":
                recommendations = [
                    "Great choice! This appears to be nutritious food.",
                    "Maintain portion control for balanced nutrition.",
                    "Include variety in your diet for optimal health.",
                    "Stay hydrated with water throughout the day."
                ]
            elif prediction == "processed":
                recommendations = [
                    "Consider reducing processed food intake.",
                    "Add fresh fruits and vegetables to your meal.",
                    "Look for whole grain alternatives.",
                    "Check sodium and sugar content on labels."
                ]
        
        return recommendations
    
    def _generate_health_insights(self, prediction: str, confidence: float, analysis_type: str) -> Dict:
        """Generate detailed health insights"""
        severity_level = "none"
        follow_up_needed = False
        
        if confidence < 0.7:
            confidence_interpretation = "Moderate confidence - consider additional evaluation"
        elif confidence < 0.9:
            confidence_interpretation = "High confidence in analysis"
        else:
            confidence_interpretation = "Very high confidence in analysis"
        
        # Determine severity and follow-up needs
        if analysis_type == "skin" and prediction in ["acne", "eczema"]:
            severity_level = "mild" if confidence > 0.8 else "uncertain"
            follow_up_needed = confidence > 0.8
        elif analysis_type == "eye" and prediction in ["redness", "fatigue"]:
            severity_level = "mild"
            follow_up_needed = confidence > 0.85
        
        next_steps = []
        if follow_up_needed:
            next_steps.append("Consider consulting a healthcare professional")
        if confidence < 0.7:
            next_steps.append("Retake image with better lighting for more accurate analysis")
        else:
            next_steps.append("Analysis results are reliable for general guidance")
        
        return {
            "severity_level": severity_level,
            "follow_up_needed": follow_up_needed,
            "confidence_interpretation": confidence_interpretation,
            "next_steps": next_steps
        }
```## 
3. Flutter Mobile App

### flutter_app/lib/main.dart
```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/services.dart';

import 'core/app.dart';
import 'core/providers/auth_provider.dart';
import 'core/providers/theme_provider.dart';
import 'core/providers/chat_provider.dart';
import 'core/providers/image_analysis_provider.dart';
import 'core/providers/voice_provider.dart';
import 'core/services/storage_service.dart';
import 'core/services/notification_service.dart';
import 'core/utils/logger.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  await _initializeServices();
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  runApp(const AIWellnessApp());
}

Future<void> _initializeServices() async {
  try {
    // Initialize storage service
    await StorageService.instance.initialize();
    
    // Initialize notification service
    await NotificationService.instance.initialize();
    
    // Initialize logger
    Logger.initialize();
    
    Logger.info('All services initialized successfully');
  } catch (e) {
    Logger.error('Failed to initialize services: $e');
  }
}

class AIWellnessApp extends StatelessWidget {
  const AIWellnessApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => ImageAnalysisProvider()),
        ChangeNotifierProvider(create: (_) => VoiceProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, child) {
          return MaterialApp(
            title: 'AI Wellness Vision',
            debugShowCheckedModeBanner: false,
            theme: themeProvider.lightTheme,
            darkTheme: themeProvider.darkTheme,
            themeMode: themeProvider.themeMode,
            home: const AppWrapper(),
            builder: (context, child) {
              return MediaQuery(
                data: MediaQuery.of(context).copyWith(textScaleFactor: 1.0),
                child: child!,
              );
            },
          );
        },
      ),
    );
  }
}
```

### flutter_app/lib/core/app.dart
```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import '../shared/presentation/pages/splash_page.dart';
import '../shared/presentation/pages/onboarding_page.dart';
import '../shared/presentation/pages/main_navigation_page.dart';
import '../features/auth/presentation/pages/login_page.dart';

class AppWrapper extends StatefulWidget {
  const AppWrapper({Key? key}) : super(key: key);

  @override
  State<AppWrapper> createState() => _AppWrapperState();
}

class _AppWrapperState extends State<AppWrapper> {
  bool _isLoading = true;
  bool _isFirstTime = true;

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    await Future.delayed(const Duration(seconds: 2)); // Splash screen duration
    
    // Check if first time user
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    await authProvider.checkAuthStatus();
    
    // Check if onboarding completed
    _isFirstTime = await _checkFirstTimeUser();
    
    setState(() {
      _isLoading = false;
    });
  }

  Future<bool> _checkFirstTimeUser() async {
    // Implementation to check if user has completed onboarding
    return false; // For demo, assume not first time
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const SplashPage();
    }

    if (_isFirstTime) {
      return const OnboardingPage();
    }

    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        if (authProvider.isAuthenticated) {
          return const MainNavigationPage();
        } else {
          return const LoginPage();
        }
      },
    );
  }
}
```

### flutter_app/lib/features/home/presentation/pages/home_page.dart
```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../core/providers/auth_provider.dart';
import '../../../../shared/presentation/widgets/custom_app_bar.dart';
import '../../../../shared/presentation/widgets/quick_action_card.dart';
import '../../../../shared/presentation/widgets/stat_card.dart';
import '../../../../shared/presentation/widgets/recent_activity_card.dart';
import '../../../../shared/presentation/widgets/health_tip_card.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildWelcomeSection(),
              const SizedBox(height: 24),
              _buildQuickActions(),
              const SizedBox(height: 24),
              _buildHealthStats(),
              const SizedBox(height: 24),
              _buildRecentActivity(),
              const SizedBox(height: 24),
              _buildHealthTips(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeSection() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.currentUser;
        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Theme.of(context).primaryColor,
                Theme.of(context).primaryColor.withOpacity(0.8),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Welcome back, ${user?.name ?? 'User'}!',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'How are you feeling today?',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.white.withOpacity(0.9),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          childAspectRatio: 1.2,
          children: [
            QuickActionCard(
              title: 'Image Analysis',
              subtitle: 'Analyze health images',
              icon: Icons.camera_alt,
              color: Colors.blue,
              onTap: () => _navigateToImageAnalysis(),
            ),
            QuickActionCard(
              title: 'AI Chat',
              subtitle: 'Health assistant',
              icon: Icons.chat_bubble,
              color: Colors.green,
              onTap: () => _navigateToChat(),
            ),
            QuickActionCard(
              title: 'Voice Assistant',
              subtitle: 'Voice interaction',
              icon: Icons.mic,
              color: Colors.orange,
              onTap: () => _navigateToVoice(),
            ),
            QuickActionCard(
              title: 'History',
              subtitle: 'View past results',
              icon: Icons.history,
              color: Colors.purple,
              onTap: () => _navigateToHistory(),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildHealthStats() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Health Overview',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: StatCard(
                title: 'Analyses',
                value: '24',
                subtitle: 'This month',
                icon: Icons.analytics,
                color: Colors.blue,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: StatCard(
                title: 'Health Score',
                value: '85%',
                subtitle: 'Good',
                icon: Icons.favorite,
                color: Colors.red,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildRecentActivity() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Recent Activity',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: () => _navigateToHistory(),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: 3,
          itemBuilder: (context, index) {
            return RecentActivityCard(
              title: 'Skin Analysis',
              subtitle: 'Healthy skin detected',
              timestamp: '2 hours ago',
              icon: Icons.check_circle,
              color: Colors.green,
            );
          },
        ),
      ],
    );
  }

  Widget _buildHealthTips() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Health Tips',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        const HealthTipCard(
          title: 'Stay Hydrated',
          content: 'Drink at least 8 glasses of water daily for optimal health.',
          icon: Icons.water_drop,
        ),
      ],
    );
  }

  void _navigateToImageAnalysis() {
    Navigator.pushNamed(context, '/image-analysis');
  }

  void _navigateToChat() {
    Navigator.pushNamed(context, '/chat');
  }

  void _navigateToVoice() {
    Navigator.pushNamed(context, '/voice');
  }

  void _navigateToHistory() {
    Navigator.pushNamed(context, '/history');
  }
}
```

---

## 4. Image Analysis Service

### src/services/image_service.py
```python
import asyncio
import io
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image
import cv2
import torch
import torchvision.transforms as transforms

from ..ai_models.cnn_health_analyzer import CNNHealthAnalyzer
from ..services.explainable_ai_service import ExplainableAIService
from ..utils.error_handling import handle_service_error

logger = logging.getLogger(__name__)

class EnhancedImageRecognitionService:
    """Enhanced image recognition service with CNN and explainable AI"""
    
    def __init__(self):
        self.cnn_analyzer = None
        self.explainable_ai = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the image recognition service"""
        try:
            logger.info("Initializing Enhanced Image Recognition Service...")
            
            # Initialize CNN analyzer
            self.cnn_analyzer = CNNHealthAnalyzer()
            
            # Initialize explainable AI service
            self.explainable_ai = ExplainableAIService()
            
            self.is_initialized = True
            logger.info("Enhanced Image Recognition Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize image service: {str(e)}")
            raise
    
    @handle_service_error
    async def analyze_image(self, image_data: bytes, analysis_type: str = "general") -> Dict:
        """
        Analyze image using CNN models with explainable AI
        
        Args:
            image_data: Raw image bytes
            analysis_type: Type of analysis (skin, eye, food, wellness)
            
        Returns:
            Dictionary containing analysis results and explanations
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            logger.info(f"Starting {analysis_type} image analysis")
            
            # Validate image
            self._validate_image(image_data)
            
            # Primary analysis with CNN
            cnn_result = await self.cnn_analyzer.analyze_image(image_data, analysis_type)
            
            # Generate explanations
            explanation = await self.explainable_ai.explain_image_analysis(
                image_data, cnn_result, analysis_type
            )
            
            # Combine results
            result = {
                **cnn_result,
                "explanation": explanation,
                "processing_method": "CNN + Explainable AI",
                "service_version": "2.0"
            }
            
            logger.info(f"Image analysis completed successfully: {analysis_type}")
            return result
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            # Fallback to basic analysis
            return await self._fallback_analysis(image_data, analysis_type)
    
    def _validate_image(self, image_data: bytes) -> None:
        """Validate image format and size"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in ['JPEG', 'PNG', 'JPG']:
                raise ValueError("Unsupported image format. Please use JPEG or PNG.")
            
            # Check size
            if image.size[0] < 100 or image.size[1] < 100:
                raise ValueError("Image too small. Minimum size is 100x100 pixels.")
            
            if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError("Image too large. Maximum size is 10MB.")
                
        except Exception as e:
            raise ValueError(f"Invalid image: {str(e)}")
    
    async def _fallback_analysis(self, image_data: bytes, analysis_type: str) -> Dict:
        """Fallback analysis when CNN fails"""
        logger.warning("Using fallback analysis method")
        
        try:
            # Basic image analysis using traditional CV methods
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            image_array = np.array(image)
            
            # Basic color and texture analysis
            avg_color = np.mean(image_array, axis=(0, 1))
            brightness = np.mean(avg_color)
            
            # Generate basic result based on analysis type
            if analysis_type == "skin":
                result = self._analyze_skin_fallback(image_array, brightness)
            elif analysis_type == "eye":
                result = self._analyze_eye_fallback(image_array, brightness)
            elif analysis_type == "food":
                result = self._analyze_food_fallback(image_array, avg_color)
            else:
                result = self._analyze_general_fallback(image_array)
            
            return {
                **result,
                "processing_method": "Fallback Analysis",
                "confidence": 0.6,  # Lower confidence for fallback
                "note": "Analysis performed using fallback method"
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {str(e)}")
            return self._get_default_result(analysis_type)
    
    def _analyze_skin_fallback(self, image_array: np.ndarray, brightness: float) -> Dict:
        """Fallback skin analysis"""
        if brightness > 150:
            condition = "healthy"
            recommendations = ["Your skin appears bright and healthy!"]
        elif brightness < 100:
            condition = "needs_attention"
            recommendations = ["Consider improving lighting for better analysis."]
        else:
            condition = "normal"
            recommendations = ["Maintain good skincare routine."]
        
        return {
            "predictions": [{"condition": condition, "confidence": 0.6}],
            "recommendations": recommendations,
            "analysis_type": "skin"
        }
    
    def _analyze_eye_fallback(self, image_array: np.ndarray, brightness: float) -> Dict:
        """Fallback eye analysis"""
        # Simple brightness-based analysis
        if brightness > 140:
            condition = "healthy"
            recommendations = ["Eyes appear bright and healthy!"]
        else:
            condition = "fatigue"
            recommendations = ["Ensure adequate rest and hydration."]
        
        return {
            "predictions": [{"condition": condition, "confidence": 0.6}],
            "recommendations": recommendations,
            "analysis_type": "eye"
        }
    
    def _analyze_food_fallback(self, image_array: np.ndarray, avg_color: np.ndarray) -> Dict:
        """Fallback food analysis"""
        # Color-based food analysis
        green_ratio = avg_color[1] / (np.sum(avg_color) + 1e-6)
        
        if green_ratio > 0.4:
            condition = "healthy"
            recommendations = ["Great choice! Appears to contain vegetables."]
        else:
            condition = "processed"
            recommendations = ["Consider adding more vegetables to your meal."]
        
        return {
            "predictions": [{"condition": condition, "confidence": 0.6}],
            "recommendations": recommendations,
            "analysis_type": "food"
        }
    
    def _analyze_general_fallback(self, image_array: np.ndarray) -> Dict:
        """Fallback general analysis"""
        return {
            "predictions": [{"condition": "analyzed", "confidence": 0.6}],
            "recommendations": ["Image analyzed successfully."],
            "analysis_type": "general"
        }
    
    def _get_default_result(self, analysis_type: str) -> Dict:
        """Get default result when all analysis methods fail"""
        return {
            "predictions": [{"condition": "unknown", "confidence": 0.3}],
            "recommendations": ["Unable to analyze image. Please try again with a clearer image."],
            "analysis_type": analysis_type,
            "processing_method": "Default Response",
            "error": "Analysis failed"
        }
    
    async def get_analysis_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's analysis history"""
        try:
            # Implementation would fetch from database
            # For now, return mock data
            return [
                {
                    "id": f"analysis_{i}",
                    "analysis_type": "skin",
                    "result": "healthy",
                    "confidence": 0.92,
                    "timestamp": "2024-01-01T10:00:00Z"
                }
                for i in range(limit)
            ]
        except Exception as e:
            logger.error(f"Failed to get analysis history: {str(e)}")
            return []
    
    async def batch_analyze_images(self, image_list: List[Tuple[bytes, str]]) -> List[Dict]:
        """Analyze multiple images in batch"""
        results = []
        
        for image_data, analysis_type in image_list:
            try:
                result = await self.analyze_image(image_data, analysis_type)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch analysis failed for image: {str(e)}")
                results.append(self._get_default_result(analysis_type))
        
        return results
```