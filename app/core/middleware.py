import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token
from app.core.database import SessionLocal
from app.models.user import User
from types import SimpleNamespace
import logging

logger = logging.getLogger("app")                                                                                           

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
                        # User.id is a UUID string (see AuditMixin). Ensure we compare as str.
                        user = db.query(User).filter(User.id == str(user_id)).first()
                        if user:
                            # load roles while session is open and build a lightweight detached user
                            roles_loaded = [SimpleNamespace(name=r.name) for r in getattr(user, "roles", [])]
                            detached_user = SimpleNamespace(
                                id=user.id,
                                email=user.email,
                                first_name=user.first_name,
                                last_name=user.last_name,
                                phone_number=user.phone_number,
                                dob=user.dob,
                                gender=user.gender,
                                roles=roles_loaded,
                                created_at=user.created_at,
                            )
                            request.state.user = detached_user
                    finally:
                        db.close()

        return await call_next(request)
    
class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Trace-Id"] = trace_id
        logger.info(
            f"Trace: {trace_id} - Path: {request.url.path} - Time: {process_time:.4f}s"
        )
        return response