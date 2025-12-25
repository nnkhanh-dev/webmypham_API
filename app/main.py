from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers.vouchers import router as vouchers_router
from app.schemas.base import BaseResponse

app = FastAPI()

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