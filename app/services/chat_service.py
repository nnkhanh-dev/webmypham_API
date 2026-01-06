from sqlalchemy.orm import Session
from app.models import User
from app.repositories.chat_repository import ChatRepository
from app.schemas.response.chat import ChatMessageResponse


class ChatService:
    def __init__(self, db: Session, sender_id: str):
        self.db = db
        self.repo = ChatRepository(db)
        self.sender_id = sender_id
        self.is_admin = self._check_is_admin()

    def _check_is_admin(self) -> bool:
        user = (
            self.db.query(User)
            .filter(User.id == self.sender_id)
            .first()
        )
        if not user or not user.roles:
            return False
        return any(role.name.upper() == "ADMIN" for role in user.roles)

    async def process_message(self, text: str, receiver_id: str | None = None):
        """
        USER  gửi: receiver_id = None
        ADMIN gửi: receiver_id = customer_id (BẮT BUỘC)
        """

        # ===== VALIDATE =====
        if self.is_admin and not receiver_id:
            raise ValueError("Admin must provide receiver_id")

        # ===== XÁC ĐỊNH CUSTOMER / ADMIN =====
        if self.is_admin:
            customer_id = receiver_id
            admin_id = self.sender_id
        else:
            customer_id = self.sender_id
            admin_id = None

        # ===== GET / CREATE CONVERSATION =====
        conv = self.repo.get_conversation_by_customer(customer_id)

        if not conv:
            conv = self.repo.create_conversation(
                customer_id=customer_id,
                admin_id=admin_id,
            )
        elif self.is_admin and not conv.admin_id:
            conv.admin_id = admin_id
            self.db.commit()

        # ===== SAVE MESSAGE =====
        msg = self.repo.save_message(
            conversation_id=conv.id,
            sender_id=self.sender_id,
            message_text=text,
        )

        # ===== RESPONSE =====
        return ChatMessageResponse(
            id=str(msg.id),
            senderId=self.sender_id,
            text=msg.message,
            createdAt=msg.created_at,
            senderType="admin" if self.is_admin else "user",
        )
