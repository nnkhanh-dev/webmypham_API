"""seed initial data MOI Cosmetics full categories and products

Revision ID: ver9
Revises: ver8
Create Date: 2026-01-07 20:30:00
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from uuid import uuid4

revision = "ver9"
down_revision = "ver8"
branch_labels = None
depends_on = None


def gen_uuid():
    return str(uuid4())


def upgrade():
    conn = op.get_bind()
    now = datetime.utcnow()

    password_hash = (
        "$argon2id$v=19$m=65536,t=3,p=4$2dv7f+89xzhHyNnb+/9/Lw$"
        "vzMjYXOE17hdU2cl314G2kyTjW2r42bAYSIIz/J1jLc"
    )

    # ===============================
    # 1. CLEAR DATA
    # ===============================
    conn.execute(sa.text("SET FOREIGN_KEY_CHECKS = 0"))
    tables = [
        "cart_items", "carts",
        "product_types", "type_values", "types",
        "products", "brands", "categories",
        "user_roles", "users", "roles",
    ]
    for t in tables:
        conn.execute(sa.text(f"DELETE FROM {t}"))
    conn.execute(sa.text("SET FOREIGN_KEY_CHECKS = 1"))

    # ===============================
    # 2. ROLES
    # ===============================
    role_admin_id = gen_uuid()
    role_client_id = gen_uuid()

    op.bulk_insert(
        sa.table("roles",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {"id": role_admin_id, "name": "ADMIN", "created_at": now, "updated_at": now},
            {"id": role_client_id, "name": "CLIENT", "created_at": now, "updated_at": now},
        ]
    )

    # ===============================
    # 3. USERS
    # ===============================
    admin_id = gen_uuid()
    client_id = gen_uuid()

    op.bulk_insert(
        sa.table("users",
            sa.column("id", sa.String),
            sa.column("email", sa.String),
            sa.column("password_hash", sa.String),
            sa.column("first_name", sa.String),
            sa.column("last_name", sa.String),
            sa.column("phone_number", sa.String),
            sa.column("gender", sa.Integer),
            sa.column("version", sa.Integer),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {
                "id": admin_id,
                "email": "admin@gmail.vn",
                "password_hash": password_hash,
                "first_name": "System",
                "last_name": "Admin",
                "phone_number": "0900000001",
                "gender": 0,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": client_id,
                "email": "khachhang@gmail.com",
                "password_hash": password_hash,
                "first_name": "Hồ Ngọc",
                "last_name": "Hà",
                "phone_number": "0988888888",
                "gender": 1,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            },
        ]
    )

    # ===============================
    # 4. USER ROLES
    # ===============================
    op.bulk_insert(
        sa.table("user_roles",
            sa.column("id", sa.String),
            sa.column("user_id", sa.String),
            sa.column("role_id", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {"id": gen_uuid(), "user_id": admin_id, "role_id": role_admin_id, "created_at": now, "updated_at": now},
            {"id": gen_uuid(), "user_id": client_id, "role_id": role_client_id, "created_at": now, "updated_at": now},
        ]
    )

    # ===============================
    # 5. CATEGORIES
    # ===============================
    categories_def = [
        ("Son Môi", "son-moi"),
        ("Trang Điểm Mắt", "trang-diem-mat"),
        ("Phấn Nước", "phan-nuoc"),
        ("Phấn Phủ", "phan-phu"),
        ("Má Hồng", "ma-hong"),
        ("Trang Điểm Da Mặt", "trang-diem-da-mat"),
        ("Chăm Sóc Da", "cham-soc-da"),
    ]

    category_ids = {}
    categories = []

    for name, slug in categories_def:
        cid = gen_uuid()
        category_ids[slug] = cid
        categories.append({
            "id": cid,
            "name": name,
            "slug": slug,
            "image_path": f"/upload/categories/{slug}.jpg",
            "description": f"Danh mục {name}",
            "parent_id": None,
            "created_at": now,
            "updated_at": now,
        })

    op.bulk_insert(
        sa.table("categories",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("slug", sa.String),
            sa.column("image_path", sa.String),
            sa.column("description", sa.Text),
            sa.column("parent_id", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        categories
    )

    # ===============================
    # 6. BRANDS
    # ===============================
    brand_moi_id = gen_uuid()
    brand_da_id = gen_uuid()

    op.bulk_insert(
        sa.table("brands",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("slug", sa.String),
            sa.column("image_path", sa.String),
            sa.column("description", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {
                "id": brand_moi_id,
                "name": "M.O.I Cosmetics",
                "slug": "moi-cosmetics",
                "image_path": "/upload/brands/moi.png",
                "description": "M.O.I Cosmetics",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": brand_da_id,
                "name": "DA by M.O.I",
                "slug": "da-by-moi",
                "image_path": "/upload/brands/da.png",
                "description": "DA by M.O.I",
                "created_at": now,
                "updated_at": now,
            },
        ]
    )

    # ===============================
    # 7. PRODUCTS
    # ===============================
    products_def = [
        ("Son Thỏi Love M.O.I", brand_moi_id, "son-moi", "son-love-moi"),
        ("Son Tint Bóng Gummy", brand_moi_id, "son-moi", "son-tint-gummy"),
        ("Mascara Perfect Shape", brand_moi_id, "trang-diem-mat", "mascara"),
        ("Cushion Baby Skin", brand_moi_id, "phan-nuoc", "baby-skin"),
        ("Nước Thần Dưỡng Da", brand_da_id, "cham-soc-da", "nuoc-than-da"),
    ]

    product_ids = []
    products = []

    for name, brand_id, cat_slug, slug in products_def:
        pid = gen_uuid()
        product_ids.append(pid)
        products.append({
            "id": pid,
            "name": name,
            "brand_id": brand_id,
            "category_id": category_ids[cat_slug],
            "description": f"Sản phẩm {name} chính hãng M.O.I",
            "thumbnail": f"/upload/products/{slug}.jpg",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        })

    op.bulk_insert(
        sa.table("products",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("brand_id", sa.String),
            sa.column("category_id", sa.String),
            sa.column("description", sa.Text),
            sa.column("thumbnail", sa.String),
            sa.column("is_active", sa.Boolean),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        products
    )

    # ===============================
    # 8. TYPES & VALUES
    # ===============================
    type_id = gen_uuid()

    op.bulk_insert(
        sa.table("types",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [{"id": type_id, "name": "Màu sắc", "created_at": now, "updated_at": now}]
    )

    type_values = []
    type_value_ids = []

    for val in ["Cam Đào", "Hồng Đất", "Đỏ Cam"]:
        tv_id = gen_uuid()
        type_value_ids.append(tv_id)
        type_values.append({
            "id": tv_id,
            "name": val,
            "type_id": type_id,
            "created_at": now,
            "updated_at": now,
        })

    op.bulk_insert(
        sa.table("type_values",
            sa.column("id", sa.String),
            sa.column("name", sa.String),
            sa.column("type_id", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        type_values
    )

    # ===============================
    # 9. PRODUCT TYPES
    # ===============================
    product_types = []

    for pid in product_ids[:2]:  # son
        for tv_id in type_value_ids:
            product_types.append({
                "id": gen_uuid(),
                "product_id": pid,
                "type_value_id": tv_id,
                "image_path": "/upload/products/variants/son.jpg",
                "price": 499000,
                "discount_price": 399000,
                "stock": 100,
                "quantity": 100,
                "volume": "3g",
                "ingredients": "Natural oils",
                "usage": "Apply to lips",
                "skin_type": "All",
                "origin": "Korea",
                "sold": 10,
                "status": "available",
                "created_at": now,
                "updated_at": now,
            })

    op.bulk_insert(
        sa.table("product_types",
            sa.column("id", sa.String),
            sa.column("product_id", sa.String),
            sa.column("type_value_id", sa.String),
            sa.column("image_path", sa.String),
            sa.column("price", sa.Float),
            sa.column("discount_price", sa.Float),
            sa.column("stock", sa.Integer),
            sa.column("quantity", sa.Integer),
            sa.column("volume", sa.String),
            sa.column("ingredients", sa.Text),
            sa.column("usage", sa.String),
            sa.column("skin_type", sa.String),
            sa.column("origin", sa.String),
            sa.column("sold", sa.Integer),
            sa.column("status", sa.String),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        product_types
    )


def downgrade():
    tables = [
        "cart_items", "carts",
        "product_types", "type_values", "types",
        "products", "brands", "categories",
        "user_roles", "users", "roles",
    ]
    for t in tables:
        op.execute(f"DELETE FROM {t}")
