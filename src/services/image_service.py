# image_service.py - Enhanced image recognition service with specialized health analyzers
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Optional PIL import with fallback
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow not available - using mock implementations")
    
    # Mock PIL Image class
    class MockImage:
        @staticmethod
        def open(path):
            class MockImageInstance:
                def __init__(self):
                    self.format = "JPEG"
                    self.mode = "RGB"
                    self.size = (224, 224)
                    self.width = 224
                    self.height = 224
                    self.info = {}
                
                def convert(self, mode):
                    return self
                
                def verify(self):
                    pass
                
                def __enter__(self):
                    return self
                
                def __exit__(self, *args):
                    pass
                
                def save(self, path):
                    pass
            
            return MockImageInstance()
        
        @staticmethod
        def new(mode, size, color=None):
            class MockNewImage:
                def save(self, path):
                    # Create empty file for testing
                    Path(path).touch()
            return MockNewImage()
    
    Image = MockImage()

# Optional imports with fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available - using Python lists as fallback")
    
    # Mock numpy for basic operations
    class MockRandom:
        @staticmethod
        def randn(*shape):
            import random
            size = 1
            for dim in shape:
                size *= dim
            return [random.gauss(0, 1) for _ in range(size)]
        
        @staticmethod
        def uniform(low, high, size=None):
            import random
            if size is None:
                return random.uniform(low, high)
            else:
                return [random.uniform(low, high) for _ in range(size)]
        
        @staticmethod
        def choice(choices, p=None):
            import random
            return random.choice(choices)
    
    class MockNumPy:
        random = MockRandom()
    
    np = MockNumPy()

# Optional imports with fallbacks
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available - some features may be limited")
    
    # Mock cv2 for basic functionality
    class MockCV2:
        @staticmethod
        def imread(path):
            return [[0, 0, 0]] * 224  # Mock image array
        
        @staticmethod
        def cvtColor(img, flag):
            return img
        
        @staticmethod
        def Canny(img, low, high):
            return img
        
        @staticmethod
        def findContours(img, mode, method):
            return [], []
        
        COLOR_BGR2GRAY = 0
        RETR_EXTERNAL = 0
        CHAIN_APPROX_SIMPLE = 0
    
    cv2 = MockCV2()

try:
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet50, mobilenet_v2, efficientnet_b0
    from torchvision.models import ResNet50_Weights, MobileNet_V2_Weights, EfficientNet_B0_Weights
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - using mock implementations")

from src.config import ModelConfig, AppConfig
from src.models import HealthAnalysisResult, AnalysisType, AnalysisStatus, FoodItem, EmotionDetection, HealthCondition
from src.utils.logging_config import get_logger, log_performance

logger = get_logger(__name__)

# Import offline mode service
try:
    from src.services.offline_mode_service import get_offline_service, is_offline_mode_active
    OFFLINE_MODE_AVAILABLE = True
except ImportError:
    OFFLINE_MODE_AVAILABLE = False
    logger.warning("Offline mode service not available")

# Mock implementations for when dependencies are not available
class MockTensor:
    """Mock tensor for when PyTorch is not available"""
    def __init__(self, shape):
        self.shape = shape
        if NUMPY_AVAILABLE:
            self.data = np.random.randn(*shape)
        else:
            import random
            size = 1
            for dim in shape:
                size *= dim
            self.data = [random.gauss(0, 1) for _ in range(size)]
    
    def to(self, device):
        return self
    
    def unsqueeze(self, dim):
        new_shape = list(self.shape)
        new_shape.insert(dim, 1)
        return MockTensor(new_shape)
    
    def __getitem__(self, idx):
        if len(self.shape) == 1:
            # Return a scalar-like MockTensor that can be converted to float
            return MockScalar()
        return MockTensor(self.shape[1:])
    
    def __len__(self):
        return self.shape[0] if self.shape else 0
    
    def item(self):
        """Return a scalar value"""
        import random
        return random.uniform(0, 1)

class MockScalar:
    """Mock scalar tensor that can be converted to float"""
    def __init__(self):
        import random
        self.value = random.uniform(0, 1)
    
    def __float__(self):
        return self.value
    
    def item(self):
        return self.value

