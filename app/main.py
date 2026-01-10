from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.middleware import AuthMiddleware,TraceIdMiddleware
from app.routers.v1.vouchers import router as vouchers_router
from app.routers.v1.brands import router as brands_router
from app.routers.v1.types import router as types_router
from app.routers.v1.type_values import router as type_values_router
from app.routers.v1.carts import router as carts_router
from app.routers.v1.wishlists import router as wishlists_router
from app.routers.v1.auth import router as auth_router
from app.routers.v1.users import router as users_router
from app.routers.v1.categories import router as categories_router
from app.routers.v1.review import router as reviews_router
from app.routers.v1.addresses import router as addresses_router
from app.routers.v1.administrative import router as administrative_router
from app.routers.v1.product import router as product_router
from app.routers.v1.product_type import router as product_type_router
from app.routers.v1.chat import router as chat_router
from app.routers.v1.chat_controller import router as chat_router_controller
from app.routers.v1.order import router as orders_router
from app.routers.v1.upload import router as upload_router
from app.routers.v1.checkout import router as checkout_router
from app.routers.v1.statistics import router as statistics_router
from app.routers.v1.notifications import router as notifications_router

app = FastAPI(
    title="WebMyPham API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Middleware - IMPORTANT: Add in reverse order (last added = first executed)
# 1. AuthMiddleware (executes third)
app.add_middleware(AuthMiddleware)

# 2. TraceIdMiddleware (executes second)
app.add_middleware(TraceIdMiddleware) 

# 3. CORS middleware (executes first - MUST BE LAST ADDED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",      # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(vouchers_router, prefix="/api/v1/vouchers", tags=["vouchers"])
app.include_router(brands_router, prefix="/api/v1/brands", tags=["brands"])
app.include_router(types_router, prefix="/api/v1/types", tags=["types"])
app.include_router(type_values_router, prefix="/api/v1/types", tags=["type-values"])
app.include_router(categories_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(carts_router, prefix="/api/v1/carts", tags=["carts"])
app.include_router(wishlists_router, prefix="/api/v1/wishlists", tags=["wishlists"])
app.include_router(reviews_router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(addresses_router, prefix="/api/v1/users/me/addresses", tags=["addresses"])
app.include_router(administrative_router, prefix="/api/v1/administrative", tags=["administrative"])
app.include_router(product_router, prefix="/api/v1/products", tags=["products"])
app.include_router(product_type_router, prefix="/api/v1/products", tags=["Product Types"])
app.include_router(chat_router_controller, prefix="/api/v1/chat", tags=["chat"])
app.include_router(chat_router)

app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(upload_router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(checkout_router, prefix="/api/v1/checkout", tags=["checkout"])
app.include_router(statistics_router, prefix="/api/v1/statistics", tags=["statistics"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])

@app.get("/")
def health_check():
    return {"status": "ok"}

