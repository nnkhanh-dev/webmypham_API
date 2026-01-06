from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from datetime import datetime

from app.models import Conversation, Message


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    # =========================
    # CONVERSATION
    # =========================
    def get_conversation_by_customer(self, customer_id: str):
        return (
            self.db.query(Conversation)
            .filter(Conversation.customer_id == customer_id)
            .first()
        )

    def create_conversation(self, customer_id: str, admin_id: str | None = None):
        conv = Conversation(
            customer_id=customer_id,
            admin_id=admin_id,
        )
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    # =========================
    # MESSAGE
    # =========================
    def save_message(
        self,
        conversation_id: str,
        sender_id: str,
        message_text: str,
    ):
        new_msg = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message=message_text,
        )

        # Atomic update
        self.db.add(new_msg)

        self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).update(
            {
                "last_message": message_text,
                "updated_at": datetime.utcnow(),
            }
        )

        self.db.commit()
        self.db.refresh(new_msg)
        return new_msg

    # =========================
    # ADMIN
    # =========================
    def get_admin_chats(self, admin_id: str):
        return (
            self.db.query(Conversation)
            .filter(
                or_(
                    Conversation.admin_id == admin_id,
                    Conversation.admin_id.is_(None),
                )
            )
            .options(joinedload(Conversation.customer))
            .order_by(Conversation.updated_at.desc())
            .all()
        )
