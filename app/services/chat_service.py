from sqlalchemy.orm import Session

from app.models import User
from app.repositories.chat_repository import ChatRepository
from app.schemas.response.chat import ChatMessageResponse


class ChatService:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.repo = ChatRepository(db)
        self.user_id = user_id
        self.is_admin = self._check_is_admin()

    # =========================
    # ROLE CHECK
    # =========================
    def _check_is_admin(self) -> bool:
        user = (
            self.db.query(User)
            .filter(User.id == self.user_id)
            .first()
        )
        if not user or not user.roles:
            return False

        return any(role.name.upper() == "ADMIN" for role in user.roles)

    # =========================
    # SEND MESSAGE (WS / REST)
    # =========================
    async def process_message(
        self,
        text: str,
        receiver_id: str | None = None,
    ):
        """
        USER:
          - receiver_id = None

        ADMIN:
          - receiver_id = customer_id (BẮT BUỘC)
        """

        # ===== VALIDATE =====
        if self.is_admin and not receiver_id:
            raise ValueError("Admin must provide receiver_id")

        # ===== DETERMINE PARTICIPANTS =====
        if self.is_admin:
            customer_id = receiver_id
            admin_id = self.user_id
        else:
            customer_id = self.user_id
            admin_id = None

        # ===== GET / CREATE CONVERSATION =====
        conv = self.repo.get_conversation_by_customer(customer_id)

        if not conv:
            conv = self.repo.create_conversation(
                customer_id=customer_id,
                admin_id=admin_id,
            )

        elif self.is_admin and not conv.admin_id:
            # admin claim conversation
            self.repo.assign_admin(
                conversation_id=conv.id,
                admin_id=admin_id,
            )

        # ===== SAVE MESSAGE =====
        msg = self.repo.save_message(
            conversation_id=conv.id,
            sender_id=self.user_id,
            message_text=text,
        )

        # ===== RESPONSE =====
        return ChatMessageResponse(
            id=str(msg.id),
            senderId=msg.sender_id,
            text=msg.message,
            createdAt=msg.created_at,
            senderType="admin" if self.is_admin else "user",
        )

    # =========================
    # GET USER MESSAGES (REST)
    # =========================
    def get_user_messages(self, limit: int = 100):
        """
        Lấy ~100 tin nhắn gần nhất của USER
        senderType:
          - 'user'  nếu senderId == user_id (token)
          - 'admin' nếu ngược lại
        """

        conv = self.repo.get_conversation_by_customer(self.user_id)
        if not conv:
            return []

        messages = self.repo.get_messages_by_conversation(
            conversation_id=conv.id,
            limit=limit,
        )

        # DB order desc → FE cần asc
        messages.reverse()

        return [
            ChatMessageResponse(
                id=str(msg.id),
                senderId=msg.sender_id,
                text=msg.message,
                createdAt=msg.created_at,
                senderType=(
                    "user"
                    if msg.sender_id == self.user_id
                    else "admin"
                ),
            )
            for msg in messages
        ]
