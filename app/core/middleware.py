from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token
from app.db.database import SessionLocal
from app.models.user import User
from types import SimpleNamespace


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization")
        request.state.user = None
        request.state.token_payload = None

        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]
            payload = decode_access_token(token)
            # attach raw token payload (contains user info) to request.state
            request.state.token_payload = payload
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.id == int(user_id)).first()
                        if user:
                            # load roles while session is open and build a lightweight detached user
                            roles_loaded = [SimpleNamespace(name=r.name) for r in getattr(user, "roles", [])]
                            detached_user = SimpleNamespace(
                                id=user.id,
                                email=user.email,
                                first_name=user.first_name,
                                last_name=user.last_name,
                                phone_number=user.phone_number,
                                roles=roles_loaded,
                            )
                            request.state.user = detached_user
                    finally:
                        db.close()

        return await call_next(request)