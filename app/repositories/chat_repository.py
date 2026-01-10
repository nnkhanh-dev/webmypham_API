from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from datetime import datetime
import pytz

from app.models import Conversation, Message

# Vietnam timezone (UTC+7)
VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")


def get_vn_now():
    """Get current time in Vietnam timezone"""
    return datetime.now(VN_TZ)


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

    def get_conversation_by_id(self, conversation_id: str):
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def create_conversation(
        self,
        customer_id: str,
        admin_id: str | None = None,
    ):
        conv = Conversation(
            customer_id=customer_id,
            admin_id=admin_id,
        )
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def assign_admin(
        self,
        conversation_id: str,
        admin_id: str,
    ):
        self.db.query(Conversation).filter(Conversation.id == conversation_id).update(
            {
                "admin_id": admin_id,
                "updated_at": get_vn_now(),
            }
        )
        self.db.commit()

    # =========================
    # MESSAGE
    # =========================
    def save_message(
        self,
        conversation_id: str,
        sender_id: str,
        message_text: str,
    ):
        msg = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message=message_text,
        )

        self.db.add(msg)

        self.db.query(Conversation).filter(Conversation.id == conversation_id).update(
            {
                "last_message": message_text,
                "updated_at": get_vn_now(),
            }
        )

        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
    ):
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

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