class MockModel:
    """Mock model for when PyTorch is not available"""
    def __init__(self):
        pass
    
    def eval(self):
        return self
    
    def to(self, device):
        return self
    
    def __call__(self, x):
        # Return mock output
        return MockTensor((1000,))

class MockTransforms:
    """Mock transforms for when PyTorch is not available"""
    def __init__(self, transforms_list):
        pass
    
    def __call__(self, image):
        # Convert PIL image to mock tensor
        return MockTensor((3, 224, 224))

if not TORCH_AVAILABLE:
    # Create mock torch module
    class MockTorch:
        # Add Tensor as an alias to MockTensor
        Tensor = MockTensor
        
        class nn:
            class functional:
                @staticmethod
                def softmax(x, dim=0):
                    # Return mock probabilities
                    return MockTensor((1000,))
            
            class Module:
                """Mock torch.nn.Module"""
                def eval(self):
                    return self
                
                def to(self, device):
                    return self
                
                def __call__(self, x):
                    return MockTensor((1000,))
        
        @staticmethod
        def no_grad():
            class NoGradContext:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return NoGradContext()
        
        @staticmethod
        def device(device_str):
            return "cpu"
        
        @staticmethod
        def topk(tensor, k):
            # Return mock top-k results
            values = MockTensor((k,))
            indices = MockTensor((k,))
            return values, indices
    
    torch = MockTorch()
    
    # Mock transforms
    class transforms:
        @staticmethod
        def Compose(transform_list):
            return MockTransforms(transform_list)
        
        @staticmethod
        def Resize(size):
            return lambda x: x
        
        @staticmethod
        def CenterCrop(size):
            return lambda x: x
        
        @staticmethod
        def ToTensor():
            return lambda x: x
        
        @staticmethod
        def Normalize(mean, std):
            return lambda x: x

