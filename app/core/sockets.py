# app/core/sockets.py
from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # {user_id: websocket_connection}
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        # Accept connection when caller đã xác thực (caller quyết định khi nào accept)
        # await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            try:
                ws = self.active_connections[user_id]
                # try to close politely
                if not ws.client_state.closed:
                    # not all frameworks expose client_state; ignore if not present
                    pass
            except Exception:
                pass
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        ws = self.active_connections.get(user_id)
        if not ws:
            return
        try:
            await ws.send_json(message)
        except Exception:
            # If send fails (client disconnected), remove connection
            try:
                del self.active_connections[user_id]
            except KeyError:
                pass

manager = ConnectionManager()
