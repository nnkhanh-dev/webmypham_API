from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class ChatMessageResponse(BaseModel):
    id: str
    senderId: str
    text: str
    createdAt: datetime
    senderType: str # 'user' | 'admin'

    model_config = ConfigDict(from_attributes=True)

class AdminConversationResponse(BaseModel):
    conversationId: str
    customerId: str
    customerName: Optional[str]
    lastMessage: Optional[str]
    updatedAt: datetime
    isWaiting: bool # True nếu chưa có admin_id

    model_config = ConfigDict(from_attributes=True)