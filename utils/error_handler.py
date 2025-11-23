"""
Structured error handling system for consistent error responses and recovery.
"""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger("error_handler")

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"           # Minor issue, can continue
    MEDIUM = "medium"     # Significant issue, may need retry
    HIGH = "high"         # Critical issue, requires intervention
    FATAL = "fatal"       # Unrecoverable error

class ErrorCategory(Enum):
    """Error categories for classification."""
    NETWORK = "network"
    API = "api"
    VALIDATION = "validation"
    PARSING = "parsing"
    FILESYSTEM = "filesystem"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"

@dataclass
class StructuredError:
    """
    Structured error object with detailed information.
    """
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    stage: str  # Which pipeline stage (mining, curation, etc.)
    details: Optional[Dict[str, Any]] = None
    recoverable: bool = True
    retry_suggested: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "stage": self.stage,
            "details": self.details or {},
            "recoverable": self.recoverable,
            "retry_suggested": self.retry_suggested
        }
        
    def to_user_message(self) -> str:
        """Convert to user-friendly message."""
        emoji_map = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "❌",
            ErrorSeverity.FATAL: "🚨"
        }
        
        emoji = emoji_map.get(self.severity, "❌")
        msg = f"{emoji} {self.message}"
        
        if self.retry_suggested:
            msg += " (Retry suggested)"
            
        return msg

