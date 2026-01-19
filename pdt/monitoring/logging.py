"""
Structured Logging.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any


class StructuredLogger:
    """Structured logger for application logging."""
    
    def __init__(self, name: str = "pdt", level: int = logging.INFO):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log(self, level: str, message: str, **kwargs):
        """
        Log structured message.
        
        Args:
            level: Log level ('info', 'warning', 'error', 'debug')
            message: Log message
            **kwargs: Additional structured data
        """
        log_data = {
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        log_message = json.dumps(log_data)
        
        if level == "info":
            self.logger.info(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "error":
            self.logger.error(log_message)
        elif level == "debug":
            self.logger.debug(log_message)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log("error", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log("debug", message, **kwargs)



