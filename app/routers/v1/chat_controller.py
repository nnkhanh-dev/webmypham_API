from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permission import require_roles
from app.repositories.chat_repository import ChatRepository
from app.services.chat_service import ChatService
from app.schemas.response.chat import ChatMessageResponse, AdminConversationResponse
from app.schemas.response.base import BaseResponse
from app.models import User

router = APIRouter()


# ======================================================
# USER - Lấy tin nhắn của chính mình
# ======================================================
@router.get(
    "/messages",
    response_model=BaseResponse[List[ChatMessageResponse]],
)
def get_user_messages(
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    USER:
    - Lấy ~`limit` tin nhắn gần nhất
    """
    service = ChatService(db, current_user.id)
    messages = service.get_user_messages(limit=limit)

    return BaseResponse(
        success=True,
        message="OK",
        data=messages,
    )


# ======================================================
# ADMIN - Lấy danh sách conversation
# ======================================================
@router.get(
    "/admin/conversations",
    response_model=BaseResponse[List[AdminConversationResponse]],
)
def get_admin_conversations(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    """
    ADMIN:
    - Danh sách conversations (đã claim + chưa claim)
    """
    admin_id = str(current_user.id)
    repo = ChatRepository(db)
    conversations = repo.get_admin_chats(admin_id)

    result: List[AdminConversationResponse] = []
    for conv in conversations:
        # Get customer name from first_name and last_name
        customer_name = None
        if conv.customer:
            first_name = conv.customer.first_name or ""
            last_name = conv.customer.last_name or ""
            customer_name = f"{first_name} {last_name}".strip() or conv.customer.email
        
        result.append(
            AdminConversationResponse(
                conversationId=str(conv.id),
                customerId=str(conv.customer_id),
                customerName=customer_name,
                lastMessage=conv.last_message,
                updatedAt=conv.updated_at,
                isWaiting=conv.admin_id is None,
                isRead=conv.is_read,  # Add read status
            )
        )

    return BaseResponse(
        success=True,
        message="OK",
        data=result,
    )


# ======================================================
# ADMIN - Lấy tin nhắn theo conversation
# ======================================================
@router.get(
    "/admin/messages/{conversation_id}",
    response_model=BaseResponse[List[ChatMessageResponse]],
)
def get_admin_messages(
    conversation_id: str,
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    """
    ADMIN:
    - Lấy tin nhắn của 1 conversation
    """
    admin_id = str(current_user.id)
    repo = ChatRepository(db)
    messages = repo.get_messages_by_conversation(
        conversation_id=conversation_id,
        limit=limit,
    )

    # DB desc → FE asc
    messages.reverse()

    response = [
        ChatMessageResponse(
            id=str(msg.id),
            senderId=msg.sender_id,
            text=msg.message,
            createdAt=msg.created_at,
            senderType="admin" if msg.sender_id == admin_id else "user",
        )
        for msg in messages
    ]

    return BaseResponse(
        success=True,
        message="OK",
        data=response,
    )


# ======================================================
# ADMIN - Claim conversation
# ======================================================
@router.post(
    "/admin/conversations/{conversation_id}/claim",
    response_model=BaseResponse[dict],
)
def claim_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    """
    ADMIN:
    - Nhận xử lý conversation đang chờ
    """
    admin_id = str(current_user.id)
    repo = ChatRepository(db)
    conv = repo.get_conversation_by_id(conversation_id)

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conv.admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation already claimed",
        )

    repo.assign_admin(
        conversation_id=conversation_id,
        admin_id=admin_id,
    )

    return BaseResponse(
        success=True,
        message="Conversation claimed successfully",
        data={"conversationId": conversation_id},
    )


# ======================================================
# ADMIN - Mark conversation as read
# ======================================================
@router.post(
    "/admin/conversations/{conversation_id}/read",
    response_model=BaseResponse[dict],
)
def mark_conversation_as_read(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    """
    ADMIN:
    - Đánh dấu conversation đã đọc
    """
    repo = ChatRepository(db)
    conv = repo.get_conversation_by_id(conversation_id)

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Mark as read
    repo.mark_as_read(conversation_id)

    return BaseResponse(
        success=True,
        message="Conversation marked as read",
        data={"conversationId": conversation_id},
    )
