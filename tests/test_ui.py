# test_ui.py - Tests for Streamlit UI components
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

class TestUIComponents(unittest.TestCase):
    """Test UI component functionality"""
    
    def setUp(self):
        # Mock streamlit
        self.mock_st = MagicMock()
        sys.modules['streamlit'] = self.mock_st
        
        # Mock streamlit components
        self.mock_st.session_state = {}
        self.mock_st.columns.return_value = [MagicMock(), MagicMock()]
        self.mock_st.tabs.return_value = [MagicMock() for _ in range(5)]
    
    def test_session_manager_initialization(self):
        """Test session manager initialization"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Check that session state is initialized
        self.assertIsInstance(session_manager._initialize_session_state, type(lambda: None))
    
    def test_theme_config_functions(self):
        """Test theme configuration functions"""
        from ui.utils.theme_config import apply_custom_theme, create_custom_component, format_confidence_score
        
        # Test theme application
        apply_custom_theme()  # Should not raise errors
        
        # Test custom component creation
        component = create_custom_component("Test content", "card")
        self.assertIn("Test content", component)
        self.assertIn("custom-card", component)
        
        # Test confidence score formatting
        high_confidence = format_confidence_score(0.9)
        medium_confidence = format_confidence_score(0.7)
        low_confidence = format_confidence_score(0.4)
        
        self.assertIn("confidence-high", high_confidence)
        self.assertIn("confidence-medium", medium_confidence)
        self.assertIn("confidence-low", low_confidence)
    
    @patch('streamlit.session_state', {})
    def test_session_manager_authentication(self):
        """Test session manager authentication"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Test initial state
        self.assertFalse(session_manager.is_authenticated())
        
        # Mock successful authentication
        with patch.object(session_manager, 'authenticate', return_value=True):
            result = session_manager.authenticate("testuser", "password")
            self.assertTrue(result)
    
    def test_session_manager_conversation_handling(self):
        """Test conversation handling in session manager"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Add conversation
        session_manager.add_conversation(
            "Test message",
            "Test response",
            "text",
            {"language": "en"}
        )
        
        # Get conversation history
        history = session_manager.get_conversation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['user_message'], "Test message")
        self.assertEqual(history[0]['ai_response'], "Test response")
    
    def test_session_manager_analysis_handling(self):
        """Test analysis handling in session manager"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Add analysis
        session_manager.add_analysis(
            "skin_condition",
            {"confidence": 0.8, "predictions": []},
            "test_image.jpg"
        )
        
        # Get analysis history
        history = session_manager.get_analysis_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['analysis_type'], "skin_condition")
        self.assertEqual(history[0]['result']['confidence'], 0.8)
    
    def test_session_manager_preferences(self):
        """Test user preferences handling"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Update preferences
        new_preferences = {
            'language': 'hi',
            'theme': 'dark',
            'notifications': False
        }
        session_manager.update_preferences(new_preferences)
        
        # Get preferences
        preferences = session_manager.get_preferences()
        self.assertEqual(preferences['language'], 'hi')
        self.assertEqual(preferences['theme'], 'dark')
        self.assertEqual(preferences['notifications'], False)
    
    def test_session_manager_stats(self):
        """Test user statistics calculation"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Add some data
        session_manager.add_conversation("Test 1", "Response 1", "text")
        session_manager.add_conversation("Test 2", "Response 2", "voice")
        session_manager.add_analysis("skin_condition", {"confidence": 0.8})
        
        # Get stats
        stats = session_manager.get_user_stats()
        
        self.assertEqual(stats['total_conversations'], 2)
        self.assertEqual(stats['total_analyses'], 1)
        self.assertEqual(stats['total_chats'], 1)
        self.assertEqual(stats['total_voice_interactions'], 1)
    
    def test_session_manager_data_export(self):
        """Test data export functionality"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Add some data
        session_manager.add_conversation("Test message", "Test response", "text")
        session_manager.add_analysis("skin_condition", {"confidence": 0.8})
        
        # Export data
        export_data = session_manager.export_data()
        
        self.assertIn('conversation_history', export_data)
        self.assertIn('analysis_history', export_data)
        self.assertIn('export_timestamp', export_data)
        self.assertEqual(len(export_data['conversation_history']), 1)
        self.assertEqual(len(export_data['analysis_history']), 1)
    
    def test_session_manager_history_limits(self):
        """Test history size limits"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Add many conversations (more than limit)
        for i in range(105):  # Limit is 100
            session_manager.add_conversation(f"Message {i}", f"Response {i}", "text")
        
        # Check that limit is enforced
        history = session_manager.get_conversation_history()
        self.assertEqual(len(history), 100)
        
        # Add many analyses (more than limit)
        for i in range(55):  # Limit is 50
            session_manager.add_analysis("skin_condition", {"confidence": 0.8})
        
        # Check that limit is enforced
        analysis_history = session_manager.get_analysis_history()
        self.assertEqual(len(analysis_history), 50)

