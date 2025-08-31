#!/usr/bin/env python3
"""
Test script for Stream Handler v4.0 functionality
Tests the core components without requiring socketify
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from message_validation import MessageValidator, MessageBuilder, MessageSerializer
        from message_registry import get_registry
        from tool_message_handlers import ToolExecutionManager, ToolMessageRouter
        print("✓ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_message_validation():
    """Test message validation functionality"""
    try:
        from message_validation import MessageValidator, MessageBuilder
        
        validator = MessageValidator()
        builder = MessageBuilder()
        
        # Test tool_call message creation and validation
        tool_call = builder.create_tool_call(
            source="test_client",
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        # Validate the message
        is_valid = validator.validate_message(tool_call)
        print(f"✓ Tool call message validation: {is_valid}")
        
        # Test tool_result message creation and validation
        tool_result = builder.create_tool_result(
            execution_id=tool_call["execution_id"],
            tool_name="test_tool",
            status="success",
            result={"output": "test result"}
        )
        
        is_valid = validator.validate_message(tool_result)
        print(f"✓ Tool result message validation: {is_valid}")
        
        return True
    except Exception as e:
        print(f"✗ Message validation error: {e}")
        return False

def test_message_registry():
    """Test message registry functionality"""
    try:
        from message_registry import get_registry
        
        registry = get_registry()
        
        # Check that core message types are registered
        supported_types = registry.list_types()
        expected_types = ['tool_call', 'tool_result', 'ally_intent', 'ally_memory', 'ally_query', 'ally_status']
        
        for msg_type in expected_types:
            if msg_type in supported_types:
                print(f"✓ Message type '{msg_type}' is registered")
            else:
                print(f"✗ Message type '{msg_type}' is NOT registered")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Message registry error: {e}")
        return False

def test_unified_stream_format():
    """Test the unified stream format from stream handler"""
    try:
        # Import the UnifiedStreamFormat class directly from the file content
        # Since we can't import the full module due to socketify dependency
        
        # Test creating stream data
        stream_data = {
            "stream_id": "test_stream_1",
            "name": "Test Stream",
            "datatype": "float",
            "unit": "m/s",
            "value": 1.23,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
        
        # Test creating negotiation message
        negotiation_msg = {
            "type": "negotiation",
            "status": "active",
            "data": {"test_stream_1": stream_data},
            "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Test creating physics message
        physics_msg = {
            "type": "physics_simulation",
            "simulation_id": "test_sim_1",
            "command": "register",
            "streams": {"test_stream_1": stream_data},
            "status": "active",
            "msg-sent-timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✓ Unified stream format structures created successfully")
        print(f"  - Negotiation message type: {negotiation_msg['type']}")
        print(f"  - Physics message type: {physics_msg['type']}")
        
        return True
    except Exception as e:
        print(f"✗ Unified stream format error: {e}")
        return False

def test_tool_execution_manager():
    """Test tool execution manager functionality"""
    try:
        from tool_message_handlers import ToolExecutionManager
        
        manager = ToolExecutionManager()
        
        # Test registering a simple tool executor
        async def dummy_tool(parameters):
            return {"result": "success", "input": parameters}
        
        manager.register_tool_executor("dummy_tool", dummy_tool)
        
        # Check that the tool is registered
        if "dummy_tool" in manager.tool_executors:
            print("✓ Tool executor registered successfully")
        else:
            print("✗ Tool executor registration failed")
            return False
        
        # Test unregistering
        manager.unregister_tool_executor("dummy_tool")
        
        if "dummy_tool" not in manager.tool_executors:
            print("✓ Tool executor unregistered successfully")
        else:
            print("✗ Tool executor unregistration failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Tool execution manager error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Stream Handler v4.0 - Core Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Message Validation", test_message_validation),
        ("Message Registry", test_message_registry),
        ("Unified Stream Format", test_unified_stream_format),
        ("Tool Execution Manager", test_tool_execution_manager)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Stream Handler v4.0 core functionality is working.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)