class ErrorHandler:
    """
    Centralized error handling with recovery strategies.
    """
    
    @staticmethod
    def handle_mining_error(error: Exception, query: str, attempted: int) -> StructuredError:
        """Handle mining stage errors."""
        error_str = str(error)
        
        # Classify error
        if "timeout" in error_str.lower():
            return StructuredError(
                category=ErrorCategory.TIMEOUT,
                severity=ErrorSeverity.MEDIUM,
                message=f"Mining timeout after attempting {attempted} images",
                stage="mining",
                details={"query": query, "attempted": attempted, "error": error_str},
                recoverable=True,
                retry_suggested=True
            )
        elif "rate limit" in error_str.lower() or "429" in error_str:
            return StructuredError(
                category=ErrorCategory.RATE_LIMIT,
                severity=ErrorSeverity.MEDIUM,
                message="Rate limit reached during mining",
                stage="mining",
                details={"query": query, "error": error_str},
                recoverable=True,
                retry_suggested=True
            )
        elif "api key" in error_str.lower() or "authentication" in error_str.lower():
            return StructuredError(
                category=ErrorCategory.AUTHENTICATION,
                severity=ErrorSeverity.FATAL,
                message="API authentication failed",
                stage="mining",
                details={"error": error_str},
                recoverable=False,
                retry_suggested=False
            )
        else:
            return StructuredError(
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                message=f"Mining failed: {error_str}",
                stage="mining",
                details={"query": query, "error": error_str},
                recoverable=True,
                retry_suggested=True
            )
    
    @staticmethod
    def handle_curation_error(error: Exception, image_path: str) -> StructuredError:
        """Handle curation stage errors."""
        error_str = str(error)
        
        if "cannot identify image" in error_str.lower() or "corrupt" in error_str.lower():
            return StructuredError(
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.LOW,
                message=f"Corrupted image skipped: {image_path}",
                stage="curation",
                details={"image": image_path, "error": error_str},
                recoverable=True,
                retry_suggested=False
            )
        else:
            return StructuredError(
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                message=f"Curation error: {error_str}",
                stage="curation",
                details={"image": image_path, "error": error_str},
                recoverable=True,
                retry_suggested=False
            )
    
    @staticmethod
    def handle_annotation_error(error: Exception, image_path: str, query: str) -> StructuredError:
        """Handle annotation stage errors."""
        error_str = str(error)
        
        if "json" in error_str.lower() or "parse" in error_str.lower():
            return StructuredError(
                category=ErrorCategory.PARSING,
                severity=ErrorSeverity.MEDIUM,
                message=f"Failed to parse annotation JSON for {image_path}",
                stage="annotation",
                details={"image": image_path, "query": query, "error": error_str},
                recoverable=True,
                retry_suggested=True
            )
        elif "timeout" in error_str.lower():
            return StructuredError(
                category=ErrorCategory.TIMEOUT,
                severity=ErrorSeverity.MEDIUM,
                message=f"Annotation timeout for {image_path}",
                stage="annotation",
                details={"image": image_path, "query": query},
                recoverable=True,
                retry_suggested=True
            )
        else:
            return StructuredError(
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.HIGH,
                message=f"Annotation failed: {error_str}",
                stage="annotation",
                details={"image": image_path, "query": query, "error": error_str},
                recoverable=True,
                retry_suggested=False
            )
    
    @staticmethod
    def handle_engineering_error(error: Exception, filename: str) -> StructuredError:
        """Handle engineering/save stage errors."""
        error_str = str(error)
        
        if "permission" in error_str.lower():
            return StructuredError(
                category=ErrorCategory.FILESYSTEM,
                severity=ErrorSeverity.FATAL,
                message="Permission denied when saving dataset",
                stage="engineering",
                details={"filename": filename, "error": error_str},
                recoverable=False,
                retry_suggested=False
            )
        elif "disk" in error_str.lower() or "space" in error_str.lower():
            return StructuredError(
                category=ErrorCategory.FILESYSTEM,
                severity=ErrorSeverity.FATAL,
                message="Insufficient disk space",
                stage="engineering",
                details={"error": error_str},
                recoverable=False,
                retry_suggested=False
            )
        else:
            return StructuredError(
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.HIGH,
                message=f"Save failed: {error_str}",
                stage="engineering",
                details={"filename": filename, "error": error_str},
                recoverable=True,
                retry_suggested=True
            )
    
    @staticmethod
    def should_retry(error: StructuredError, attempt: int, max_attempts: int = 3) -> bool:
        """
        Determine if operation should be retried.
        
        Args:
            error: The structured error
            attempt: Current attempt number
            max_attempts: Maximum retry attempts
            
        Returns:
            bool indicating if retry should be attempted
        """
        if attempt >= max_attempts:
            return False
            
        if not error.recoverable:
            return False
            
        if error.severity == ErrorSeverity.FATAL:
            return False
            
        # Retry on rate limits, timeouts, and network issues
        retry_categories = [
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.TIMEOUT,
            ErrorCategory.NETWORK
        ]
        
        return error.category in retry_categories or error.retry_suggested
    
    @staticmethod
    def log_error(error: StructuredError):
        """Log error with appropriate level."""
        severity_to_log_level = {
            ErrorSeverity.LOW: logger.warning,
            ErrorSeverity.MEDIUM: logger.warning,
            ErrorSeverity.HIGH: logger.error,
            ErrorSeverity.FATAL: logger.critical
        }
        
        log_func = severity_to_log_level.get(error.severity, logger.error)
        log_func(
            f"[{error.stage.upper()}] {error.message}",
            extra=error.details or {}
        )

def create_error_response(
    status: str = "error",
    message: str = "",
    error: Optional[StructuredError] = None,
    data: Any = None
) -> Dict[str, Any]:
    """
    Create standardized error response dictionary.
    
    Args:
        status: Response status ("error", "partial_success", etc.)
        message: Human-readable message
        error: Optional StructuredError object
        data: Optional data to include
        
    Returns:
        Standardized error response dict
    """
    response = {
        "status": status,
        "message": message
    }
    
    if error:
        response["error"] = error.to_dict()
        
    if data is not None:
        response["data"] = data
        
    return response

def create_success_response(
    message: str = "Success",
    data: Any = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized success response dictionary.
    
    Args:
        message: Success message
        data: Data to include
        metadata: Optional metadata
        
    Returns:
        Standardized success response dict
    """
    response = {
        "status": "success",
        "message": message
    }
    
    if data is not None:
        response["data"] = data
        
    if metadata:
        response["metadata"] = metadata
        
    return response
