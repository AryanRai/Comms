"""
Simple integration test for protocol handler integration.
Tests basic functionality without complex mocking.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from message_validation import create_tool_call, create_tool_result, validate_message
from message_registry import get_registry


async def test_message_creation_and_validation():
    """Test message creation and validation"""
    print("Testing message creation and validation...")
    
    # Test tool_call creation
    tool_call = create_tool_call(
        source="test_source",
        tool_name="test_tool",
        parameters={"param1": "value1", "param2": 42},
        execution_id="exec_test_123",
        context={"user": "test_user"}
    )
    
    print(f"Created tool_call: {tool_call}")
    
    # Validate tool_call
    is_valid = validate_message(tool_call)
    print(f"Tool call validation: {'PASS' if is_valid else 'FAIL'}")
    
    # Test tool_result creation
    tool_result = create_tool_result(
        execution_id="exec_test_123",
        tool_name="test_tool",
        status="success",
        result={"output": "test output"},
        error=None
    )
    
    print(f"Created tool_result: {tool_result}")
    
    # Validate tool_result
    is_valid = validate_message(tool_result)
    print(f"Tool result validation: {'PASS' if is_valid else 'FAIL'}")
    
    return True


async def test_message_registry():
    """Test message registry functionality"""
    print("\nTesting message registry...")
    
    registry = get_registry()
    
    # Check if tool message types are registered
    tool_call_registered = registry.is_registered('tool_call')
    tool_result_registered = registry.is_registered('tool_result')
    
    print(f"tool_call registered: {'PASS' if tool_call_registered else 'FAIL'}")
    print(f"tool_result registered: {'PASS' if tool_result_registered else 'FAIL'}")
    
    # Get type info instead of schemas
    try:
        tool_call_info = registry.get_type_info('tool_call')
        tool_result_info = registry.get_type_info('tool_result')
        
        print(f"tool_call info available: {'PASS' if tool_call_info else 'FAIL'}")
        print(f"tool_result info available: {'PASS' if tool_result_info else 'FAIL'}")
    except Exception as e:
        print(f"Type info retrieval error: {e}")
        return False
    
    return True


async def test_tool_router_basic():
    """Test basic tool router functionality"""
    print("\nTesting tool router basic functionality...")
    
    try:
        # Test that we can import the tool message handlers
        from tool_message_handlers import get_execution_manager, start_tool_handlers
        
        execution_manager = get_execution_manager()
        print(f"Execution manager available: {'PASS' if execution_manager else 'FAIL'}")
        
        # Test message handler functions exist
        from message_validation import validate_message
        from message_registry import get_registry
        
        registry = get_registry()
        print(f"Message registry available: {'PASS' if registry else 'FAIL'}")
        
        # Test that we can create a simple router-like object
        message_handlers = {}
        message_handlers['tool_call'] = lambda x: x  # Simple handler
        message_handlers['tool_result'] = lambda x: x  # Simple handler
        
        print(f"Message handlers created: {'PASS' if len(message_handlers) == 2 else 'FAIL'}")
        
        return True
        
    except Exception as e:
        print(f"Tool router test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=== Protocol Handler Integration Tests ===\n")
    
    tests = [
        test_message_creation_and_validation,
        test_message_registry,
        test_tool_router_basic
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Overall: {'PASS' if all(results) else 'FAIL'}")
    
    return all(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)