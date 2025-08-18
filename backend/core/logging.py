"""
Logging configuration for the Research-to-Insights Agent
Provides structured logging with different levels and formats
"""

import logging
import sys
from typing import Dict, Any
from datetime import datetime
import json
from core.config import get_settings

# Get settings
settings = get_settings()

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class StructuredLogger:
    """Structured logger with consistent formatting"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        # Add handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            if settings.log_format.lower() == "json":
                handler.setFormatter(JSONFormatter())
            else:
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
            self.logger.addHandler(handler)
    
    def info(self, message: str, extra_fields: Dict[str, Any] = None):
        """Log info message with optional extra fields"""
        if extra_fields:
            self.logger.info(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.info(message)
    
    def error(self, message: str, extra_fields: Dict[str, Any] = None):
        """Log error message with optional extra fields"""
        if extra_fields:
            self.logger.error(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.error(message)
    
    def warning(self, message: str, extra_fields: Dict[str, Any] = None):
        """Log warning message with optional extra fields"""
        if extra_fields:
            self.logger.warning(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.warning(message)
    
    def debug(self, message: str, extra_fields: Dict[str, Any] = None):
        """Log debug message with optional extra fields"""
        if extra_fields:
            self.logger.debug(message, extra={"extra_fields": extra_fields})
        else:
            self.logger.debug(message)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)


# Create default loggers
app_logger = get_logger("research_insights")
api_logger = get_logger("research_insights.api")
db_logger = get_logger("research_insights.database")
ai_logger = get_logger("research_insights.ai")
