"""
Unit tests for message type registration system.
Tests message type registration, handler management, and middleware.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Import the modules to test
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from message_registry import (
    MessageTypeRegistry, MessageTypeInfo, MessagePriority, MessageCategory,
    register_message_type, register_handler, get_handlers, list_message_types,
    is_message_type_registered, get_registry
)


class TestMessageTypeRegistry(unittest.TestCase):
    """Test cases for MessageTypeRegistry class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.registry = MessageTypeRegistry()
    
    def test_initialization(self):
        """Test registry initialization with core types"""
        # Check that core types are registered
        self.assertTrue(self.registry.is_registered('tool_call'))
        self.assertTrue(self.registry.is_registered('tool_result'))
        self.assertTrue(self.registry.is_registered('ally_intent'))
        self.assertTrue(self.registry.is_registered('ally_memory'))
        self.assertTrue(self.registry.is_registered('ally_query'))
        self.assertTrue(self.registry.is_registered('ally_status'))
        self.assertTrue(self.registry.is_registered('negotiation'))
        self.assertTrue(self.registry.is_registered('query'))
    
    def test_register_new_type(self):
        """Test registering a new message type"""
        success = self.registry.register_type(
            message_type="test_message",
            category=MessageCategory.SYSTEM,
            description="Test message type",
            schema_version="1.0"
        )
        
        self.assertTrue(success)
        self.assertTrue(self.registry.is_registered('test_message'))
        
        # Check type info
        info = self.registry.get_type_info('test_message')
        self.assertIsNotNone(info)
        self.assertEqual(info.message_type, 'test_message')
        self.assertEqual(info.category, MessageCategory.SYSTEM)
        self.assertEqual(info.description, 'Test message type')
        self.assertEqual(info.schema_version, '1.0')
    
    def test_register_duplicate_type(self):
        """Test registering duplicate message type"""
        # First registration should succeed
        success1 = self.registry.register_type(
            message_type="duplicate_test",
            category=MessageCategory.SYSTEM,
            description="First registration",
            schema_version="1.0"
        )
        self.assertTrue(success1)
        
        # Second registration should fail
        success2 = self.registry.register_type(
            message_type="duplicate_test",
            category=MessageCategory.SYSTEM,
            description="Second registration",
            schema_version="1.0"
        )
        self.assertFalse(success2)
    
    def test_unregister_type(self):
        """Test unregistering a message type"""
        # Register a type first
        self.registry.register_type(
            message_type="temp_message",
            category=MessageCategory.SYSTEM,
            description="Temporary message",
            schema_version="1.0"
        )
        self.assertTrue(self.registry.is_registered('temp_message'))
        
        # Unregister it
        success = self.registry.unregister_type('temp_message')
        self.assertTrue(success)
        self.assertFalse(self.registry.is_registered('temp_message'))
        
        # Try to unregister non-existent type
        success2 = self.registry.unregister_type('non_existent')
        self.assertFalse(success2)
    
    def test_register_handler(self):
        """Test registering message handlers"""
        def test_handler(message):
            return "handled"
        
        # Register handler for existing type
        success = self.registry.register_handler('tool_call', test_handler)
        self.assertTrue(success)
        
        # Check handler is registered
        handlers = self.registry.get_handlers('tool_call')
        self.assertIn(test_handler, handlers)
        
        # Try to register handler for non-existent type
        success2 = self.registry.register_handler('non_existent', test_handler)
        self.assertFalse(success2)
    
    def test_register_invalid_handler(self):
        """Test registering invalid handler (no parameters)"""
        def invalid_handler():
            return "invalid"
        
        success = self.registry.register_handler('tool_call', invalid_handler)
        self.assertFalse(success)
    
    def test_unregister_handler(self):
        """Test unregistering message handlers"""
        def test_handler(message):
            return "handled"
        
        # Register handler first
        self.registry.register_handler('tool_call', test_handler)
        self.assertIn(test_handler, self.registry.get_handlers('tool_call'))
        
        # Unregister handler
        success = self.registry.unregister_handler('tool_call', test_handler)
        self.assertTrue(success)
        self.assertNotIn(test_handler, self.registry.get_handlers('tool_call'))
        
        # Try to unregister non-existent handler
        success2 = self.registry.unregister_handler('tool_call', test_handler)
        self.assertFalse(success2)
    
    def test_list_types(self):
        """Test listing message types"""
        # List all types
        all_types = self.registry.list_types()
        self.assertIn('tool_call', all_types)
        self.assertIn('ally_intent', all_types)
        
        # List by category
        tool_types = self.registry.list_types(category=MessageCategory.TOOL_EXECUTION)
        self.assertIn('tool_call', tool_types)
        self.assertIn('tool_result', tool_types)
        self.assertNotIn('ally_intent', tool_types)
        
        # List excluding deprecated
        non_deprecated = self.registry.list_types(include_deprecated=False)
        self.assertNotIn('query', non_deprecated)  # query is deprecated
        self.assertIn('tool_call', non_deprecated)
    
    def test_deprecated_types(self):
        """Test deprecated type handling"""
        # Check that 'query' is deprecated
        self.assertTrue(self.registry.is_deprecated('query'))
        self.assertFalse(self.registry.is_deprecated('tool_call'))
        
        # Check replacement type
        replacement = self.registry.get_replacement_type('query')
        self.assertEqual(replacement, 'ally_query')
        
        # Non-deprecated type should have no replacement
        self.assertIsNone(self.registry.get_replacement_type('tool_call'))
    
    def test_register_middleware(self):
        """Test registering middleware"""
        def test_middleware(message, next_func):
            return next_func(message)
        
        success = self.registry.register_middleware(test_middleware)
        self.assertTrue(success)
        
        middleware_list = self.registry.get_middleware()
        self.assertIn(test_middleware, middleware_list)
    
    def test_register_invalid_middleware(self):
        """Test registering invalid middleware (insufficient parameters)"""
        def invalid_middleware(message):
            return message
        
        success = self.registry.register_middleware(invalid_middleware)
        self.assertFalse(success)
    
    def test_validate_message_type(self):
        """Test message type validation"""
        # Valid message with registered type
        valid_message = {"type": "tool_call", "data": "test"}
        is_valid, error = self.registry.validate_message_type(valid_message)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Message with unknown type
        unknown_message = {"type": "unknown_type", "data": "test"}
        is_valid, error = self.registry.validate_message_type(unknown_message)
        self.assertFalse(is_valid)
        self.assertIn("Unknown message type", error)
        
        # Message missing type field
        no_type_message = {"data": "test"}
        is_valid, error = self.registry.validate_message_type(no_type_message)
        self.assertFalse(is_valid)
        self.assertIn("missing 'type' field", error)
        
        # Message with deprecated type (should be valid but log warning)
        deprecated_message = {"type": "query", "data": "test"}
        with patch('message_registry.logger') as mock_logger:
            is_valid, error = self.registry.validate_message_type(deprecated_message)
            self.assertTrue(is_valid)
            self.assertIsNone(error)
            mock_logger.warning.assert_called_once()
    
    def test_get_statistics(self):
        """Test getting registry statistics"""
        stats = self.registry.get_statistics()
        
        self.assertIn('total_types', stats)
        self.assertIn('total_handlers', stats)
        self.assertIn('middleware_count', stats)
        self.assertIn('by_category', stats)
        self.assertIn('deprecated_count', stats)
        
        # Check that we have the expected core types
        self.assertGreaterEqual(stats['total_types'], 8)  # At least 8 core types
        
        # Check category breakdown
        self.assertIn('tool_execution', stats['by_category'])
        self.assertIn('cognitive', stats['by_category'])
        self.assertIn('legacy', stats['by_category'])
        
        # Check deprecated count
        self.assertGreaterEqual(stats['deprecated_count'], 1)  # At least 'query' is deprecated


