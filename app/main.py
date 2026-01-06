from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
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
from app.routers.v1.product import router as product_router

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

# CORS middleware - cho phép Frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",      # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # "https://your-frontend-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# middleware
app.add_middleware(TraceIdMiddleware) 
app.add_middleware(AuthMiddleware)

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
app.include_router(product_router, prefix="/api/v1/products", tags=["products"])

@app.get("/")
def health_check():
    return {"status": "ok"}
