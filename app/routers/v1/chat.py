from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.core.sockets import manager
from app.services.chat_service import ChatService

router = APIRouter()


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(...),
):
    # ✅ 1. PHẢI ACCEPT TRƯỚC
    await websocket.accept()

    # ✅ 2. VERIFY TOKEN
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db: Session = SessionLocal()

    try:
        # ✅ 3. CONNECT MANAGER
        await manager.connect(user_id, websocket)
        print(f"✅ WS CONNECTED: {user_id}")

        service = ChatService(db=db, user_id=user_id)

        while True:
            data = await websocket.receive_json()

            response = await service.process_message(
                text=data["text"],
                receiver_id=data.get("receiver_id"),
            )

            payload = response.model_dump()

            # gửi lại cho sender
            await manager.send_personal_message(payload, user_id)

            # gửi cho receiver nếu có
            if data.get("receiver_id"):
                await manager.send_personal_message(
                    payload,
                    data["receiver_id"]
                )

    except WebSocketDisconnect:
        print(f"❌ WS DISCONNECTED: {user_id}")
        manager.disconnect(user_id)

    except Exception as e:
        print("❌ WS ERROR:", e)
        manager.disconnect(user_id)

    finally:
        db.close()