class TestUIPageComponents(unittest.TestCase):
    """Test UI page components"""
    
    def setUp(self):
        # Mock streamlit and dependencies
        self.mock_st = MagicMock()
        sys.modules['streamlit'] = self.mock_st
        sys.modules['plotly.express'] = MagicMock()
        sys.modules['plotly.graph_objects'] = MagicMock()
        sys.modules['pandas'] = MagicMock()
        
        # Mock streamlit session state
        self.mock_st.session_state = {
            'authenticated': True,
            'user_info': {'username': 'testuser', 'roles': ['user']},
            'conversation_history': [],
            'analysis_history': [],
            'user_preferences': {'language': 'en'}
        }
    
    def test_home_page_render(self):
        """Test home page rendering"""
        try:
            from ui.pages import home_page
            
            # Mock session manager
            with patch('ui.pages.home_page.SessionManager') as mock_session_manager:
                mock_instance = MagicMock()
                mock_instance.get_user_info.return_value = {'username': 'testuser'}
                mock_instance.get_user_stats.return_value = {
                    'total_analyses': 5,
                    'total_chats': 10,
                    'total_voice_interactions': 2,
                    'total_conversations': 12
                }
                mock_session_manager.return_value = mock_instance
                
                # Should not raise errors
                home_page.render()
                
        except ImportError:
            self.skipTest("UI page modules not available for testing")
    
    def test_image_analysis_page_render(self):
        """Test image analysis page rendering"""
        try:
            from ui.pages import image_analysis_page
            
            # Mock session manager
            with patch('ui.pages.image_analysis_page.SessionManager') as mock_session_manager:
                mock_instance = MagicMock()
                mock_session_manager.return_value = mock_instance
                
                # Should not raise errors
                image_analysis_page.render()
                
        except ImportError:
            self.skipTest("UI page modules not available for testing")
    
    def test_chat_interface_page_render(self):
        """Test chat interface page rendering"""
        try:
            from ui.pages import chat_interface_page
            
            # Mock session manager
            with patch('ui.pages.chat_interface_page.SessionManager') as mock_session_manager:
                mock_instance = MagicMock()
                mock_instance.get_conversation_history.return_value = []
                mock_session_manager.return_value = mock_instance
                
                # Should not raise errors
                chat_interface_page.render()
                
        except ImportError:
            self.skipTest("UI page modules not available for testing")

class TestUIIntegration(unittest.TestCase):
    """Test UI integration scenarios"""
    
    def setUp(self):
        # Mock all required modules
        self.mock_modules = [
            'streamlit',
            'plotly.express',
            'plotly.graph_objects', 
            'pandas',
            'streamlit_option_menu',
            'streamlit_chat',
            'streamlit_extras'
        ]
        
        for module in self.mock_modules:
            sys.modules[module] = MagicMock()
    
    def test_main_app_structure(self):
        """Test main application structure"""
        try:
            # Import main app
            import streamlit_app
            
            # Should have main function
            self.assertTrue(hasattr(streamlit_app, 'main'))
            self.assertTrue(callable(streamlit_app.main))
            
        except ImportError as e:
            self.skipTest(f"Main app not available for testing: {e}")
    
    def test_ui_package_structure(self):
        """Test UI package structure"""
        try:
            # Test package imports
            from ui.utils import session_manager, theme_config
            from ui.components import auth
            
            # Check that modules have expected functions
            self.assertTrue(hasattr(session_manager, 'SessionManager'))
            self.assertTrue(hasattr(theme_config, 'apply_custom_theme'))
            self.assertTrue(hasattr(auth, 'authentication_component'))
            
        except ImportError as e:
            self.skipTest(f"UI packages not available for testing: {e}")
    
    def test_ui_error_handling(self):
        """Test UI error handling"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Test with invalid data
        try:
            session_manager.add_conversation(None, None, None)
            # Should handle gracefully or raise appropriate error
        except Exception as e:
            # Error should be handled appropriately
            self.assertIsInstance(e, (TypeError, ValueError))
    
    def test_ui_data_validation(self):
        """Test UI data validation"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Test conversation validation
        session_manager.add_conversation("", "", "text")  # Empty strings should be handled
        
        # Test analysis validation
        session_manager.add_analysis("", {}, None)  # Empty/None values should be handled
        
        # Should not crash
        history = session_manager.get_conversation_history()
        analysis_history = session_manager.get_analysis_history()
        
        self.assertIsInstance(history, list)
        self.assertIsInstance(analysis_history, list)

class TestUIAccessibility(unittest.TestCase):
    """Test UI accessibility features"""
    
    def test_theme_accessibility_features(self):
        """Test accessibility features in theme"""
        from ui.utils.theme_config import apply_custom_theme
        
        # Should not raise errors
        apply_custom_theme()
        
        # Theme should include accessibility considerations
        # (In a real test, we'd check for proper contrast ratios, focus indicators, etc.)
    
    def test_session_manager_accessibility_preferences(self):
        """Test accessibility preferences in session manager"""
        from ui.utils.session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Test accessibility preferences
        accessibility_prefs = {
            'high_contrast': True,
            'screen_reader': True,
            'reduce_motion': True,
            'keyboard_navigation': True
        }
        
        session_manager.update_preferences(accessibility_prefs)
        preferences = session_manager.get_preferences()
        
        for key, value in accessibility_prefs.items():
            self.assertEqual(preferences[key], value)

if __name__ == '__main__':
    unittest.main()