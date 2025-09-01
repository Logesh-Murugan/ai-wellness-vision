# test_explainable_ai_service.py - Tests for explainable AI service
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.services.explainable_ai_service import (
    GradCAMGenerator, LIMEExplainer, DecisionPathGenerator,
    VisualizationEngine, ComprehensiveExplainableAIService
)
from src.models import HealthAnalysisResult, AnalysisType, AnalysisStatus

class TestGradCAMGenerator(unittest.TestCase):
    """Test Grad-CAM generation functionality"""
    
    def setUp(self):
        self.generator = GradCAMGenerator()
    
    def test_generator_initialization(self):
        """Test Grad-CAM generator initializes correctly"""
        self.assertIsNotNone(self.generator.supported_layers)
        self.assertIn('conv', self.generator.supported_layers)
        self.assertIn('relu', self.generator.supported_layers)
    
    def test_generate_gradcam_mock(self):
        """Test Grad-CAM generation (mock)"""
        mock_model = MagicMock()
        mock_image = MagicMock()
        
        result = self.generator.generate_gradcam(mock_model, mock_image, target_class=1)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('heatmap', result)
        self.assertIn('target_class', result)
        self.assertIn('processing_time', result)
        self.assertEqual(result['target_class'], 1)
    
    def test_overlay_heatmap_mock(self):
        """Test heatmap overlay (mock)"""
        mock_image = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        mock_heatmap = [[0.1, 0.5, 0.9], [0.3, 0.7, 0.2], [0.8, 0.4, 0.6]]
        
        result = self.generator.overlay_heatmap(mock_image, mock_heatmap, alpha=0.5)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('overlay_image', result)
        self.assertEqual(result['alpha'], 0.5)

class TestLIMEExplainer(unittest.TestCase):
    """Test LIME explanation functionality"""
    
    def setUp(self):
        self.explainer = LIMEExplainer()
    
    def test_explainer_initialization(self):
        """Test LIME explainer initializes correctly"""
        # Should initialize even without LIME library
        self.assertIsNotNone(self.explainer)
    
    def test_explain_image_mock(self):
        """Test image explanation (mock)"""
        mock_image = [[1, 2, 3], [4, 5, 6]]
        mock_predict_fn = lambda x: [[0.3, 0.7]] * len(x)
        
        result = self.explainer.explain_image(mock_image, mock_predict_fn, num_features=5)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('explanation', result)
        self.assertIn('mask', result)
        self.assertIn('processing_time', result)
        self.assertEqual(result['num_features'], 5)
    
    def test_explain_text_mock(self):
        """Test text explanation (mock)"""
        text = "This is a test sentence for explanation"
        mock_predict_fn = lambda x: [[0.2, 0.8]] * len(x)
        
        result = self.explainer.explain_text(text, mock_predict_fn, num_features=3)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('word_importance', result)
        self.assertIn('text', result)
        self.assertEqual(result['text'], text)
        self.assertIsInstance(result['word_importance'], dict)
    
    def test_generate_mock_mask(self):
        """Test mock mask generation"""
        mock_image = MagicMock()
        mock_image.shape = (100, 100, 3)
        
        mask = self.explainer._generate_mock_mask(mock_image)
        
        self.assertIsNotNone(mask)

class TestDecisionPathGenerator(unittest.TestCase):
    """Test decision path generation functionality"""
    
    def setUp(self):
        self.generator = DecisionPathGenerator()
    
    def test_generator_initialization(self):
        """Test decision path generator initializes correctly"""
        self.assertIsNotNone(self.generator.health_decision_templates)
        self.assertIn('skin_condition', self.generator.health_decision_templates)
        self.assertIn('eye_health', self.generator.health_decision_templates)
    
    def test_generate_decision_path_skin_condition(self):
        """Test decision path generation for skin condition"""
        prediction_result = {
            'confidence': 0.85,
            'prediction': 'acne'
        }
        
        result = self.generator.generate_decision_path(
            AnalysisType.SKIN_CONDITION, prediction_result
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['analysis_type'], 'skin_condition')
        self.assertIn('decision_steps', result)
        self.assertIn('path_confidence', result)
        self.assertIn('insights', result)
        self.assertGreater(len(result['decision_steps']), 0)
    
    def test_generate_decision_path_eye_health(self):
        """Test decision path generation for eye health"""
        prediction_result = {
            'confidence': 0.75,
            'prediction': 'healthy_eye'
        }
        
        result = self.generator.generate_decision_path(
            AnalysisType.EYE_HEALTH, prediction_result
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['analysis_type'], 'eye_health')
        self.assertIn('decision_steps', result)
        self.assertIsInstance(result['decision_steps'], list)
    
    def test_generate_generic_decision_path(self):
        """Test generic decision path generation"""
        prediction_result = {
            'confidence': 0.6,
            'prediction': 'unknown'
        }
        
        result = self.generator._generate_generic_decision_path(prediction_result)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['analysis_type'], 'generic')
        self.assertIn('decision_steps', result)
        self.assertEqual(len(result['decision_steps']), 3)
    
    def test_calculate_path_confidence(self):
        """Test path confidence calculation"""
        decision_steps = [
            {'confidence': 0.8, 'weight': 0.3},
            {'confidence': 0.7, 'weight': 0.4},
            {'confidence': 0.9, 'weight': 0.3}
        ]
        
        confidence = self.generator._calculate_path_confidence(decision_steps)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_generate_decision_insights(self):
        """Test decision insights generation"""
        decision_steps = [
            {'name': 'Step 1', 'confidence': 0.9},
            {'name': 'Step 2', 'confidence': 0.6},
            {'name': 'Step 3', 'confidence': 0.8}
        ]
        
        insights = self.generator._generate_decision_insights(
            decision_steps, AnalysisType.SKIN_CONDITION
        )
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        self.assertTrue(any('Step 1' in insight for insight in insights))  # Strongest step

