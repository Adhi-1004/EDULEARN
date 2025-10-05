"""
Core package initialization
Contains configuration, security, and base utilities
"""
from .config import settings
from .security import SecurityManager

__all__ = ["settings", "SecurityManager"]