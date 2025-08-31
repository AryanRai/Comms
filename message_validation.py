"""
Message validation and serialization utilities for Chyappy v3.0 protocol extensions.
Provides validation for tool_call, tool_result, and ally_* message types.
"""

import json
import jsonschema
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import uuid


class MessageValidationError(Exception):
    """Exception raised when message validation fails"""
    pass


class MessageValidator:
    """Validates Chyappy v3.0 protocol messages against JSON schemas"""
    
    def __init__(self, schema_dir: str = None):
        """Initialize validator with schema directory"""
        if schema_dir is None:
            schema_dir = os.path.join(os.path.dirname(__file__), 'schemas')
        
        self.schema_dir = Path(schema_dir)
        self.schemas: Dict[str, Dict] = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all JSON schemas from the schema directory"""
        schema_files = {
            'tool_call': 'tool_call.schema.json',
            'tool_result': 'tool_result.schema.json',
            'ally_intent': 'ally_intent.schema.json',
            'ally_memory': 'ally_memory.schema.json',
            'ally_query': 'ally_query.schema.json',
            'ally_status': 'ally_status.schema.json'
        }
        
        for message_type, filename in schema_files.items():
            schema_path = self.schema_dir / filename
            if schema_path.exists():
                try:
                    with open(schema_path, 'r') as f:
                        self.schemas[message_type] = json.load(f)
                except Exception as e:
                    print(f"Warning: Failed to load schema {filename}: {e}")
            else:
                print(f"Warning: Schema file not found: {schema_path}")
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate a message against its schema
        
        Args:
            message: Message dictionary to validate
            
        Returns:
            True if valid
            
        Raises:
            MessageValidationError: If validation fails
        """
        message_type = message.get('type')
        if not message_type:
            raise MessageValidationError("Message missing 'type' field")
        
        if message_type not in self.schemas:
            raise MessageValidationError(f"Unknown message type: {message_type}")
        
        schema = self.schemas[message_type]
        
        try:
            jsonschema.validate(message, schema)
            return True
        except jsonschema.ValidationError as e:
            raise MessageValidationError(f"Validation failed for {message_type}: {e.message}")
        except jsonschema.SchemaError as e:
            raise MessageValidationError(f"Schema error for {message_type}: {e.message}")
    
    def get_schema(self, message_type: str) -> Optional[Dict]:
        """Get schema for a specific message type"""
        return self.schemas.get(message_type)
    
    def list_supported_types(self) -> List[str]:
        """List all supported message types"""
        return list(self.schemas.keys())


class MessageBuilder:
    """Builder class for creating valid Chyappy v3.0 protocol messages"""
    
    def __init__(self, validator: MessageValidator = None):
        """Initialize builder with optional validator"""
        self.validator = validator or MessageValidator()
    
    def create_tool_call(
        self,
        source: str,
        tool_name: str,
        parameters: Dict[str, Any],
        execution_id: str = None,
        context: Dict[str, Any] = None,
        security: Dict[str, Any] = None,
        correlation_id: str = None,
        workflow_id: str = None
    ) -> Dict[str, Any]:
        """
        Create a tool_call message
        
        Args:
            source: Source component initiating the call
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            execution_id: Unique execution ID (auto-generated if None)
            context: Execution context
            security: Security requirements
            correlation_id: Optional correlation ID
            workflow_id: Optional workflow ID
            
        Returns:
            Valid tool_call message dictionary
        """
        if execution_id is None:
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        message = {
            "type": "tool_call",
            "source": source,
            "tool_name": tool_name,
            "parameters": parameters,
            "execution_id": execution_id,
            "msg-sent-timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if context:
            message["context"] = context
        if security:
            message["security"] = security
        if correlation_id:
            message["correlation_id"] = correlation_id
        if workflow_id:
            message["workflow_id"] = workflow_id
        
        # Validate before returning
        self.validator.validate_message(message)
        return message
    
    def create_tool_result(
        self,
        execution_id: str,
        tool_name: str,
        status: str,
        result: Any = None,
        error: Dict[str, Any] = None,
        execution_info: Dict[str, Any] = None,
        source: str = "tool_executor",
        correlation_id: str = None,
        workflow_id: str = None,
        next_actions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a tool_result message
        
        Args:
            execution_id: Execution ID from the original tool_call
            tool_name: Name of the executed tool
            status: Execution status (success, error, timeout, cancelled, partial)
            result: Tool execution result (for success/partial status)
            error: Error information (for error status)
            execution_info: Execution metadata
            source: Component that executed the tool
            correlation_id: Optional correlation ID
            workflow_id: Optional workflow ID
            next_actions: Suggested follow-up actions
            
        Returns:
            Valid tool_result message dictionary
        """
        message = {
            "type": "tool_result",
            "execution_id": execution_id,
            "tool_name": tool_name,
            "status": status,
            "source": source,
            "msg-sent-timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if result is not None:
            message["result"] = result
        if error:
            message["error"] = error
        if execution_info:
            message["execution_info"] = execution_info
        if correlation_id:
            message["correlation_id"] = correlation_id
        if workflow_id:
            message["workflow_id"] = workflow_id
        if next_actions:
            message["next_actions"] = next_actions
        
        # Validate before returning
        self.validator.validate_message(message)
        return message
    
    def create_ally_intent(
        self,
        source: str,
        intent: str,
        confidence: float,
        slots: Dict[str, Any] = None,
        context: Dict[str, Any] = None,
        alternatives: List[Dict[str, Any]] = None,
        priority: str = "normal",
        requires_confirmation: bool = False,
        safety_classification: str = "safe",
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Create an ally_intent message
        
        Args:
            source: Source component generating the intent
            intent: The identified intent
            confidence: Confidence score (0.0-1.0)
            slots: Extracted parameters
            context: Contextual information
            alternatives: Alternative interpretations
            priority: Priority level
            requires_confirmation: Whether confirmation is needed
            safety_classification: Safety level
            correlation_id: Optional correlation ID
            
        Returns:
            Valid ally_intent message dictionary
        """
        message = {
            "type": "ally_intent",
            "source": source,
            "intent": intent,
            "confidence": confidence,
            "priority": priority,
            "requires_confirmation": requires_confirmation,
            "safety_classification": safety_classification,
            "msg-sent-timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if slots:
            message["slots"] = slots
        if context:
            message["context"] = context
        if alternatives:
            message["alternatives"] = alternatives
        if correlation_id:
            message["correlation_id"] = correlation_id
        
        # Validate before returning
        self.validator.validate_message(message)
        return message
    
    def create_ally_memory(
        self,
        source: str,
        action: str,
        memory_type: str = None,
        memory_id: str = None,
        content: Dict[str, Any] = None,
        query: Dict[str, Any] = None,
        results: List[Dict[str, Any]] = None,
        context: Dict[str, Any] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Create an ally_memory message
        
        Args:
            source: Source component handling memory
            action: Memory operation (store, retrieve, update, delete, search)
            memory_type: Type of memory
            memory_id: Memory identifier
            content: Memory content (for store/update)
            query: Query parameters (for retrieve/search)
            results: Query results (for responses)
            context: Context information
            correlation_id: Optional correlation ID
            
        Returns:
            Valid ally_memory message dictionary
        """
        message = {
            "type": "ally_memory",
            "source": source,
            "action": action,
            "msg-sent-timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if memory_type:
            message["memory_type"] = memory_type
        if memory_id:
            message["memory_id"] = memory_id
        if content:
            message["content"] = content
        if query:
            message["query"] = query
        if results:
            message["results"] = results
        if context:
            message["context"] = context
        if correlation_id:
            message["correlation_id"] = correlation_id
        
        # Validate before returning
        self.validator.validate_message(message)
        return message
    
    def create_ally_query(
        self,
        source: str,
        query_type: str,
        parameters: Dict[str, Any] = None,
        response_data: Dict[str, Any] = None,
        context: Dict[str, Any] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Create an ally_query message
        
        Args:
            source: Source component making the query
            query_type: Type of query
            parameters: Query parameters
            response_data: Response data (for response messages)
            context: Context information
            correlation_id: Optional correlation ID
            
        Returns:
            Valid ally_query message dictionary
        """
        message = {
            "type": "ally_query",
            "source": source,
            "query_type": query_type,
            "msg-sent-timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if parameters:
            message["parameters"] = parameters
        if response_data:
            message["response_data"] = response_data
        if context:
            message["context"] = context
        if correlation_id:
            message["correlation_id"] = correlation_id
        
        # Validate before returning
        self.validator.validate_message(message)
        return message
    
    def create_ally_status(
        self,
        source: str,
        component: str,
        status: str,
        health: Dict[str, Any] = None,
        capabilities: List[str] = None,
        configuration: Dict[str, Any] = None,
        dependencies: List[Dict[str, Any]] = None,
        alerts: List[Dict[str, Any]] = None,
        context: Dict[str, Any] = None,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Create an ally_status message
        
        Args:
            source: Source component reporting status
            component: Component being reported on
            status: Current status
            health: Health information
            capabilities: Current capabilities
            configuration: Configuration settings
            dependencies: Dependency status
            alerts: Active alerts
            context: Context information
            correlation_id: Optional correlation ID
            
        Returns:
            Valid ally_status message dictionary
        """
        message = {
            "type": "ally_status",
            "source": source,
            "component": component,
            "status": status,
            "msg-sent-timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if health:
            message["health"] = health
        if capabilities:
            message["capabilities"] = capabilities
        if configuration:
            message["configuration"] = configuration
        if dependencies:
            message["dependencies"] = dependencies
        if alerts:
            message["alerts"] = alerts
        if context:
            message["context"] = context
        if correlation_id:
            message["correlation_id"] = correlation_id
        
        # Validate before returning
        self.validator.validate_message(message)
        return message


class MessageSerializer:
    """Handles serialization and deserialization of Chyappy messages"""
    
    def __init__(self, validator: MessageValidator = None):
        """Initialize serializer with optional validator"""
        self.validator = validator or MessageValidator()
    
    def serialize(self, message: Dict[str, Any], validate: bool = True) -> str:
        """
        Serialize message to JSON string
        
        Args:
            message: Message dictionary
            validate: Whether to validate before serializing
            
        Returns:
            JSON string representation
            
        Raises:
            MessageValidationError: If validation fails
        """
        if validate:
            self.validator.validate_message(message)
        
        try:
            return json.dumps(message, ensure_ascii=False, separators=(',', ':'))
        except Exception as e:
            raise MessageValidationError(f"Serialization failed: {e}")
    
    def deserialize(self, json_str: str, validate: bool = True) -> Dict[str, Any]:
        """
        Deserialize JSON string to message dictionary
        
        Args:
            json_str: JSON string to deserialize
            validate: Whether to validate after deserializing
            
        Returns:
            Message dictionary
            
        Raises:
            MessageValidationError: If deserialization or validation fails
        """
        try:
            message = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise MessageValidationError(f"JSON deserialization failed: {e}")
        
        if validate:
            self.validator.validate_message(message)
        
        return message
    
    def serialize_batch(self, messages: List[Dict[str, Any]], validate: bool = True) -> List[str]:
        """
        Serialize multiple messages
        
        Args:
            messages: List of message dictionaries
            validate: Whether to validate each message
            
        Returns:
            List of JSON strings
        """
        return [self.serialize(msg, validate) for msg in messages]
    
    def deserialize_batch(self, json_strings: List[str], validate: bool = True) -> List[Dict[str, Any]]:
        """
        Deserialize multiple JSON strings
        
        Args:
            json_strings: List of JSON strings
            validate: Whether to validate each message
            
        Returns:
            List of message dictionaries
        """
        return [self.deserialize(json_str, validate) for json_str in json_strings]


# Global instances for convenience
_validator = MessageValidator()
_builder = MessageBuilder(_validator)
_serializer = MessageSerializer(_validator)

# Convenience functions
def validate_message(message: Dict[str, Any]) -> bool:
    """Validate a message using the global validator"""
    return _validator.validate_message(message)

def create_tool_call(**kwargs) -> Dict[str, Any]:
    """Create a tool_call message using the global builder"""
    return _builder.create_tool_call(**kwargs)

def create_tool_result(**kwargs) -> Dict[str, Any]:
    """Create a tool_result message using the global builder"""
    return _builder.create_tool_result(**kwargs)

def serialize_message(message: Dict[str, Any], validate: bool = True) -> str:
    """Serialize a message using the global serializer"""
    return _serializer.serialize(message, validate)

def deserialize_message(json_str: str, validate: bool = True) -> Dict[str, Any]:
    """Deserialize a message using the global serializer"""
    return _serializer.deserialize(json_str, validate)