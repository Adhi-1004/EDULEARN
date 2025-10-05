"""
Database package initialization
Contains database connection and session management
"""
from .session import get_db, init_db, close_db
from .mock_db import MockDatabase

__all__ = ["get_db", "init_db", "close_db", "MockDatabase"]