"""
Integration tests for protocol handler integration with tool message routing.
Tests the complete flow from message reception to tool execution and response.
"""

import asyncio
import json
import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from HyperThreaderv2 import ToolMessageRouter, EnhancedProcessManager
from message_validation import create_tool_call, create_tool_result
from tool_message_handlers import get_execution_manager


class TestProtocolIntegration:
    """Test protocol handler integration"""
    
    @pytest.fixture
    def tool_router(self):
        """Create a tool message router for testing"""
        return ToolMessageRouter()
    
    @pytest.fixture
    def sample_tool_call(self):
        """Create a sample tool call message"""
        return create_tool_call(
            tool_name="test_tool",
            parameters={"param1": "value1", "param2": 42},
            execution_id="test_exec_123",
            context={"user": "test_user", "session": "test_session"}
        )
    
    @pytest.fixture
    def sample_tool_result(self):
        """Create a sample tool result message"""
        return create_tool_result(
            execution_id="test_exec_123",
            tool_name="test_tool",
            status="success",
            result={"output": "test output", "value": 100},
            error=None
        )
    
    @pytest.mark.asyncio
    async def test_tool_call_routing(self, tool_router, sample_tool_call):
        """Test that tool_call messages are routed correctly"""
        # Mock the execution manager
        with patch.object(tool_router.execution_manager, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                'status': 'success',
                'result': {'output': 'test result'},
                'error': None
            }
            
            # Route the message
            response = await tool_router.route_message(sample_tool_call)
            
            # Verify execution manager was called
            mock_execute.assert_called_once_with(
                tool_name="test_tool",
                parameters={"param1": "value1", "param2": 42},
                execution_id="test_exec_123",
                context={"user": "test_user", "session": "test_session"}
            )
            
            # Verify response format
            assert response is not None
            assert response['type'] == 'tool_result'
            assert response['execution_id'] == 'test_exec_123'
            assert response['tool_name'] == 'test_tool'
            assert response['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_tool_result_routing(self, tool_router, sample_tool_result):
        """Test that tool_result messages are routed correctly"""
        # Mock the execution manager
        with patch.object(tool_router.execution_manager, 'handle_tool_result', new_callable=AsyncMock) as mock_handle:
            # Route the message
            response = await tool_router.route_message(sample_tool_result)
            
            # Verify execution manager was called
            mock_handle.assert_called_once_with(sample_tool_result)
            
            # Verify no response (tool_result messages don't generate responses)
            assert response is None
    
    @pytest.mark.asyncio
    async def test_invalid_message_handling(self, tool_router):
        """Test handling of invalid messages"""
        invalid_message = {
            "type": "tool_call",
            "invalid_field": "should_not_be_here"
            # Missing required fields
        }
        
        response = await tool_router.route_message(invalid_message)
        
        # Should return error response
        assert response is not None
        assert response['type'] == 'tool_result'
        assert response['status'] == 'error'
        assert 'error' in response
    
    @pytest.mark.asyncio
    async def test_unknown_message_type(self, tool_router):
        """Test handling of unknown message types"""
        unknown_message = {
            "type": "unknown_type",
            "data": "some data"
        }
        
        response = await tool_router.route_message(unknown_message)
        
        # Should return None for unknown types
        assert response is None
    
    @pytest.mark.asyncio
    async def test_tool_execution_error_handling(self, tool_router, sample_tool_call):
        """Test error handling during tool execution"""
        # Mock the execution manager to raise an exception
        with patch.object(tool_router.execution_manager, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Tool execution failed")
            
            # Route the message
            response = await tool_router.route_message(sample_tool_call)
            
            # Verify error response
            assert response is not None
            assert response['type'] == 'tool_result'
            assert response['status'] == 'error'
            assert 'Tool execution failed' in response['error']
    
    def test_enhanced_process_manager_initialization(self):
        """Test that EnhancedProcessManager initializes correctly"""
        # Mock Tk to avoid GUI creation during tests
        with patch('HyperThreaderv2.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create manager
            manager = EnhancedProcessManager()
            
            # Verify initialization
            assert manager.tool_router is not None
            assert isinstance(manager.tool_router, ToolMessageRouter)
            assert manager.message_queue is not None
            assert manager.running is False
    
    @pytest.mark.asyncio
    async def test_message_queue_processing(self):
        """Test message queue processing"""
        # Mock Tk to avoid GUI creation during tests
        with patch('HyperThreaderv2.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create manager
            manager = EnhancedProcessManager()
            
            # Mock the tool router
            with patch.object(manager.tool_router, 'route_message', new_callable=AsyncMock) as mock_route:
                mock_route.return_value = None
                
                # Queue a test message
                test_message = {"type": "test", "data": "test_data"}
                await manager.queue_message(test_message)
                
                # Process the message
                await manager.process_message(test_message)
                
                # Verify routing was called
                mock_route.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self):
        """Test tool execution statistics tracking"""
        # Mock Tk to avoid GUI creation during tests
        with patch('HyperThreaderv2.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create manager
            manager = EnhancedProcessManager()
            
            # Mock the tool router to return success
            with patch.object(manager.tool_router, 'route_message', new_callable=AsyncMock) as mock_route:
                mock_route.return_value = create_tool_result(
                    execution_id="test_123",
                    tool_name="test_tool",
                    status="success",
                    result={"output": "success"},
                    error=None
                )
                
                # Process a tool_call message
                tool_call = create_tool_call(
                    tool_name="test_tool",
                    parameters={},
                    execution_id="test_123"
                )
                
                initial_total = manager.tool_stats['total_executions']
                initial_active = manager.tool_stats['active_executions']
                
                await manager.process_message(tool_call)
                
                # Verify statistics were updated
                assert manager.tool_stats['total_executions'] == initial_total + 1
                assert manager.tool_stats['active_executions'] == initial_active  # Should be back to original
    
    @pytest.mark.asyncio
    async def test_error_statistics_tracking(self):
        """Test error statistics tracking"""
        # Mock Tk to avoid GUI creation during tests
        with patch('HyperThreaderv2.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Create manager
            manager = EnhancedProcessManager()
            
            # Mock the tool router to return error
            with patch.object(manager.tool_router, 'route_message', new_callable=AsyncMock) as mock_route:
                mock_route.return_value = create_tool_result(
                    execution_id="test_123",
                    tool_name="test_tool",
                    status="error",
                    result=None,
                    error="Test error"
                )
                
                # Process a tool_call message
                tool_call = create_tool_call(
                    tool_name="test_tool",
                    parameters={},
                    execution_id="test_123"
                )
                
                initial_errors = manager.tool_stats['error_count']
                
                await manager.process_message(tool_call)
                
                # Verify error count was incremented
                assert manager.tool_stats['error_count'] == initial_errors + 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])