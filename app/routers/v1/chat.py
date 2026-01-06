from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session

from app.core.sockets import manager
from app.core.database import SessionLocal
from app.services.chat_service import ChatService
from app.core.security import decode_access_token

router = APIRouter()


@router.websocket("/ws/chat/{user_id}")
async def chat_websocket(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(None),  # ws://.../ws/chat/{user_id}?token=xxx
):
    # ===== 1. XÁC THỰC (OPTIONAL – CÓ THỂ BẬT LẠI SAU) =====
    # if token:
    #     payload = decode_access_token(token)
    #     if not payload or str(payload.get("sub")) != user_id:
    #         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    #         return

    # ===== 2. TẠO DB SESSION THỦ CÔNG (BẮT BUỘC) =====
    db: Session = SessionLocal()

    try:
        # ===== 3. ACCEPT KẾT NỐI =====
        await manager.connect(user_id, websocket)
        print(f"✅ USER CONNECTED: {user_id}")

        # sender_id = user_id (TUYỆT ĐỐI KHÔNG HARDCODE)
        service = ChatService(db=db, sender_id=user_id)

        while True:
            # Nhận JSON từ client
            # Ví dụ:
            # USER -> {"text": "hello"}
            # ADMIN -> {"text": "hi", "receiver_id": "customer_id"}
            data = await websocket.receive_json()

            response = await service.process_message(
                text=data["text"],
                receiver_id=data.get("receiver_id"),
            )

            message_payload = response.model_dump()

            # Gửi cho chính người gửi
            await manager.send_personal_message(message_payload, user_id)

            # Nếu có receiver_id (admin gửi cho user)
            if data.get("receiver_id"):
                await manager.send_personal_message(
                    message_payload,
                    data["receiver_id"],
                )

    except WebSocketDisconnect:
        manager.disconnect(user_id)

    except Exception as e:
        print("❌ WebSocket error:", e)
        manager.disconnect(user_id)

    finally:
        db.close()
