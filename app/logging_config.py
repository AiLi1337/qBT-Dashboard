"""
Logging configuration — kept for import compatibility.
Actual logging is initialized in app.main on startup.
"""
import logging


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