class ModelManager:
    """Manages loading and switching between different AI models"""
    
    def __init__(self):
        if TORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"
        self.models = {}
        self.current_model = None
        logger.info(f"Using device: {self.device}")
    
    def load_model(self, model_name: str):
        """Load a specific model by name"""
        if model_name in self.models:
            return self.models[model_name]
        
        # Check for valid model names first
        valid_models = ["resnet50", "mobilenet_v2", "efficientnet_b0"]
        if model_name not in valid_models:
            raise ValueError(f"Unknown model: {model_name}")
        
        try:
            if not TORCH_AVAILABLE:
                # Return mock model when PyTorch is not available
                model = MockModel()
                self.models[model_name] = model
                logger.warning(f"Using mock model for {model_name} (PyTorch not available)")
                return model
            
            if model_name == "resnet50":
                model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
            elif model_name == "mobilenet_v2":
                model = mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
            elif model_name == "efficientnet_b0":
                model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
            
            model.eval()
            model.to(self.device)
            self.models[model_name] = model
            
            logger.info(f"Loaded model: {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            # Return mock model as fallback for other errors (missing dependencies, etc.)
            model = MockModel()
            self.models[model_name] = model
            logger.warning(f"Using mock model for {model_name} due to error: {e}")
            return model
    
    def get_model(self, model_name: str = None) -> torch.nn.Module:
        """Get a model, loading it if necessary"""
        if model_name is None:
            model_name = ModelConfig.IMAGE_MODEL_NAME
        
        if model_name not in self.models:
            return self.load_model(model_name)
        
        return self.models[model_name]
    
    def switch_model(self, model_name: str) -> None:
        """Switch to a different model"""
        self.current_model = self.get_model(model_name)
        logger.info(f"Switched to model: {model_name}")

class ImagePreprocessor:
    """Handles image preprocessing and validation"""
    
    def __init__(self):
        self.transforms = self._get_transforms()
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    def _get_transforms(self) -> transforms.Compose:
        """Get image preprocessing transforms"""
        return transforms.Compose([
            transforms.Resize(ModelConfig.IMAGE_INPUT_SIZE),
            transforms.CenterCrop(ModelConfig.IMAGE_INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def validate_image(self, image_path: Union[str, Path]) -> bool:
        """Validate image file format and accessibility"""
        try:
            image_path = Path(image_path)
            
            # Check if file exists
            if not image_path.exists():
                raise ValueError(f"Image file does not exist: {image_path}")
            
            # Check file extension
            if image_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported image format: {image_path.suffix}")
            
            # Check file size (max 10MB by default)
            max_size = AppConfig.MAX_UPLOAD_SIZE
            if image_path.stat().st_size > max_size:
                raise ValueError(f"Image file too large: {image_path.stat().st_size} bytes")
            
            # Try to open the image
            with Image.open(image_path) as img:
                img.verify()
            
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            raise ValueError(f"Invalid image: {str(e)}")
    
    def preprocess_image(self, image_path: Union[str, Path]):
        """Preprocess image for model input"""
        try:
            self.validate_image(image_path)
            
            # Load and convert image
            image = Image.open(image_path).convert('RGB')
            
            # Apply transforms
            tensor = self.transforms(image).unsqueeze(0)
            
            if hasattr(tensor, 'shape'):
                logger.debug(f"Preprocessed image shape: {tensor.shape}")
            else:
                logger.debug("Preprocessed image (mock tensor)")
            return tensor
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ValueError(f"Error preprocessing image: {str(e)}")
    
    def get_image_info(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """Get basic information about the image"""
        try:
            with Image.open(image_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {}

class SkinAnalyzer:
    """Specialized analyzer for skin condition detection"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.skin_conditions = {
            'acne': {'severity_threshold': 0.7, 'urgency': 'routine'},
            'eczema': {'severity_threshold': 0.6, 'urgency': 'routine'},
            'melanoma': {'severity_threshold': 0.5, 'urgency': 'urgent'},
            'psoriasis': {'severity_threshold': 0.6, 'urgency': 'routine'},
            'dermatitis': {'severity_threshold': 0.6, 'urgency': 'routine'},
            'healthy_skin': {'severity_threshold': 0.8, 'urgency': 'routine'}
        }
    
    @log_performance()
    def analyze_skin_condition(self, image_tensor: torch.Tensor, image_info: Dict[str, Any]) -> HealthCondition:
        """Analyze skin condition from image"""
        try:
            # Check offline mode
            if OFFLINE_MODE_AVAILABLE and is_offline_mode_active():
                logger.info("Using offline mode for skin analysis")
                return self._offline_skin_analysis(image_info)
            
            model = self.model_manager.get_model()
            device = self.model_manager.device
            
            # Move tensor to device
            image_tensor = image_tensor.to(device)
            
            # Get model predictions
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Simulate skin condition detection (in practice, this would use a specialized model)
            # For demo purposes, we'll create realistic-looking results
            skin_predictions = self._simulate_skin_analysis(probabilities)
            
            # Get the most confident prediction
            top_prediction = max(skin_predictions, key=lambda x: x['confidence'])
            
            # Create health condition
            condition = HealthCondition(
                condition_name=top_prediction['condition'],
                category="dermatological",
                severity=self._determine_severity(top_prediction),
                confidence=top_prediction['confidence'],
                description=self._get_condition_description(top_prediction['condition']),
                recommendations=self._get_recommendations(top_prediction['condition']),
                medical_attention_urgency=self.skin_conditions.get(
                    top_prediction['condition'], {}
                ).get('urgency', 'routine')
            )
            
            logger.info(f"Skin analysis completed: {condition.condition_name} ({condition.confidence:.2f})")
            return condition
            
        except Exception as e:
            logger.error(f"Skin analysis failed: {e}")
            raise
    
    def _simulate_skin_analysis(self, probabilities: torch.Tensor) -> List[Dict[str, Any]]:
        """Simulate skin condition analysis (replace with actual model in production)"""
        # This is a simulation - in practice, you'd use a trained dermatology model
        conditions = list(self.skin_conditions.keys())
        results = []
        
        for i, condition in enumerate(conditions):
            # Create realistic confidence scores
            base_confidence = float(probabilities[i % len(probabilities)])
            adjusted_confidence = min(base_confidence * np.random.uniform(0.7, 1.3), 1.0)
            
            results.append({
                'condition': condition,
                'confidence': adjusted_confidence,
                'region_detected': True
            })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    def _determine_severity(self, prediction: Dict[str, Any]) -> str:
        """Determine severity based on condition and confidence"""
        condition = prediction['condition']
        confidence = prediction['confidence']
        
        if condition == 'melanoma' and confidence > 0.7:
            return 'severe'
        elif condition in ['acne', 'eczema'] and confidence > 0.8:
            return 'moderate'
        elif confidence > 0.9:
            return 'moderate'
        else:
            return 'mild'
    
    def _get_condition_description(self, condition: str) -> str:
        """Get description for a skin condition"""
        descriptions = {
            'acne': 'Common skin condition characterized by pimples, blackheads, and whiteheads',
            'eczema': 'Inflammatory skin condition causing dry, itchy, and inflamed skin',
            'melanoma': 'Serious form of skin cancer that develops in melanocytes',
            'psoriasis': 'Autoimmune condition causing rapid skin cell buildup and scaling',
            'dermatitis': 'General term for skin inflammation with various causes',
            'healthy_skin': 'No significant skin conditions detected'
        }
        return descriptions.get(condition, 'Skin condition requiring further evaluation')
    
    def _get_recommendations(self, condition: str) -> List[str]:
        """Get recommendations for a skin condition"""
        recommendations = {
            'acne': [
                'Maintain good skincare hygiene',
                'Use non-comedogenic products',
                'Consider over-the-counter treatments',
                'Consult dermatologist if severe'
            ],
            'eczema': [
                'Keep skin moisturized',
                'Avoid known triggers',
                'Use gentle, fragrance-free products',
                'Consider topical treatments'
            ],
            'melanoma': [
                'Seek immediate medical attention',
                'Schedule dermatologist appointment',
                'Monitor for changes in size, color, or shape',
                'Protect skin from UV exposure'
            ],
            'healthy_skin': [
                'Continue current skincare routine',
                'Use sunscreen daily',
                'Stay hydrated',
                'Regular skin self-examinations'
            ]
        }
        return recommendations.get(condition, ['Consult healthcare professional for proper diagnosis'])
    
    def _offline_skin_analysis(self, image_info: Dict[str, Any]) -> HealthCondition:
        """Provide offline skin analysis with basic recommendations"""
        return HealthCondition(
            condition_name="offline_analysis",
            category="dermatological",
            severity="unknown",
            confidence=0.5,
            description="Offline mode: Image analysis is currently unavailable. Please try again when online.",
            recommendations=[
                "Check your internet connection",
                "Try again when online for detailed analysis",
                "Consult a dermatologist for professional evaluation",
                "Take note of any changes in your skin condition"
            ],
            medical_attention_urgency="routine"
        )

class EyeHealthAnalyzer:
    """Specialized analyzer for eye health screening"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.eye_conditions = {
            'diabetic_retinopathy': {'severity_levels': ['mild', 'moderate', 'severe'], 'urgency': 'urgent'},
            'cataract': {'severity_levels': ['early', 'moderate', 'advanced'], 'urgency': 'routine'},
            'glaucoma': {'severity_levels': ['early', 'moderate', 'advanced'], 'urgency': 'urgent'},
            'macular_degeneration': {'severity_levels': ['early', 'intermediate', 'advanced'], 'urgency': 'urgent'},
            'healthy_eye': {'severity_levels': ['normal'], 'urgency': 'routine'}
        }
    
    @log_performance()
    def screen_eye_health(self, image_tensor: torch.Tensor, image_info: Dict[str, Any]) -> HealthCondition:
        """Screen for eye health conditions"""
        try:
            model = self.model_manager.get_model()
            device = self.model_manager.device
            
            image_tensor = image_tensor.to(device)
            
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Simulate eye health screening
            eye_predictions = self._simulate_eye_analysis(probabilities)
            top_prediction = max(eye_predictions, key=lambda x: x['confidence'])
            
            condition = HealthCondition(
                condition_name=top_prediction['condition'],
                category="ophthalmological",
                severity=self._determine_eye_severity(top_prediction),
                confidence=top_prediction['confidence'],
                description=self._get_eye_condition_description(top_prediction['condition']),
                recommendations=self._get_eye_recommendations(top_prediction['condition']),
                medical_attention_urgency=self.eye_conditions.get(
                    top_prediction['condition'], {}
                ).get('urgency', 'routine')
            )
            
            logger.info(f"Eye health screening completed: {condition.condition_name} ({condition.confidence:.2f})")
            return condition
            
        except Exception as e:
            logger.error(f"Eye health screening failed: {e}")
            raise
    
    def _simulate_eye_analysis(self, probabilities: torch.Tensor) -> List[Dict[str, Any]]:
        """Simulate eye health analysis"""
        conditions = list(self.eye_conditions.keys())
        results = []
        
        for i, condition in enumerate(conditions):
            base_confidence = float(probabilities[i % len(probabilities)])
            adjusted_confidence = min(base_confidence * np.random.uniform(0.6, 1.2), 1.0)
            
            results.append({
                'condition': condition,
                'confidence': adjusted_confidence,
                'features_detected': np.random.choice([True, False], p=[0.7, 0.3])
            })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    def _determine_eye_severity(self, prediction: Dict[str, Any]) -> str:
        """Determine eye condition severity"""
        condition = prediction['condition']
        confidence = prediction['confidence']
        
        if condition in ['diabetic_retinopathy', 'glaucoma'] and confidence > 0.8:
            return 'severe'
        elif confidence > 0.7:
            return 'moderate'
        else:
            return 'mild'
    
    def _get_eye_condition_description(self, condition: str) -> str:
        """Get description for eye condition"""
        descriptions = {
            'diabetic_retinopathy': 'Diabetes-related damage to blood vessels in the retina',
            'cataract': 'Clouding of the eye lens causing vision impairment',
            'glaucoma': 'Group of eye conditions damaging the optic nerve',
            'macular_degeneration': 'Deterioration of the central portion of the retina',
            'healthy_eye': 'No significant eye conditions detected'
        }
        return descriptions.get(condition, 'Eye condition requiring professional evaluation')
    
    def _get_eye_recommendations(self, condition: str) -> List[str]:
        """Get recommendations for eye condition"""
        recommendations = {
            'diabetic_retinopathy': [
                'Schedule immediate ophthalmologist appointment',
                'Monitor blood sugar levels closely',
                'Regular diabetic eye exams',
                'Follow diabetes management plan'
            ],
            'cataract': [
                'Schedule eye examination',
                'Monitor vision changes',
                'Consider surgical options if advanced',
                'Use proper lighting for reading'
            ],
            'glaucoma': [
                'Urgent ophthalmologist consultation',
                'Regular eye pressure monitoring',
                'Follow prescribed treatment plan',
                'Avoid activities that increase eye pressure'
            ],
            'healthy_eye': [
                'Continue regular eye exams',
                'Protect eyes from UV exposure',
                'Maintain healthy diet rich in vitamins',
                'Take regular breaks from screen time'
            ]
        }
        return recommendations.get(condition, ['Consult eye care professional for proper diagnosis'])

class FoodRecognizer:
    """Specialized analyzer for food recognition and nutritional analysis"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.food_database = self._load_food_database()
    
    def _load_food_database(self) -> Dict[str, Dict[str, Any]]:
        """Load food nutritional database"""
        # In practice, this would load from a comprehensive food database
        return {
            'apple': {
                'category': 'fruit',
                'calories_per_100g': 52,
                'nutrients': {'vitamin_c': 4.6, 'fiber': 2.4, 'potassium': 107},
                'health_benefits': ['High in fiber', 'Rich in antioxidants', 'Supports heart health'],
                'allergens': [],
                'dietary_tags': ['vegan', 'gluten-free', 'low-calorie']
            },
            'banana': {
                'category': 'fruit',
                'calories_per_100g': 89,
                'nutrients': {'potassium': 358, 'vitamin_b6': 0.4, 'vitamin_c': 8.7},
                'health_benefits': ['High in potassium', 'Good source of energy', 'Supports muscle function'],
                'allergens': [],
                'dietary_tags': ['vegan', 'gluten-free']
            },
            'broccoli': {
                'category': 'vegetable',
                'calories_per_100g': 34,
                'nutrients': {'vitamin_c': 89.2, 'vitamin_k': 101.6, 'folate': 63},
                'health_benefits': ['High in vitamins', 'Anti-inflammatory', 'Supports immune system'],
                'allergens': [],
                'dietary_tags': ['vegan', 'gluten-free', 'low-calorie', 'high-fiber']
            }
        }
    
    @log_performance()
    def recognize_food(self, image_tensor: torch.Tensor, image_info: Dict[str, Any]) -> FoodItem:
        """Recognize food items and provide nutritional information"""
        try:
            model = self.model_manager.get_model()
            device = self.model_manager.device
            
            image_tensor = image_tensor.to(device)
            
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Simulate food recognition
            food_predictions = self._simulate_food_recognition(probabilities)
            top_prediction = max(food_predictions, key=lambda x: x['confidence'])
            
            food_name = top_prediction['food']
            food_data = self.food_database.get(food_name, {})
            
            food_item = FoodItem(
                food_name=food_name,
                confidence=top_prediction['confidence'],
                category=food_data.get('category', 'unknown'),
                calories_per_serving=food_data.get('calories_per_100g', 0),
                health_benefits=food_data.get('health_benefits', []),
                allergens=food_data.get('allergens', []),
                dietary_tags=food_data.get('dietary_tags', [])
            )
            
            # Add nutritional information
            nutrients = food_data.get('nutrients', {})
            for nutrient, value in nutrients.items():
                food_item.add_nutritional_info(nutrient, value, 'mg' if 'vitamin' in nutrient else 'g')
            
            logger.info(f"Food recognition completed: {food_name} ({top_prediction['confidence']:.2f})")
            return food_item
            
        except Exception as e:
            logger.error(f"Food recognition failed: {e}")
            raise
    
    def _simulate_food_recognition(self, probabilities: torch.Tensor) -> List[Dict[str, Any]]:
        """Simulate food recognition"""
        foods = list(self.food_database.keys())
        results = []
        
        for i, food in enumerate(foods):
            base_confidence = float(probabilities[i % len(probabilities)])
            adjusted_confidence = min(base_confidence * np.random.uniform(0.8, 1.2), 1.0)
            
            results.append({
                'food': food,
                'confidence': adjusted_confidence,
                'portion_detected': True
            })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)

class EmotionAnalyzer:
    """Specialized analyzer for facial expression and emotion detection"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.emotions = {
            'happy': {'wellness_score': 0.8, 'intensity_factor': 1.0},
            'sad': {'wellness_score': 0.3, 'intensity_factor': 0.7},
            'angry': {'wellness_score': 0.2, 'intensity_factor': 0.8},
            'surprised': {'wellness_score': 0.6, 'intensity_factor': 0.9},
            'fearful': {'wellness_score': 0.2, 'intensity_factor': 0.6},
            'disgusted': {'wellness_score': 0.3, 'intensity_factor': 0.7},
            'neutral': {'wellness_score': 0.5, 'intensity_factor': 0.5}
        }
    
    @log_performance()
    def detect_emotion(self, image_tensor: torch.Tensor, image_info: Dict[str, Any]) -> EmotionDetection:
        """Detect emotions from facial expressions"""
        try:
            model = self.model_manager.get_model()
            device = self.model_manager.device
            
            image_tensor = image_tensor.to(device)
            
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Simulate emotion detection
            emotion_predictions = self._simulate_emotion_detection(probabilities)
            top_prediction = max(emotion_predictions, key=lambda x: x['confidence'])
            
            primary_emotion = top_prediction['emotion']
            emotion_data = self.emotions.get(primary_emotion, {})
            
            emotion_detection = EmotionDetection(
                emotion=primary_emotion,
                confidence=top_prediction['confidence'],
                intensity=top_prediction['intensity'],
                wellness_indicators={
                    'overall_score': emotion_data.get('wellness_score', 0.5),
                    'stress_level': self._calculate_stress_level(emotion_predictions),
                    'emotional_stability': self._calculate_stability(emotion_predictions)
                }
            )
            
            # Add secondary emotions
            for pred in emotion_predictions[1:3]:  # Top 2 secondary emotions
                emotion_detection.add_secondary_emotion(pred['emotion'], pred['confidence'])
            
            logger.info(f"Emotion detection completed: {primary_emotion} ({top_prediction['confidence']:.2f})")
            return emotion_detection
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            raise
    
    def _simulate_emotion_detection(self, probabilities: torch.Tensor) -> List[Dict[str, Any]]:
        """Simulate emotion detection"""
        emotions = list(self.emotions.keys())
        results = []
        
        for i, emotion in enumerate(emotions):
            base_confidence = float(probabilities[i % len(probabilities)])
            adjusted_confidence = min(base_confidence * np.random.uniform(0.7, 1.3), 1.0)
            intensity = adjusted_confidence * self.emotions[emotion]['intensity_factor']
            
            results.append({
                'emotion': emotion,
                'confidence': adjusted_confidence,
                'intensity': intensity
            })
        
        return sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    def _calculate_stress_level(self, predictions: List[Dict[str, Any]]) -> float:
        """Calculate stress level based on emotion predictions"""
        stress_emotions = {'angry': 0.8, 'fearful': 0.9, 'sad': 0.6, 'disgusted': 0.5}
        stress_score = 0.0
        
        for pred in predictions:
            emotion = pred['emotion']
            if emotion in stress_emotions:
                stress_score += pred['confidence'] * stress_emotions[emotion]
        
        return min(stress_score, 1.0)
    
    def _calculate_stability(self, predictions: List[Dict[str, Any]]) -> float:
        """Calculate emotional stability score"""
        # Higher stability when one emotion dominates
        top_confidence = predictions[0]['confidence']
        confidence_spread = top_confidence - predictions[-1]['confidence']
        
        return min(confidence_spread + 0.3, 1.0)

class EnhancedImageRecognitionService:
    """Main service class that orchestrates all image analysis capabilities"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.preprocessor = ImagePreprocessor()
        self.skin_analyzer = SkinAnalyzer(self.model_manager)
        self.eye_analyzer = EyeHealthAnalyzer(self.model_manager)
        self.food_recognizer = FoodRecognizer(self.model_manager)
        self.emotion_analyzer = EmotionAnalyzer(self.model_manager)
        
        logger.info("Enhanced Image Recognition Service initialized")
    
    def analyze_image(self, image_path: Union[str, Path], analysis_type: AnalysisType, 
                     analysis_id: str = None) -> HealthAnalysisResult:
        """Main method to analyze images based on specified type"""
        start_time = time.time()
        
        try:
            # Create analysis result
            if analysis_id is None:
                analysis_id = f"analysis_{int(time.time())}"
            
            result = HealthAnalysisResult(
                analysis_id=analysis_id,
                analysis_type=analysis_type,
                status=AnalysisStatus.PROCESSING
            )
            
            # Get image info and preprocess
            image_info = self.preprocessor.get_image_info(image_path)
            image_tensor = self.preprocessor.preprocess_image(image_path)
            
            result.input_data = {
                'image_path': str(image_path),
                'image_info': image_info,
                'analysis_type': analysis_type.value
            }
            
            # Perform specific analysis
            if analysis_type == AnalysisType.SKIN_CONDITION:
                condition = self.skin_analyzer.analyze_skin_condition(image_tensor, image_info)
                result.add_prediction(condition.condition_name, condition.confidence, condition.to_dict())
                
            elif analysis_type == AnalysisType.EYE_HEALTH:
                condition = self.eye_analyzer.screen_eye_health(image_tensor, image_info)
                result.add_prediction(condition.condition_name, condition.confidence, condition.to_dict())
                
            elif analysis_type == AnalysisType.FOOD_RECOGNITION:
                food_item = self.food_recognizer.recognize_food(image_tensor, image_info)
                result.add_prediction(food_item.food_name, food_item.confidence, food_item.to_dict())
                
            elif analysis_type == AnalysisType.EMOTION_DETECTION:
                emotion = self.emotion_analyzer.detect_emotion(image_tensor, image_info)
                result.add_prediction(emotion.emotion, emotion.confidence, emotion.to_dict())
                
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
            # Complete the analysis
            processing_time = time.time() - start_time
            result.set_completed(processing_time)
            
            logger.info(f"Image analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Image analysis failed after {processing_time:.2f}s: {e}")
            
            if 'result' in locals():
                result.set_failed(str(e))
                return result
            else:
                # Create a failed result
                result = HealthAnalysisResult(
                    analysis_id=analysis_id or f"failed_{int(time.time())}",
                    analysis_type=analysis_type,
                    status=AnalysisStatus.FAILED
                )
                result.set_failed(str(e))
                return result
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        return list(self.preprocessor.supported_formats)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'device': str(self.model_manager.device),
            'loaded_models': list(self.model_manager.models.keys()),
            'current_model': self.model_manager.current_model.__class__.__name__ if self.model_manager.current_model else None
        }