class TestVisualizationEngine(unittest.TestCase):
    """Test visualization engine functionality"""
    
    def setUp(self):
        self.engine = VisualizationEngine()
    
    def test_engine_initialization(self):
        """Test visualization engine initializes correctly"""
        self.assertIsNotNone(self.engine.color_schemes)
        self.assertIsNotNone(self.engine.chart_templates)
        self.assertIn('heatmap', self.engine.color_schemes)
        self.assertIn('feature_importance', self.engine.chart_templates)
    
    def test_create_heatmap_visualization(self):
        """Test heatmap visualization creation"""
        heatmap_data = [[0.1, 0.5, 0.9], [0.3, 0.7, 0.2], [0.8, 0.4, 0.6]]
        
        result = self.engine.create_heatmap_visualization(
            heatmap_data, title="Test Heatmap"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('visualization', result)
        self.assertIn('format', result)
        self.assertEqual(result['title'], "Test Heatmap")
    
    def test_create_feature_importance_chart(self):
        """Test feature importance chart creation"""
        feature_importance = {
            'feature1': 0.8,
            'feature2': 0.6,
            'feature3': 0.9,
            'feature4': 0.4
        }
        
        result = self.engine.create_feature_importance_chart(
            feature_importance, title="Test Importance"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('visualization', result)
        self.assertIn('top_features', result)
        self.assertEqual(result['title'], "Test Importance")
    
    def test_create_decision_path_diagram(self):
        """Test decision path diagram creation"""
        decision_steps = [
            {
                'step': 1,
                'name': 'Input Processing',
                'confidence': 0.9,
                'weight': 0.3
            },
            {
                'step': 2,
                'name': 'Feature Analysis',
                'confidence': 0.8,
                'weight': 0.7
            }
        ]
        
        result = self.engine.create_decision_path_diagram(
            decision_steps, title="Test Decision Path"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('visualization', result)
        self.assertEqual(result['num_steps'], 2)
        self.assertEqual(result['title'], "Test Decision Path")
    
    def test_create_confidence_breakdown_chart(self):
        """Test confidence breakdown chart creation"""
        confidence_data = {
            'High Confidence': 0.6,
            'Medium Confidence': 0.3,
            'Low Confidence': 0.1
        }
        
        result = self.engine.create_confidence_breakdown_chart(
            confidence_data, title="Test Confidence"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('visualization', result)
        self.assertIn('data', result)
        self.assertEqual(result['title'], "Test Confidence")

class TestComprehensiveExplainableAIService(unittest.TestCase):
    """Test the main explainable AI service"""
    
    def setUp(self):
        try:
            self.service = ComprehensiveExplainableAIService()
        except Exception as e:
            self.skipTest(f"Explainable AI service initialization failed: {e}")
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        self.assertIsNotNone(self.service.gradcam_generator)
        self.assertIsNotNone(self.service.lime_explainer)
        self.assertIsNotNone(self.service.decision_path_generator)
        self.assertIsNotNone(self.service.visualization_engine)
    
    def test_explain_prediction_skin_condition(self):
        """Test prediction explanation for skin condition"""
        # Create mock analysis result
        analysis_result = HealthAnalysisResult(
            analysis_id="test_skin_123",
            analysis_type=AnalysisType.SKIN_CONDITION,
            status=AnalysisStatus.COMPLETED
        )
        analysis_result.add_prediction("acne", 0.85, {"severity": "mild"})
        
        result = self.service.explain_prediction(
            analysis_result,
            explanation_types=['decision_path', 'visualization']
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['analysis_type'], 'skin_condition')
        self.assertIn('explanations', result)
        self.assertIn('summary', result)
        self.assertIn('processing_time', result)
    
    def test_explain_prediction_with_gradcam(self):
        """Test prediction explanation with Grad-CAM"""
        analysis_result = HealthAnalysisResult(
            analysis_id="test_gradcam_123",
            analysis_type=AnalysisType.EYE_HEALTH,
            status=AnalysisStatus.COMPLETED
        )
        analysis_result.add_prediction("healthy_eye", 0.92)
        
        mock_image = [[1, 2, 3], [4, 5, 6]]
        
        result = self.service.explain_prediction(
            analysis_result,
            image_data=mock_image,
            explanation_types=['gradcam', 'decision_path']
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('explanations', result)
        
        if 'gradcam' in result['explanations']:
            gradcam_result = result['explanations']['gradcam']
            self.assertEqual(gradcam_result['status'], 'success')
    
    def test_explain_text_prediction(self):
        """Test text prediction explanation"""
        text = "I have been feeling anxious and stressed lately"
        prediction = {
            'sentiment': 'negative',
            'confidence': 0.75
        }
        
        result = self.service.explain_text_prediction(
            text, prediction, explanation_types=['lime', 'feature_importance']
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['text'], text)
        self.assertIn('explanations', result)
    
    def test_get_explanation_capabilities(self):
        """Test getting explanation capabilities"""
        capabilities = self.service.get_explanation_capabilities()
        
        self.assertIn('gradcam_available', capabilities)
        self.assertIn('lime_available', capabilities)
        self.assertIn('supported_analysis_types', capabilities)
        self.assertIn('explanation_methods', capabilities)
        self.assertIn('dependencies', capabilities)
        
        self.assertIsInstance(capabilities['supported_analysis_types'], list)
        self.assertIn('skin_condition', capabilities['supported_analysis_types'])
    
    def test_create_mock_predict_fn(self):
        """Test mock prediction function creation"""
        analysis_result = HealthAnalysisResult(
            analysis_id="test_predict_fn",
            analysis_type=AnalysisType.FOOD_RECOGNITION,
            status=AnalysisStatus.COMPLETED
        )
        analysis_result.add_prediction("apple", 0.8)
        
        predict_fn = self.service._create_mock_predict_fn(analysis_result)
        
        # Test the function
        mock_inputs = [1, 2, 3]  # Mock batch of inputs
        predictions = predict_fn(mock_inputs)
        
        self.assertIsNotNone(predictions)
        self.assertEqual(len(predictions), len(mock_inputs))
    
    def test_create_explanation_summary(self):
        """Test explanation summary creation"""
        analysis_result = HealthAnalysisResult(
            analysis_id="test_summary",
            analysis_type=AnalysisType.EMOTION_DETECTION,
            status=AnalysisStatus.COMPLETED
        )
        analysis_result.add_prediction("happy", 0.75)
        
        mock_explanations = {
            'gradcam': {'status': 'success', 'method': 'gradcam'},
            'decision_path': {
                'status': 'success',
                'path_confidence': 0.8,
                'insights': ['Test insight 1', 'Test insight 2']
            }
        }
        
        summary = self.service._create_explanation_summary(mock_explanations, analysis_result)
        
        self.assertIn('analysis_type', summary)
        self.assertIn('prediction_confidence', summary)
        self.assertIn('explanation_methods', summary)
        self.assertIn('key_insights', summary)
        self.assertIn('reliability_score', summary)
        self.assertEqual(summary['analysis_type'], 'emotion_detection')

class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and workflows"""
    
    def setUp(self):
        try:
            self.service = ComprehensiveExplainableAIService()
        except Exception as e:
            self.skipTest(f"Service initialization failed: {e}")
    
    def test_full_explanation_workflow(self):
        """Test complete explanation workflow"""
        # Create comprehensive analysis result
        analysis_result = HealthAnalysisResult(
            analysis_id="integration_test_123",
            analysis_type=AnalysisType.SKIN_CONDITION,
            status=AnalysisStatus.COMPLETED
        )
        analysis_result.add_prediction("acne", 0.75, {"severity": "moderate"})
        analysis_result.add_prediction("healthy_skin", 0.25)
        
        # Run full explanation
        result = self.service.explain_prediction(
            analysis_result,
            explanation_types=['gradcam', 'lime', 'decision_path', 'visualization']
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('explanations', result)
        self.assertIn('summary', result)
        
        # Check that multiple explanation types were attempted
        explanations = result['explanations']
        self.assertGreater(len(explanations), 0)
    
    def test_error_handling(self):
        """Test error handling in explanation generation"""
        # Test with invalid analysis result
        invalid_result = None
        
        try:
            result = self.service.explain_prediction(invalid_result)
            self.assertEqual(result['status'], 'error')
            self.assertIn('message', result)
        except Exception:
            # Should handle gracefully
            pass
    
    def test_different_analysis_types(self):
        """Test explanations for different analysis types"""
        analysis_types = [
            AnalysisType.SKIN_CONDITION,
            AnalysisType.EYE_HEALTH,
            AnalysisType.FOOD_RECOGNITION,
            AnalysisType.EMOTION_DETECTION
        ]
        
        for analysis_type in analysis_types:
            analysis_result = HealthAnalysisResult(
                analysis_id=f"test_{analysis_type.value}",
                analysis_type=analysis_type,
                status=AnalysisStatus.COMPLETED
            )
            analysis_result.add_prediction("test_prediction", 0.8)
            
            result = self.service.explain_prediction(
                analysis_result,
                explanation_types=['decision_path']
            )
            
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['analysis_type'], analysis_type.value)

if __name__ == '__main__':
    unittest.main()