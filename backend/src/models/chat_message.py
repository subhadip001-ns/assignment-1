from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.postgres import Base


class ChatMessage(Base):
    """
    ChatMessage model representing a message in a chat conversation.
    
    Attributes:
        id: Primary key
        user_id: User ID (student ID or admin ID which is 1)
        role: Message role ('user' or 'assistant')
        content: Message content
        created_at: Timestamp when the message was created
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Student ID or admin ID (1)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Optional relationship to student (only for student users, not admin)
    # Note: We use a manual foreign key check in the service layer instead of SQLAlchemy FK
    # This allows admin users (ID 1) to save messages without a student record