class TestMessageTypeInfo(unittest.TestCase):
    """Test cases for MessageTypeInfo dataclass"""
    
    def test_create_message_type_info(self):
        """Test creating MessageTypeInfo instance"""
        info = MessageTypeInfo(
            message_type="test_type",
            category=MessageCategory.SYSTEM,
            description="Test type",
            schema_version="1.0",
            priority=MessagePriority.HIGH,
            requires_response=True,
            timeout_seconds=30.0
        )
        
        self.assertEqual(info.message_type, "test_type")
        self.assertEqual(info.category, MessageCategory.SYSTEM)
        self.assertEqual(info.description, "Test type")
        self.assertEqual(info.schema_version, "1.0")
        self.assertEqual(info.priority, MessagePriority.HIGH)
        self.assertTrue(info.requires_response)
        self.assertEqual(info.timeout_seconds, 30.0)
        self.assertFalse(info.deprecated)
        self.assertIsNone(info.replacement_type)


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions"""
    
    def test_register_message_type_function(self):
        """Test global register_message_type function"""
        success = register_message_type(
            message_type="global_test_type",
            category=MessageCategory.SYSTEM,
            description="Global test type",
            schema_version="1.0"
        )
        
        self.assertTrue(success)
        self.assertTrue(is_message_type_registered('global_test_type'))
    
    def test_register_handler_function(self):
        """Test global register_handler function"""
        def test_handler(message):
            return "handled"
        
        success = register_handler('tool_call', test_handler)
        self.assertTrue(success)
        
        handlers = get_handlers('tool_call')
        self.assertIn(test_handler, handlers)
    
    def test_list_message_types_function(self):
        """Test global list_message_types function"""
        types = list_message_types()
        self.assertIn('tool_call', types)
        self.assertIn('ally_intent', types)
        
        # Test with category filter
        tool_types = list_message_types(category=MessageCategory.TOOL_EXECUTION)
        self.assertIn('tool_call', tool_types)
        self.assertNotIn('ally_intent', tool_types)
    
    def test_is_message_type_registered_function(self):
        """Test global is_message_type_registered function"""
        self.assertTrue(is_message_type_registered('tool_call'))
        self.assertFalse(is_message_type_registered('non_existent_type'))
    
    def test_get_registry_function(self):
        """Test global get_registry function"""
        registry = get_registry()
        self.assertIsInstance(registry, MessageTypeRegistry)
        self.assertTrue(registry.is_registered('tool_call'))


class TestEnums(unittest.TestCase):
    """Test cases for enum classes"""
    
    def test_message_priority_enum(self):
        """Test MessagePriority enum"""
        self.assertEqual(MessagePriority.LOW.value, "low")
        self.assertEqual(MessagePriority.NORMAL.value, "normal")
        self.assertEqual(MessagePriority.HIGH.value, "high")
        self.assertEqual(MessagePriority.CRITICAL.value, "critical")
    
    def test_message_category_enum(self):
        """Test MessageCategory enum"""
        self.assertEqual(MessageCategory.TOOL_EXECUTION.value, "tool_execution")
        self.assertEqual(MessageCategory.COGNITIVE.value, "cognitive")
        self.assertEqual(MessageCategory.SYSTEM.value, "system")
        self.assertEqual(MessageCategory.LEGACY.value, "legacy")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestMessageTypeRegistry))
    suite.addTest(unittest.makeSuite(TestMessageTypeInfo))
    suite.addTest(unittest.makeSuite(TestConvenienceFunctions))
    suite.addTest(unittest.makeSuite(TestEnums))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)