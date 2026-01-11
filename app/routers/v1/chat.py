from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.core.sockets import manager
from app.services.chat_service import ChatService
from app.repositories.user_repository import UserRepository

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
        
        # Check if user is admin
        user_repo = UserRepository(db)
        current_user = user_repo.get_with_roles(user_id)
        
        # User has a roles relationship (list of Role objects)
        is_admin = False
        user_role = "USER"
        if current_user and current_user.roles:
            is_admin = any(role.name == "ADMIN" for role in current_user.roles)
            # Get first role name for tracking
            user_role = current_user.roles[0].name if current_user.roles else "USER"
        
        # Track user role for broadcasting
        manager.set_user_role(user_id, user_role)

        service = ChatService(db=db, user_id=user_id)

        while True:
            data = await websocket.receive_json()
            print(f"📩 Received from {user_id} ({'ADMIN' if is_admin else 'USER'}): {data}")

            response = await service.process_message(
                text=data["text"],
                receiver_id=data.get("receiver_id"),
            )

            # Serialize with JSON mode to handle datetime
            payload = response.model_dump(mode='json')
            print(f"📤 Sending response: {payload}")

            # gửi lại cho sender (confirmation)
            await manager.send_personal_message(payload, user_id)
            print(f"✅ Sent to sender: {user_id}")

            # gửi cho receiver nếu có (admin -> specific user)
            if data.get("receiver_id"):
                await manager.send_personal_message(
                    payload,
                    data["receiver_id"]
                )
                print(f"✅ Sent to receiver: {data['receiver_id']}")
            
            # 🔥 Broadcast to all admins if message is from user
            if not is_admin:
                print(f"📢 Broadcasting to all admins (user message)")
                await manager.broadcast_to_admins(payload, exclude_user_id=user_id)
            else:
                print(f"ℹ️  Admin message - not broadcasting to other admins")

    except WebSocketDisconnect:
        print(f"❌ WS DISCONNECTED: {user_id}")
        manager.disconnect(user_id)

    except Exception as e:
        print("❌ WS ERROR:", e)
        manager.disconnect(user_id)

    finally:
        db.close()
