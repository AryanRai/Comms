"""
Message type registration system for Chyappy v3.0 protocol extensions.
Manages registration and discovery of message types and their handlers.
"""

from typing import Dict, Any, Callable, Optional, List, Set
from dataclasses import dataclass
from enum import Enum
import inspect
import logging

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageCategory(Enum):
    """Message categories for organization"""
    TOOL_EXECUTION = "tool_execution"
    COGNITIVE = "cognitive"
    SYSTEM = "system"
    LEGACY = "legacy"


@dataclass
class MessageTypeInfo:
    """Information about a registered message type"""
    message_type: str
    category: MessageCategory
    description: str
    schema_version: str
    handler_function: Optional[Callable] = None
    priority: MessagePriority = MessagePriority.NORMAL
    requires_response: bool = False
    timeout_seconds: Optional[float] = None
    deprecated: bool = False
    replacement_type: Optional[str] = None


class MessageTypeRegistry:
    """Registry for managing message types and their handlers"""
    
    def __init__(self):
        """Initialize the message type registry"""
        self._types: Dict[str, MessageTypeInfo] = {}
        self._handlers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
        self._initialize_core_types()
    
    def _initialize_core_types(self):
        """Initialize core Chyappy v3.0 message types"""
        
        # Tool execution message types
        self.register_type(
            message_type="tool_call",
            category=MessageCategory.TOOL_EXECUTION,
            description="Request to execute a tool with specified parameters",
            schema_version="1.0",
            requires_response=True,
            timeout_seconds=300.0
        )
        
        self.register_type(
            message_type="tool_result",
            category=MessageCategory.TOOL_EXECUTION,
            description="Result of tool execution with status and output",
            schema_version="1.0",
            requires_response=False
        )
        
        # Cognitive message types
        self.register_type(
            message_type="ally_intent",
            category=MessageCategory.COGNITIVE,
            description="Cognitive intent extracted from user input",
            schema_version="1.0",
            requires_response=True,
            timeout_seconds=30.0
        )
        
        self.register_type(
            message_type="ally_memory",
            category=MessageCategory.COGNITIVE,
            description="Memory storage and retrieval operations",
            schema_version="1.0",
            requires_response=True,
            timeout_seconds=10.0
        )
        
        self.register_type(
            message_type="ally_query",
            category=MessageCategory.COGNITIVE,
            description="System queries for status and information",
            schema_version="1.0",
            requires_response=True,
            timeout_seconds=5.0
        )
        
        self.register_type(
            message_type="ally_status",
            category=MessageCategory.COGNITIVE,
            description="System status and health information",
            schema_version="1.0",
            requires_response=False
        )
        
        # Legacy system message types
        self.register_type(
            message_type="negotiation",
            category=MessageCategory.LEGACY,
            description="Legacy stream negotiation message",
            schema_version="legacy",
            requires_response=False
        )
        
        self.register_type(
            message_type="query",
            category=MessageCategory.LEGACY,
            description="Legacy query message",
            schema_version="legacy",
            requires_response=True,
            deprecated=True,
            replacement_type="ally_query"
        )
    
    def register_type(
        self,
        message_type: str,
        category: MessageCategory,
        description: str,
        schema_version: str,
        handler_function: Optional[Callable] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_response: bool = False,
        timeout_seconds: Optional[float] = None,
        deprecated: bool = False,
        replacement_type: Optional[str] = None
    ) -> bool:
        """
        Register a new message type
        
        Args:
            message_type: Unique message type identifier
            category: Message category
            description: Human-readable description
            schema_version: Schema version
            handler_function: Optional default handler
            priority: Message priority level
            requires_response: Whether message requires a response
            timeout_seconds: Response timeout
            deprecated: Whether type is deprecated
            replacement_type: Replacement type if deprecated
            
        Returns:
            True if registration successful, False if type already exists
        """
        if message_type in self._types:
            logger.warning(f"Message type '{message_type}' already registered")
            return False
        
        type_info = MessageTypeInfo(
            message_type=message_type,
            category=category,
            description=description,
            schema_version=schema_version,
            handler_function=handler_function,
            priority=priority,
            requires_response=requires_response,
            timeout_seconds=timeout_seconds,
            deprecated=deprecated,
            replacement_type=replacement_type
        )
        
        self._types[message_type] = type_info
        self._handlers[message_type] = []
        
        if handler_function:
            self.register_handler(message_type, handler_function)
        
        logger.info(f"Registered message type: {message_type}")
        return True
    
    def unregister_type(self, message_type: str) -> bool:
        """
        Unregister a message type
        
        Args:
            message_type: Message type to unregister
            
        Returns:
            True if unregistration successful
        """
        if message_type not in self._types:
            logger.warning(f"Message type '{message_type}' not found")
            return False
        
        del self._types[message_type]
        del self._handlers[message_type]
        
        logger.info(f"Unregistered message type: {message_type}")
        return True
    
    def register_handler(self, message_type: str, handler: Callable) -> bool:
        """
        Register a handler for a message type
        
        Args:
            message_type: Message type to handle
            handler: Handler function
            
        Returns:
            True if registration successful
        """
        if message_type not in self._types:
            logger.error(f"Cannot register handler for unknown message type: {message_type}")
            return False
        
        # Validate handler signature
        sig = inspect.signature(handler)
        if len(sig.parameters) < 1:
            logger.error(f"Handler for {message_type} must accept at least one parameter (message)")
            return False
        
        self._handlers[message_type].append(handler)
        logger.info(f"Registered handler for message type: {message_type}")
        return True
    
    def unregister_handler(self, message_type: str, handler: Callable) -> bool:
        """
        Unregister a specific handler
        
        Args:
            message_type: Message type
            handler: Handler function to remove
            
        Returns:
            True if unregistration successful
        """
        if message_type not in self._handlers:
            return False
        
        try:
            self._handlers[message_type].remove(handler)
            logger.info(f"Unregistered handler for message type: {message_type}")
            return True
        except ValueError:
            logger.warning(f"Handler not found for message type: {message_type}")
            return False
    
    def get_handlers(self, message_type: str) -> List[Callable]:
        """
        Get all handlers for a message type
        
        Args:
            message_type: Message type
            
        Returns:
            List of handler functions
        """
        return self._handlers.get(message_type, [])
    
    def get_type_info(self, message_type: str) -> Optional[MessageTypeInfo]:
        """
        Get information about a message type
        
        Args:
            message_type: Message type
            
        Returns:
            MessageTypeInfo or None if not found
        """
        return self._types.get(message_type)
    
    def list_types(self, category: Optional[MessageCategory] = None, include_deprecated: bool = True) -> List[str]:
        """
        List registered message types
        
        Args:
            category: Optional category filter
            include_deprecated: Whether to include deprecated types
            
        Returns:
            List of message type names
        """
        types = []
        for msg_type, info in self._types.items():
            if category and info.category != category:
                continue
            if not include_deprecated and info.deprecated:
                continue
            types.append(msg_type)
        
        return sorted(types)
    
    def is_registered(self, message_type: str) -> bool:
        """
        Check if a message type is registered
        
        Args:
            message_type: Message type to check
            
        Returns:
            True if registered
        """
        return message_type in self._types
    
    def is_deprecated(self, message_type: str) -> bool:
        """
        Check if a message type is deprecated
        
        Args:
            message_type: Message type to check
            
        Returns:
            True if deprecated
        """
        info = self._types.get(message_type)
        return info.deprecated if info else False
    
    def get_replacement_type(self, message_type: str) -> Optional[str]:
        """
        Get replacement type for deprecated message type
        
        Args:
            message_type: Deprecated message type
            
        Returns:
            Replacement type name or None
        """
        info = self._types.get(message_type)
        return info.replacement_type if info and info.deprecated else None
    
    def register_middleware(self, middleware: Callable) -> bool:
        """
        Register middleware for message processing
        
        Args:
            middleware: Middleware function that takes (message, next) parameters
            
        Returns:
            True if registration successful
        """
        sig = inspect.signature(middleware)
        if len(sig.parameters) < 2:
            logger.error("Middleware must accept at least two parameters (message, next)")
            return False
        
        self._middleware.append(middleware)
        logger.info("Registered message middleware")
        return True
    
    def get_middleware(self) -> List[Callable]:
        """
        Get all registered middleware
        
        Returns:
            List of middleware functions
        """
        return self._middleware.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics
        
        Returns:
            Dictionary with registry statistics
        """
        stats = {
            "total_types": len(self._types),
            "total_handlers": sum(len(handlers) for handlers in self._handlers.values()),
            "middleware_count": len(self._middleware),
            "by_category": {},
            "deprecated_count": 0
        }
        
        for info in self._types.values():
            category = info.category.value
            if category not in stats["by_category"]:
                stats["by_category"][category] = 0
            stats["by_category"][category] += 1
            
            if info.deprecated:
                stats["deprecated_count"] += 1
        
        return stats
    
    def validate_message_type(self, message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that a message has a registered type
        
        Args:
            message: Message dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        message_type = message.get('type')
        if not message_type:
            return False, "Message missing 'type' field"
        
        if not self.is_registered(message_type):
            return False, f"Unknown message type: {message_type}"
        
        if self.is_deprecated(message_type):
            replacement = self.get_replacement_type(message_type)
            warning = f"Message type '{message_type}' is deprecated"
            if replacement:
                warning += f", use '{replacement}' instead"
            logger.warning(warning)
        
        return True, None


# Global registry instance
_registry = MessageTypeRegistry()

# Convenience functions
def register_message_type(**kwargs) -> bool:
    """Register a message type using the global registry"""
    return _registry.register_type(**kwargs)

def register_handler(message_type: str, handler: Callable) -> bool:
    """Register a handler using the global registry"""
    return _registry.register_handler(message_type, handler)

def get_handlers(message_type: str) -> List[Callable]:
    """Get handlers using the global registry"""
    return _registry.get_handlers(message_type)

def list_message_types(**kwargs) -> List[str]:
    """List message types using the global registry"""
    return _registry.list_types(**kwargs)

def is_message_type_registered(message_type: str) -> bool:
    """Check if message type is registered using the global registry"""
    return _registry.is_registered(message_type)

def get_registry() -> MessageTypeRegistry:
    """Get the global message type registry"""
    return _registry