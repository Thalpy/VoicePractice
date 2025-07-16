"""
Centralized error handling and logging for Voice Practice application.
"""

import logging
import traceback
import os
from datetime import datetime
from config_manager import config

class VoicePracticeLogger:
    """Custom logger for the Voice Practice application"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = config.get_setting('logs', './logs/')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"voice_practice_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG if config.get_setting('dev', False) else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('VoicePractice')
    
    def log_error(self, component: str, error: Exception, context: str = ""):
        """Log an error with context"""
        error_msg = f"[{component}] {context}: {str(error)}"
        self.logger.error(error_msg)
        
        if config.get_setting('dev', False):
            self.logger.debug(traceback.format_exc())
    
    def log_warning(self, component: str, message: str):
        """Log a warning"""
        self.logger.warning(f"[{component}] {message}")
    
    def log_info(self, component: str, message: str):
        """Log an info message"""
        self.logger.info(f"[{component}] {message}")
    
    def log_debug(self, component: str, message: str):
        """Log a debug message"""
        if config.get_setting('dev', False):
            self.logger.debug(f"[{component}] {message}")

# Global logger instance
logger = VoicePracticeLogger()

def handle_exception(component: str, context: str = ""):
    """Decorator for handling exceptions in functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_error(component, e, context or func.__name__)
                return None
        return wrapper
    return decorator