"""
API package initialization
Contains all API endpoint routers and configurations
"""
from .v1 import api_router

__all__ = ["api_router"]