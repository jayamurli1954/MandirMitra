"""
Structured logging configuration for the application
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds timestamp"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Ensure timestamp is in ISO format
        if 'timestamp' not in log_record:
            log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name


def setup_logging(
    level: str = "INFO",
    use_json: bool = True,
    log_file: str = None
) -> logging.Logger:
    """
    Configure structured logging for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (recommended for production)
        log_file: Optional file path to write logs to
        
    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger('app')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    if use_json and JSON_LOGGER_AVAILABLE:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(name)s %(levelname)s %(message)s'
        )
    else:
        # Fallback to standard formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler (always add)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Set logging level for third-party libraries
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    
    return logger


# Initialize logger on module import
logger = setup_logging(
    level="INFO",
    use_json=JSON_LOGGER_AVAILABLE
)


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (defaults to 'app')
        
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f'app.{name}')
    return logger


