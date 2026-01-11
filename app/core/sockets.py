# app/core/sockets.py
from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # {user_id: websocket_connection}
        self.active_connections: Dict[str, WebSocket] = {}
        # {user_id: role} - track user roles for efficient broadcasting
        self.user_roles: Dict[str, str] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        # Accept connection when caller đã xác thực (caller quyết định khi nào accept)
        # await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def set_user_role(self, user_id: str, role: str):
        """Track user role for broadcasting purposes"""
        self.user_roles[user_id] = role

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
        
        # Also remove from user_roles
        if user_id in self.user_roles:
            del self.user_roles[user_id]

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
    
    async def broadcast_to_admins(self, message: dict, exclude_user_id: str = None):
        """Broadcast message to all connected admin users"""
        admin_user_ids = [
            user_id for user_id, role in self.user_roles.items() 
            if role == "ADMIN" and user_id != exclude_user_id
        ]
        
        print(f"📢 Broadcasting to {len(admin_user_ids)} admins")
        
        for admin_id in admin_user_ids:
            await self.send_personal_message(message, admin_id)

manager = ConnectionManager()
