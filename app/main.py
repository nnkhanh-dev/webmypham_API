from app.core.middleware import AuthMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers.vouchers import router as vouchers_router
from app.routers.auth import router as auth_router
from app.schemas.base import BaseResponse
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# register middleware and routers
app.add_middleware(AuthMiddleware)
app.include_router(auth_router)
app.include_router(vouchers_router)


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    body = BaseResponse(success=False, message=str(exc.detail or "HTTP error"), errors=[str(exc)])
    return JSONResponse(status_code=exc.status_code, content=body.dict())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [f"{e.get('loc')} - {e.get('msg')}" for e in exc.errors()]
    body = BaseResponse(success=False, message="Validation error", errors=errors)
    return JSONResponse(status_code=422, content=body.dict())


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    body = BaseResponse(success=False, message="Internal server error", errors=[str(exc)])
    return JSONResponse(status_code=500, content=body.dict())

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title="Your API", version="1.0.0", routes=app.routes)
    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    # Option A: show Authorize globally (adds lock icon to endpoints)
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi