# base.py - Base data models and validation utilities
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from abc import ABC, abstractmethod

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)

class BaseValidator(ABC):
    """Abstract base class for validators"""
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate a value and return True if valid"""
        pass
    
    @abstractmethod
    def get_error_message(self, value: Any) -> str:
        """Get error message for invalid value"""
        pass

class RequiredValidator(BaseValidator):
    """Validator for required fields"""
    
    def validate(self, value: Any) -> bool:
        return value is not None and value != ""
    
    def get_error_message(self, value: Any) -> str:
        return "This field is required"

class LengthValidator(BaseValidator):
    """Validator for string length constraints"""
    
    def __init__(self, min_length: int = 0, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        length = len(value)
        if length < self.min_length:
            return False
        
        if self.max_length is not None and length > self.max_length:
            return False
        
        return True
    
    def get_error_message(self, value: Any) -> str:
        if self.max_length is not None:
            return f"Length must be between {self.min_length} and {self.max_length} characters"
        return f"Length must be at least {self.min_length} characters"

class EmailValidator(BaseValidator):
    """Validator for email addresses"""
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, value) is not None
    
    def get_error_message(self, value: Any) -> str:
        return "Invalid email address format"

class ChoiceValidator(BaseValidator):
    """Validator for choice fields"""
    
    def __init__(self, choices: List[Any]):
        self.choices = choices
    
    def validate(self, value: Any) -> bool:
        return value in self.choices
    
    def get_error_message(self, value: Any) -> str:
        return f"Value must be one of: {', '.join(map(str, self.choices))}"

@dataclass
class BaseModel:
    """Base model with validation and serialization capabilities"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Post-initialization validation"""
        self.validate()
    
    def validate(self) -> None:
        """Validate the model instance"""
        validators = getattr(self.__class__, '_validators', {})
        
        for field_name, field_validators in validators.items():
            value = getattr(self, field_name, None)
            
            for validator in field_validators:
                if not validator.validate(value):
                    raise ValidationError(
                        validator.get_error_message(value),
                        field=field_name,
                        value=value
                    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, datetime):
                result[field_name] = field_value.isoformat()
            elif isinstance(field_value, Enum):
                result[field_name] = field_value.value
            elif hasattr(field_value, 'to_dict'):
                result[field_name] = field_value.to_dict()
            elif isinstance(field_value, (list, tuple)):
                result[field_name] = [
                    item.to_dict() if hasattr(item, 'to_dict') else item
                    for item in field_value
                ]
            else:
                result[field_name] = field_value
        
        return result
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        # Convert datetime strings back to datetime objects
        for field_name, field_value in data.items():
            if field_name.endswith('_at') and isinstance(field_value, str):
                try:
                    data[field_name] = datetime.fromisoformat(field_value)
                except ValueError:
                    pass
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseModel':
        """Create model instance from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update(self, **kwargs) -> None:
        """Update model fields and re-validate"""
        for field_name, field_value in kwargs.items():
            if hasattr(self, field_name):
                setattr(self, field_name, field_value)
        
        self.updated_at = datetime.utcnow()
        self.validate()

def add_validators(validators: Dict[str, List[BaseValidator]]):
    """Decorator to add validators to a model class"""
    def decorator(cls):
        cls._validators = validators
        return cls
    return decorator