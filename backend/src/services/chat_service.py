from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from src.models.chat_message import ChatMessage
from src.services.student_service import StudentService


class ChatService:
    """Service layer for chat message operations"""

    @staticmethod
    def save_message(
        db: Session,
        user_id: int,
        role: str,
        content: str
    ) -> ChatMessage:
        """
        Save a chat message to the database.

        Args:
            db: Database session
            user_id: User ID (student ID, or admin ID which is 1)
            role: Message role ('user' or 'assistant')
            content: Message content

        Returns:
            Created ChatMessage object

        Raises:
            HTTPException: If user not found or invalid role
        """
        # Validate role
        if role not in ['user', 'assistant']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}. Must be 'user' or 'assistant'"
            )

        # For admin users (ID 1), we'll use a special handling
        # For now, skip validation for admin - they can still save messages
        # In a production system, you might want a separate admin_chat_messages table
        if user_id != 1:
            # Verify student exists (will raise 404 if not found)
            StudentService.get_student(db, user_id)

        try:
            chat_message = ChatMessage(
                user_id=user_id,
                role=role,
                content=content
            )
            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)
            return chat_message
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save chat message: {str(e)}"
            )

    @staticmethod
    def get_chat_history(
        db: Session,
        user_id: int,
        limit: int = 100
    ) -> List[ChatMessage]:
        """
        Get chat history for a user, ordered by creation time (oldest first).

        Args:
            db: Database session
            user_id: User ID (student ID, or admin ID which is 1)
            limit: Maximum number of messages to return (default: 100)

        Returns:
            List of ChatMessage objects ordered by created_at (ascending)

        Raises:
            HTTPException: If user not found
        """
        # For admin users (ID 1), skip validation
        if user_id != 1:
            # Verify student exists (will raise 404 if not found)
            StudentService.get_student(db, user_id)

        return db.query(ChatMessage)\
            .filter(ChatMessage.user_id == user_id)\
            .order_by(ChatMessage.created_at.asc())\
            .limit(limit)\
            .all()

    @staticmethod
    def clear_chat_history(db: Session, user_id: int) -> None:
        """
        Clear all chat history for a user.

        Args:
            db: Database session
            user_id: User ID (student ID, or admin ID which is 1)

        Raises:
            HTTPException: If user not found or deletion fails
        """
        # For admin users (ID 1), skip validation
        if user_id != 1:
            # Verify student exists (will raise 404 if not found)
            StudentService.get_student(db, user_id)

        try:
            db.query(ChatMessage)\
                .filter(ChatMessage.user_id == user_id)\
                .delete()
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to clear chat history: {str(e)}"
            )

