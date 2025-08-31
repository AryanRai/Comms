"""
Unit tests for message validation and serialization utilities.
Tests JSON schema validation, message building, and serialization.
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from message_validation import (
    MessageValidator, MessageBuilder, MessageSerializer,
    MessageValidationError, validate_message, create_tool_call,
    create_tool_result, serialize_message, deserialize_message
)


class TestMessageValidator(unittest.TestCase):
    """Test cases for MessageValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = MessageValidator()
    
    def test_load_schemas(self):
        """Test schema loading"""
        # Check that schemas are loaded
        self.assertIn('tool_call', self.validator.schemas)
        self.assertIn('tool_result', self.validator.schemas)
        self.assertIn('ally_intent', self.validator.schemas)
        self.assertIn('ally_memory', self.validator.schemas)
        self.assertIn('ally_query', self.validator.schemas)
        self.assertIn('ally_status', self.validator.schemas)
    
    def test_validate_valid_tool_call(self):
        """Test validation of valid tool_call message"""
        message = {
            "type": "tool_call",
            "source": "ally_overlay",
            "tool_name": "robot_navigate",
            "parameters": {"x": 5.0, "y": 3.0},
            "execution_id": "exec_12345",
            "msg-sent-timestamp": "2025-07-27T19:25:35.123Z"
        }
        
        # Should not raise exception
        self.assertTrue(self.validator.validate_message(message))
    
    def test_validate_invalid_tool_call_missing_field(self):
        """Test validation of invalid tool_call message missing required field"""
        message = {
            "type": "tool_call",
            "source": "ally_overlay",
            "tool_name": "robot_navigate",
            "parameters": {"x": 5.0, "y": 3.0},
            # Missing execution_id and msg-sent-timestamp
        }
        
        with self.assertRaises(MessageValidationError):
            self.validator.validate_message(message)
    
    def test_validate_invalid_tool_call_wrong_type(self):
        """Test validation of tool_call with wrong field type"""
        message = {
            "type": "tool_call",
            "source": "ally_overlay",
            "tool_name": "robot_navigate",
            "parameters": {"x": 5.0, "y": 3.0},
            "execution_id": 12345,  # Should be string
            "msg-sent-timestamp": "2025-07-27T19:25:35.123Z"
        }
        
        with self.assertRaises(MessageValidationError):
            self.validator.validate_message(message)
    
    def test_validate_valid_tool_result(self):
        """Test validation of valid tool_result message"""
        message = {
            "type": "tool_result",
            "execution_id": "exec_12345",
            "tool_name": "robot_navigate",
            "status": "success",
            "result": {"final_position": {"x": 5.0, "y": 3.0}},
            "msg-sent-timestamp": "2025-07-27T19:25:47.456Z"
        }
        
        self.assertTrue(self.validator.validate_message(message))
    
    def test_validate_tool_result_with_error(self):
        """Test validation of tool_result with error status"""
        message = {
            "type": "tool_result",
            "execution_id": "exec_12345",
            "tool_name": "robot_navigate",
            "status": "error",
            "error": {
                "code": "NAVIGATION_FAILED",
                "message": "Path blocked by obstacle"
            },
            "msg-sent-timestamp": "2025-07-27T19:25:47.456Z"
        }
        
        self.assertTrue(self.validator.validate_message(message))
    
    def test_validate_unknown_message_type(self):
        """Test validation of unknown message type"""
        message = {
            "type": "unknown_type",
            "data": "test"
        }
        
        with self.assertRaises(MessageValidationError) as cm:
            self.validator.validate_message(message)
        
        self.assertIn("Unknown message type", str(cm.exception))
    
    def test_validate_message_missing_type(self):
        """Test validation of message missing type field"""
        message = {
            "data": "test"
        }
        
        with self.assertRaises(MessageValidationError) as cm:
            self.validator.validate_message(message)
        
        self.assertIn("missing 'type' field", str(cm.exception))
    
    def test_get_schema(self):
        """Test getting schema for message type"""
        schema = self.validator.get_schema('tool_call')
        self.assertIsNotNone(schema)
        self.assertEqual(schema['title'], 'Tool Call Message')
        
        # Test non-existent schema
        self.assertIsNone(self.validator.get_schema('non_existent'))
    
    def test_list_supported_types(self):
        """Test listing supported message types"""
        types = self.validator.list_supported_types()
        self.assertIn('tool_call', types)
        self.assertIn('tool_result', types)
        self.assertIn('ally_intent', types)
        self.assertIn('ally_memory', types)
        self.assertIn('ally_query', types)
        self.assertIn('ally_status', types)


