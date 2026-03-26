"""
Database model package
Exports all ORM models and the db instance
"""
from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance and initialize it in app.py
db = SQLAlchemy()

from models.user import User
from models.knowledge_base import KnowledgeBase
from models.document import Document
from models.chat_history import ChatHistory

