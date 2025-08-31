"""
Tool execution message handlers for Comms v3.0 infrastructure.
Handles tool_call and tool_result messages in the Stream Handler and HyperThreader.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
import uuid
import time

from message_validation import MessageValidator, MessageBuilder, deserialize_message, serialize_message
from message_registry import get_registry, MessageCategory

logger = logging.getLogger(__name__)


@dataclass
class ToolExecutionContext:
    """Context for tracking tool execution"""
    execution_id: str
    tool_name: str
    source: str
    start_time: float
    parameters: Dict[str, Any]
    status: str = "pending"
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[float] = None
    correlation_id: Optional[str] = None
    workflow_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    callbacks: List[Callable] = field(default_factory=list)


class ToolExecutionManager:
    """Manages tool execution contexts and routing"""
    
    def __init__(self):
        """Initialize the tool execution manager"""
        self.active_executions: Dict[str, ToolExecutionContext] = {}
        self.message_validator = MessageValidator()
        self.message_builder = MessageBuilder()
        self.registry = get_registry()
        self.tool_executors: Dict[str, Callable] = {}
        self.execution_timeout = 300.0  # Default 5 minutes
        self.cleanup_interval = 60.0  # Cleanup every minute
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the execution manager"""
        logger.info("Starting Tool Execution Manager")
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_executions())
    
    async def stop(self):
        """Stop the execution manager"""
        logger.info("Stopping Tool Execution Manager")
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all active executions
        for execution_id in list(self.active_executions.keys()):
            await self.cancel_execution(execution_id, "Manager shutdown")
    
    def register_tool_executor(self, tool_name: str, executor: Callable):
        """
        Register a tool executor function
        
        Args:
            tool_name: Name of the tool
            executor: Async function that executes the tool
        """
        self.tool_executors[tool_name] = executor
        logger.info(f"Registered tool executor: {tool_name}")
    
    def unregister_tool_executor(self, tool_name: str):
        """
        Unregister a tool executor
        
        Args:
            tool_name: Name of the tool to unregister
        """
        if tool_name in self.tool_executors:
            del self.tool_executors[tool_name]
            logger.info(f"Unregistered tool executor: {tool_name}")
    
    async def handle_tool_call(self, message: Dict[str, Any], ws_publish_callback: Callable = None) -> bool:
        """
        Handle incoming tool_call message
        
        Args:
            message: tool_call message dictionary
            ws_publish_callback: Callback to publish messages via WebSocket
            
        Returns:
            True if handling was successful
        """
        try:
            # Validate message
            self.message_validator.validate_message(message)
            
            execution_id = message["execution_id"]
            tool_name = message["tool_name"]
            source = message["source"]
            parameters = message["parameters"]
            
            # Check if execution already exists
            if execution_id in self.active_executions:
                logger.warning(f"Execution {execution_id} already exists")
                await self._send_error_result(
                    execution_id, tool_name, "DUPLICATE_EXECUTION",
                    "Execution ID already exists", ws_publish_callback
                )
                return False
            
            # Check if tool executor is available
            if tool_name not in self.tool_executors:
                logger.error(f"No executor registered for tool: {tool_name}")
                await self._send_error_result(
                    execution_id, tool_name, "TOOL_NOT_FOUND",
                    f"No executor registered for tool: {tool_name}", ws_publish_callback
                )
                return False
            
            # Create execution context
            context = ToolExecutionContext(
                execution_id=execution_id,
                tool_name=tool_name,
                source=source,
                start_time=time.time(),
                parameters=parameters,
                timeout_seconds=message.get("context", {}).get("timeout", self.execution_timeout),
                correlation_id=message.get("correlation_id"),
                workflow_id=message.get("workflow_id"),
                max_retries=message.get("context", {}).get("retry_count", 3)
            )
            
            self.active_executions[execution_id] = context
            
            # Start tool execution
            asyncio.create_task(self._execute_tool(context, ws_publish_callback))
            
            logger.info(f"Started tool execution: {execution_id} ({tool_name})")
            return True
            
        except Exception as e:
            logger.error(f"Error handling tool_call: {e}")
            if "execution_id" in message and "tool_name" in message:
                await self._send_error_result(
                    message["execution_id"], message["tool_name"],
                    "HANDLER_ERROR", str(e), ws_publish_callback
                )
            return False
    
    async def handle_tool_result(self, message: Dict[str, Any]) -> bool:
        """
        Handle incoming tool_result message
        
        Args:
            message: tool_result message dictionary
            
        Returns:
            True if handling was successful
        """
        try:
            # Validate message
            self.message_validator.validate_message(message)
            
            execution_id = message["execution_id"]
            
            # Find execution context
            context = self.active_executions.get(execution_id)
            if not context:
                logger.warning(f"Received result for unknown execution: {execution_id}")
                return False
            
            # Update context with result
            context.status = message["status"]
            if "result" in message:
                context.result = message["result"]
            if "error" in message:
                context.error = message["error"]
            
            # Execute callbacks
            for callback in context.callbacks:
                try:
                    await callback(context, message)
                except Exception as e:
                    logger.error(f"Error in result callback: {e}")
            
            # Clean up completed execution
            if context.status in ["success", "error", "cancelled", "timeout"]:
                del self.active_executions[execution_id]
                logger.info(f"Completed tool execution: {execution_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling tool_result: {e}")
            return False
    
    async def cancel_execution(self, execution_id: str, reason: str = "Cancelled") -> bool:
        """
        Cancel a tool execution
        
        Args:
            execution_id: Execution ID to cancel
            reason: Cancellation reason
            
        Returns:
            True if cancellation was successful
        """
        context = self.active_executions.get(execution_id)
        if not context:
            return False
        
        context.status = "cancelled"
        context.error = {"code": "CANCELLED", "message": reason}
        
        # Send cancellation result
        result_message = self.message_builder.create_tool_result(
            execution_id=execution_id,
            tool_name=context.tool_name,
            status="cancelled",
            error=context.error,
            execution_info={
                "start_time": datetime.fromtimestamp(context.start_time).isoformat() + "Z",
                "end_time": datetime.utcnow().isoformat() + "Z",
                "duration_ms": (time.time() - context.start_time) * 1000
            }
        )
        
        # Execute callbacks
        for callback in context.callbacks:
            try:
                await callback(context, result_message)
            except Exception as e:
                logger.error(f"Error in cancellation callback: {e}")
        
        del self.active_executions[execution_id]
        logger.info(f"Cancelled tool execution: {execution_id}")
        return True
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a tool execution
        
        Args:
            execution_id: Execution ID to query
            
        Returns:
            Execution status dictionary or None if not found
        """
        context = self.active_executions.get(execution_id)
        if not context:
            return None
        
        return {
            "execution_id": context.execution_id,
            "tool_name": context.tool_name,
            "source": context.source,
            "status": context.status,
            "start_time": datetime.fromtimestamp(context.start_time).isoformat() + "Z",
            "duration_ms": (time.time() - context.start_time) * 1000,
            "retry_count": context.retry_count,
            "correlation_id": context.correlation_id,
            "workflow_id": context.workflow_id
        }
    
    def list_active_executions(self) -> List[Dict[str, Any]]:
        """
        List all active tool executions
        
        Returns:
            List of execution status dictionaries
        """
        return [
            self.get_execution_status(execution_id)
            for execution_id in self.active_executions.keys()
        ]
    
    async def _execute_tool(self, context: ToolExecutionContext, ws_publish_callback: Callable = None):
        """
        Execute a tool with the given context
        
        Args:
            context: Tool execution context
            ws_publish_callback: Callback to publish results
        """
        executor = self.tool_executors[context.tool_name]
        
        try:
            # Set up timeout
            timeout = context.timeout_seconds or self.execution_timeout
            
            # Execute tool with timeout
            result = await asyncio.wait_for(
                executor(context.parameters),
                timeout=timeout
            )
            
            # Create success result
            execution_info = {
                "start_time": datetime.fromtimestamp(context.start_time).isoformat() + "Z",
                "end_time": datetime.utcnow().isoformat() + "Z",
                "duration_ms": (time.time() - context.start_time) * 1000,
                "retry_count": context.retry_count
            }
            
            result_message = self.message_builder.create_tool_result(
                execution_id=context.execution_id,
                tool_name=context.tool_name,
                status="success",
                result=result,
                execution_info=execution_info,
                correlation_id=context.correlation_id,
                workflow_id=context.workflow_id
            )
            
            # Update context
            context.status = "success"
            context.result = result
            
            # Send result
            if ws_publish_callback:
                await ws_publish_callback(serialize_message(result_message))
            
            # Execute callbacks
            for callback in context.callbacks:
                try:
                    await callback(context, result_message)
                except Exception as e:
                    logger.error(f"Error in success callback: {e}")
            
            # Clean up
            if context.execution_id in self.active_executions:
                del self.active_executions[context.execution_id]
            
            logger.info(f"Tool execution completed successfully: {context.execution_id}")
            
        except asyncio.TimeoutError:
            await self._handle_execution_error(
                context, "TIMEOUT", "Tool execution timed out", ws_publish_callback
            )
        except Exception as e:
            await self._handle_execution_error(
                context, "EXECUTION_FAILED", str(e), ws_publish_callback
            )
    
    async def _handle_execution_error(
        self, 
        context: ToolExecutionContext, 
        error_code: str, 
        error_message: str,
        ws_publish_callback: Callable = None
    ):
        """
        Handle tool execution error with retry logic
        
        Args:
            context: Tool execution context
            error_code: Error code
            error_message: Error message
            ws_publish_callback: Callback to publish results
        """
        context.retry_count += 1
        
        # Check if we should retry
        if context.retry_count <= context.max_retries and error_code != "TIMEOUT":
            logger.warning(f"Tool execution failed, retrying ({context.retry_count}/{context.max_retries}): {context.execution_id}")
            
            # Wait before retry (exponential backoff)
            await asyncio.sleep(min(2 ** context.retry_count, 30))
            
            # Retry execution
            await self._execute_tool(context, ws_publish_callback)
            return
        
        # Max retries reached or non-retryable error
        error_info = {
            "code": error_code,
            "message": error_message
        }
        
        execution_info = {
            "start_time": datetime.fromtimestamp(context.start_time).isoformat() + "Z",
            "end_time": datetime.utcnow().isoformat() + "Z",
            "duration_ms": (time.time() - context.start_time) * 1000,
            "retry_count": context.retry_count
        }
        
        result_message = self.message_builder.create_tool_result(
            execution_id=context.execution_id,
            tool_name=context.tool_name,
            status="error",
            error=error_info,
            execution_info=execution_info,
            correlation_id=context.correlation_id,
            workflow_id=context.workflow_id
        )
        
        # Update context
        context.status = "error"
        context.error = error_info
        
        # Send error result
        if ws_publish_callback:
            await ws_publish_callback(serialize_message(result_message))
        
        # Execute callbacks
        for callback in context.callbacks:
            try:
                await callback(context, result_message)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
        
        # Clean up
        if context.execution_id in self.active_executions:
            del self.active_executions[context.execution_id]
        
        logger.error(f"Tool execution failed: {context.execution_id} - {error_message}")
    
    async def _send_error_result(
        self,
        execution_id: str,
        tool_name: str,
        error_code: str,
        error_message: str,
        ws_publish_callback: Callable = None
    ):
        """
        Send an error result message
        
        Args:
            execution_id: Execution ID
            tool_name: Tool name
            error_code: Error code
            error_message: Error message
            ws_publish_callback: Callback to publish the message
        """
        result_message = self.message_builder.create_tool_result(
            execution_id=execution_id,
            tool_name=tool_name,
            status="error",
            error={"code": error_code, "message": error_message}
        )
        
        if ws_publish_callback:
            await ws_publish_callback(serialize_message(result_message))
    
    async def _cleanup_expired_executions(self):
        """
        Periodically clean up expired executions
        """
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = time.time()
                expired_executions = []
                
                for execution_id, context in self.active_executions.items():
                    timeout = context.timeout_seconds or self.execution_timeout
                    if current_time - context.start_time > timeout:
                        expired_executions.append(execution_id)
                
                for execution_id in expired_executions:
                    await self.cancel_execution(execution_id, "Execution timeout")
                
                if expired_executions:
                    logger.info(f"Cleaned up {len(expired_executions)} expired executions")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")


class ToolMessageRouter:
    """Routes tool messages to appropriate handlers"""
    
    def __init__(self, execution_manager: ToolExecutionManager):
        """Initialize the message router"""
        self.execution_manager = execution_manager
        self.message_validator = MessageValidator()
        self.registry = get_registry()
    
    async def route_message(self, message: Dict[str, Any], ws_publish_callback: Callable = None) -> bool:
        """
        Route a message to the appropriate handler
        
        Args:
            message: Message dictionary
            ws_publish_callback: Callback to publish response messages
            
        Returns:
            True if routing was successful
        """
        try:
            message_type = message.get("type")
            if not message_type:
                logger.error("Message missing type field")
                return False
            
            # Validate message type is registered
            is_valid, error = self.registry.validate_message_type(message)
            if not is_valid:
                logger.error(f"Message validation failed: {error}")
                return False
            
            # Route based on message type
            if message_type == "tool_call":
                return await self.execution_manager.handle_tool_call(message, ws_publish_callback)
            elif message_type == "tool_result":
                return await self.execution_manager.handle_tool_result(message)
            else:
                # Not a tool message, let other handlers process it
                logger.debug(f"Message type {message_type} not handled by tool router")
                return True
                
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            return False
    
    def supports_message_type(self, message_type: str) -> bool:
        """
        Check if this router supports a message type
        
        Args:
            message_type: Message type to check
            
        Returns:
            True if supported
        """
        return message_type in ["tool_call", "tool_result"]


# Global instances for integration with existing Comms infrastructure
_execution_manager = ToolExecutionManager()
_message_router = ToolMessageRouter(_execution_manager)

# Convenience functions for integration
async def start_tool_handlers():
    """Start the tool message handlers"""
    await _execution_manager.start()

async def stop_tool_handlers():
    """Stop the tool message handlers"""
    await _execution_manager.stop()

def register_tool_executor(tool_name: str, executor: Callable):
    """Register a tool executor"""
    _execution_manager.register_tool_executor(tool_name, executor)

async def route_tool_message(message: Dict[str, Any], ws_publish_callback: Callable = None) -> bool:
    """Route a tool message"""
    return await _message_router.route_message(message, ws_publish_callback)

def get_execution_manager() -> ToolExecutionManager:
    """Get the global execution manager"""
    return _execution_manager

def get_message_router() -> ToolMessageRouter:
    """Get the global message router"""
    return _message_router