class TestMessageBuilder(unittest.TestCase):
    """Test cases for MessageBuilder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.builder = MessageBuilder()
    
    def test_create_tool_call_minimal(self):
        """Test creating minimal tool_call message"""
        message = self.builder.create_tool_call(
            source="test_source",
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        self.assertEqual(message["type"], "tool_call")
        self.assertEqual(message["source"], "test_source")
        self.assertEqual(message["tool_name"], "test_tool")
        self.assertEqual(message["parameters"], {"param1": "value1"})
        self.assertIn("execution_id", message)
        self.assertIn("msg-sent-timestamp", message)
    
    def test_create_tool_call_with_context(self):
        """Test creating tool_call message with context"""
        context = {"user": "test_user", "session": "sess_123"}
        message = self.builder.create_tool_call(
            source="test_source",
            tool_name="test_tool",
            parameters={"param1": "value1"},
            context=context
        )
        
        self.assertEqual(message["context"], context)
    
    def test_create_tool_result_success(self):
        """Test creating successful tool_result message"""
        message = self.builder.create_tool_result(
            execution_id="exec_12345",
            tool_name="test_tool",
            status="success",
            result={"output": "test_output"}
        )
        
        self.assertEqual(message["type"], "tool_result")
        self.assertEqual(message["execution_id"], "exec_12345")
        self.assertEqual(message["tool_name"], "test_tool")
        self.assertEqual(message["status"], "success")
        self.assertEqual(message["result"], {"output": "test_output"})
    
    def test_create_tool_result_error(self):
        """Test creating error tool_result message"""
        error = {"code": "TEST_ERROR", "message": "Test error occurred"}
        message = self.builder.create_tool_result(
            execution_id="exec_12345",
            tool_name="test_tool",
            status="error",
            error=error
        )
        
        self.assertEqual(message["status"], "error")
        self.assertEqual(message["error"], error)
        self.assertNotIn("result", message)
    
    def test_create_ally_intent(self):
        """Test creating ally_intent message"""
        message = self.builder.create_ally_intent(
            source="ally_overlay",
            intent="navigate_to_location",
            confidence=0.95,
            slots={"location": {"x": 5.0, "y": 3.0}}
        )
        
        self.assertEqual(message["type"], "ally_intent")
        self.assertEqual(message["source"], "ally_overlay")
        self.assertEqual(message["intent"], "navigate_to_location")
        self.assertEqual(message["confidence"], 0.95)
        self.assertEqual(message["slots"], {"location": {"x": 5.0, "y": 3.0}})
    
    def test_create_ally_memory_store(self):
        """Test creating ally_memory store message"""
        content = {
            "text": "User asked robot to go to kitchen",
            "metadata": {"timestamp": "2025-07-27T19:25:35.123Z"}
        }
        message = self.builder.create_ally_memory(
            source="memory_service",
            action="store",
            memory_type="episodic",
            content=content
        )
        
        self.assertEqual(message["type"], "ally_memory")
        self.assertEqual(message["action"], "store")
        self.assertEqual(message["memory_type"], "episodic")
        self.assertEqual(message["content"], content)
    
    def test_create_ally_query(self):
        """Test creating ally_query message"""
        message = self.builder.create_ally_query(
            source="ui_client",
            query_type="robot_status",
            parameters={"format": "summary"}
        )
        
        self.assertEqual(message["type"], "ally_query")
        self.assertEqual(message["source"], "ui_client")
        self.assertEqual(message["query_type"], "robot_status")
        self.assertEqual(message["parameters"], {"format": "summary"})
    
    def test_create_ally_status(self):
        """Test creating ally_status message"""
        health = {"cpu_usage": 45.2, "memory_usage": 512.0}
        message = self.builder.create_ally_status(
            source="robot_controller",
            component="navigation_system",
            status="online",
            health=health
        )
        
        self.assertEqual(message["type"], "ally_status")
        self.assertEqual(message["source"], "robot_controller")
        self.assertEqual(message["component"], "navigation_system")
        self.assertEqual(message["status"], "online")
        self.assertEqual(message["health"], health)


class TestMessageSerializer(unittest.TestCase):
    """Test cases for MessageSerializer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.serializer = MessageSerializer()
        self.builder = MessageBuilder()
    
    def test_serialize_valid_message(self):
        """Test serializing valid message"""
        message = self.builder.create_tool_call(
            source="test_source",
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        json_str = self.serializer.serialize(message)
        self.assertIsInstance(json_str, str)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        self.assertEqual(parsed["type"], "tool_call")
    
    def test_serialize_without_validation(self):
        """Test serializing without validation"""
        message = {"type": "invalid_type", "data": "test"}
        
        # Should succeed without validation
        json_str = self.serializer.serialize(message, validate=False)
        self.assertIsInstance(json_str, str)
    
    def test_serialize_with_validation_fails(self):
        """Test serializing invalid message with validation"""
        message = {"type": "invalid_type", "data": "test"}
        
        with self.assertRaises(MessageValidationError):
            self.serializer.serialize(message, validate=True)
    
    def test_deserialize_valid_json(self):
        """Test deserializing valid JSON"""
        message = self.builder.create_tool_call(
            source="test_source",
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        json_str = self.serializer.serialize(message)
        
        deserialized = self.serializer.deserialize(json_str)
        self.assertEqual(deserialized["type"], "tool_call")
        self.assertEqual(deserialized["source"], "test_source")
    
    def test_deserialize_invalid_json(self):
        """Test deserializing invalid JSON"""
        invalid_json = '{"type": "tool_call", "invalid": json}'
        
        with self.assertRaises(MessageValidationError):
            self.serializer.deserialize(invalid_json)
    
    def test_deserialize_without_validation(self):
        """Test deserializing without validation"""
        json_str = '{"type": "invalid_type", "data": "test"}'
        
        # Should succeed without validation
        message = self.serializer.deserialize(json_str, validate=False)
        self.assertEqual(message["type"], "invalid_type")
    
    def test_serialize_batch(self):
        """Test batch serialization"""
        messages = [
            self.builder.create_tool_call(
                source="test_source",
                tool_name="tool1",
                parameters={"param1": "value1"}
            ),
            self.builder.create_tool_call(
                source="test_source",
                tool_name="tool2",
                parameters={"param2": "value2"}
            )
        ]
        
        json_strings = self.serializer.serialize_batch(messages)
        self.assertEqual(len(json_strings), 2)
        
        for json_str in json_strings:
            self.assertIsInstance(json_str, str)
            parsed = json.loads(json_str)
            self.assertEqual(parsed["type"], "tool_call")
    
    def test_deserialize_batch(self):
        """Test batch deserialization"""
        messages = [
            self.builder.create_tool_call(
                source="test_source",
                tool_name="tool1",
                parameters={"param1": "value1"}
            ),
            self.builder.create_tool_call(
                source="test_source",
                tool_name="tool2",
                parameters={"param2": "value2"}
            )
        ]
        
        json_strings = self.serializer.serialize_batch(messages)
        deserialized = self.serializer.deserialize_batch(json_strings)
        
        self.assertEqual(len(deserialized), 2)
        self.assertEqual(deserialized[0]["tool_name"], "tool1")
        self.assertEqual(deserialized[1]["tool_name"], "tool2")


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions"""
    
    def test_validate_message_function(self):
        """Test global validate_message function"""
        message = {
            "type": "tool_call",
            "source": "ally_overlay",
            "tool_name": "robot_navigate",
            "parameters": {"x": 5.0, "y": 3.0},
            "execution_id": "exec_12345",
            "msg-sent-timestamp": "2025-07-27T19:25:35.123Z"
        }
        
        self.assertTrue(validate_message(message))
    
    def test_create_tool_call_function(self):
        """Test global create_tool_call function"""
        message = create_tool_call(
            source="test_source",
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        self.assertEqual(message["type"], "tool_call")
        self.assertEqual(message["source"], "test_source")
    
    def test_create_tool_result_function(self):
        """Test global create_tool_result function"""
        message = create_tool_result(
            execution_id="exec_12345",
            tool_name="test_tool",
            status="success",
            result={"output": "test_output"}
        )
        
        self.assertEqual(message["type"], "tool_result")
        self.assertEqual(message["status"], "success")
    
    def test_serialize_deserialize_functions(self):
        """Test global serialize/deserialize functions"""
        message = create_tool_call(
            source="test_source",
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        json_str = serialize_message(message)
        deserialized = deserialize_message(json_str)
        
        self.assertEqual(deserialized["type"], "tool_call")
        self.assertEqual(deserialized["source"], "test_source")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestMessageValidator))
    suite.addTest(unittest.makeSuite(TestMessageBuilder))
    suite.addTest(unittest.makeSuite(TestMessageSerializer))
    suite.addTest(unittest.makeSuite(TestConvenienceFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)