"""seed data

Revision ID: ver2
Revises: ver1
Create Date: 2026-01-12 22:03:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision: str = 'ver2'
down_revision: Union[str, None] = 'ver1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get connection
    conn = op.get_bind()
    
    # Helper function to generate UUID
    def gen_uuid():
        return str(uuid.uuid4())
    
    now = datetime.now()
    
    # ===== SEED ROLES (10 records) =====
    roles_data = []
    role_ids = []
    for i in range(10):
        role_id = gen_uuid()
        role_ids.append(role_id)
        roles_data.append({
            'id': role_id,
            'name': f'Role_{i+1}' if i >= 3 else ['Admin', 'Customer', 'Staff'][i],
            'description': f'Description for role {i+1}',
            'created_at': now,
            'updated_at': now
        })
    
    if roles_data:
        op.bulk_insert(sa.table('roles',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), roles_data)
    
    # ===== SEED BRANDS (10 records) =====
    brands_data = []
    brand_ids = []
    brand_names = ['La Roche-Posay', 'Vichy', 'Bioderma', 'Eucerin', 'Cerave', 
                   'Neutrogena', 'Innisfree', 'The Ordinary', 'Cocoon', 'Klairs']
    
    for i in range(10):
        brand_id = gen_uuid()
        brand_ids.append(brand_id)
        brands_data.append({
            'id': brand_id,
            'name': brand_names[i],
            'slug': brand_names[i].lower().replace(' ', '-'),
            'image_path': f'/uploads/brands/{brand_names[i].lower().replace(" ", "-")}.jpg',
            'description': f'Premium cosmetics brand {brand_names[i]}',
            'created_at': now,
            'updated_at': now
        })
    
    if brands_data:
        op.bulk_insert(sa.table('brands',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('slug', sa.String),
            sa.column('image_path', sa.String),
            sa.column('description', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), brands_data)
    
    # ===== SEED CATEGORIES (10 records) =====
    categories_data = []
    category_ids = []
    category_names = ['Skincare', 'Makeup', 'Haircare', 'Body Care', 'Sunscreen',
                      'Cleansers', 'Moisturizers', 'Serums', 'Toners', 'Masks']
    
    for i in range(10):
        category_id = gen_uuid()
        category_ids.append(category_id)
        categories_data.append({
            'id': category_id,
            'name': category_names[i],
            'slug': category_names[i].lower().replace(' ', '-'),
            'image_path': f'/uploads/categories/{category_names[i].lower().replace(" ", "-")}.jpg',
            'description': f'Category for {category_names[i]} products',
            'created_at': now,
            'updated_at': now
        })
    
    if categories_data:
        op.bulk_insert(sa.table('categories',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('slug', sa.String),
            sa.column('image_path', sa.String),
            sa.column('description', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), categories_data)
    
    # ===== SEED TYPES (10 records) =====
    types_data = []
    type_ids = []
    type_names = ['Size', 'Color', 'Scent', 'Variant', 'Package',
                  'Edition', 'Formula', 'Texture', 'Skin Type', 'SPF Level']
    
    for i in range(10):
        type_id = gen_uuid()
        type_ids.append(type_id)
        types_data.append({
            'id': type_id,
            'name': type_names[i],
            'description': f'Product type: {type_names[i]}',
            'created_at': now,
            'updated_at': now
        })
    
    if types_data:
        op.bulk_insert(sa.table('types',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), types_data)
    
    # ===== SEED TYPE_VALUES (10 records per type - total 100, but we'll do 10 for simplicity) =====
    type_values_data = []
    type_value_ids = []
    
    # Size type values
    size_values = ['50ml', '100ml', '150ml', '200ml', '250ml', '30ml', '75ml', '125ml', '175ml', '300ml']
    for i in range(10):
        type_value_id = gen_uuid()
        type_value_ids.append(type_value_id)
        type_values_data.append({
            'id': type_value_id,
            'name': size_values[i],
            'type_id': type_ids[0],  # Size type
            'created_at': now,
            'updated_at': now
        })
    
    if type_values_data:
        op.bulk_insert(sa.table('type_values',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('type_id', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), type_values_data)
    
    # ===== SEED USERS (10 records) =====
    users_data = []
    user_ids = []
    
    for i in range(10):
        user_id = gen_uuid()
        user_ids.append(user_id)
        users_data.append({
            'id': user_id,
            'email': f'user{i+1}@example.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzR1vKxqXu',  # hashed "password123"
            'phone_number': f'090000000{i}',
            'first_name': f'First{i+1}',
            'last_name': f'Last{i+1}',
            'gender': i % 3,  # 0: Female, 1: Male, 2: Other
            'email_confirmed': True,
            'version': 1,
            'created_at': now,
            'updated_at': now
        })
    
    if users_data:
        op.bulk_insert(sa.table('users',
            sa.column('id', sa.String),
            sa.column('email', sa.String),
            sa.column('password_hash', sa.String),
            sa.column('phone_number', sa.String),
            sa.column('first_name', sa.String),
            sa.column('last_name', sa.String),
            sa.column('gender', sa.Integer),
            sa.column('email_confirmed', sa.Boolean),
            sa.column('version', sa.Integer),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), users_data)
    
    # ===== SEED USER_ROLES (10 records) =====
    user_roles_data = []
    for i in range(10):
        user_roles_data.append({
            'id': gen_uuid(),
            'user_id': user_ids[i],
            'role_id': role_ids[1] if i >= 3 else role_ids[i % 3],  # First 3 users get Admin/Customer/Staff, rest get Customer
            'created_at': now,
            'updated_at': now
        })
    
    if user_roles_data:
        op.bulk_insert(sa.table('user_roles',
            sa.column('id', sa.String),
            sa.column('user_id', sa.String),
            sa.column('role_id', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), user_roles_data)
    
    # ===== SEED PRODUCTS (20 records) =====
    products_data = []
    product_ids = []
    product_names = [
        'Hyaluronic Acid Serum', 'Vitamin C Brightening Cream', 'Niacinamide Toner',
        'Gentle Foam Cleanser', 'Sunscreen SPF50+', 'Retinol Night Cream',
        'AHA/BHA Exfoliating Toner', 'Ceramide Moisturizer', 'Tea Tree Oil Serum',
        'Collagen Eye Cream', 'Rosehip Facial Oil', 'Clay Mask Purifying',
        'Peptide Anti-Aging Cream', 'Aloe Vera Soothing Gel', 'Micellar Water',
        'Green Tea Face Mist', 'Snail Mucin Essence', 'Centella Calming Cream',
        'Vitamin E Night Mask', 'Glycolic Acid Peel'
    ]
    
    for i in range(20):
        product_id = gen_uuid()
        product_ids.append(product_id)
        products_data.append({
            'id': product_id,
            'name': product_names[i],
            'brand_id': brand_ids[i % 10],
            'category_id': category_ids[i % 10],
            'description': f'High-quality {product_names[i]} for all skin types',
            'thumbnail': f'/uploads/products/{product_names[i].lower().replace(" ", "-")}.jpg',
            'is_active': True,
            'created_at': now,
            'updated_at': now
        })
    
    if products_data:
        op.bulk_insert(sa.table('products',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('brand_id', sa.String),
            sa.column('category_id', sa.String),
            sa.column('description', sa.String),
            sa.column('thumbnail', sa.String),
            sa.column('is_active', sa.Boolean),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), products_data)
    
    # ===== SEED PRODUCT_TYPES (10 records) =====
    product_types_data = []
    product_type_ids = []
    
    for i in range(10):
        product_type_id = gen_uuid()
        product_type_ids.append(product_type_id)
        product_types_data.append({
            'id': product_type_id,
            'product_id': product_ids[i],
            'type_value_id': type_value_ids[i],
            'image_path': f'/uploads/product_types/product_type_{i+1}.jpg',
            'price': 250000 + (i * 50000),
            'discount_price': 200000 + (i * 40000),
            'status': 'in_stock',
            'quantity': 100 + (i * 10),
            'stock': 100 + (i * 10),
            'volume': size_values[i],
            'ingredients': 'Water, Glycerin, Hyaluronic Acid, Niacinamide',
            'usage': 'Apply to clean skin twice daily',
            'skin_type': 'All skin types',
            'origin': 'Korea',
            'sold': i * 5,
            'created_at': now,
            'updated_at': now
        })
    
    if product_types_data:
        op.bulk_insert(sa.table('product_types',
            sa.column('id', sa.String),
            sa.column('product_id', sa.String),
            sa.column('type_value_id', sa.String),
            sa.column('image_path', sa.String),
            sa.column('price', sa.Float),
            sa.column('discount_price', sa.Float),
            sa.column('status', sa.String),
            sa.column('quantity', sa.Integer),
            sa.column('stock', sa.Integer),
            sa.column('volume', sa.String),
            sa.column('ingredients', sa.String),
            sa.column('usage', sa.String),
            sa.column('skin_type', sa.String),
            sa.column('origin', sa.String),
            sa.column('sold', sa.Integer),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), product_types_data)
    
    # ===== SEED VOUCHERS (10 records) =====
    vouchers_data = []
    voucher_ids = []
    
    for i in range(10):
        voucher_id = gen_uuid()
        voucher_ids.append(voucher_id)
        vouchers_data.append({
            'id': voucher_id,
            'code': f'VOUCHER{i+1:02d}',
            'discount': 10 + (i * 5),  # 10%, 15%, 20%, etc.
            'description': f'Discount voucher {i+1}',
            'quantity': 100,
            'min_order_amount': 100000 + (i * 50000),
            'max_discount': 50000 + (i * 10000),
            'limit': 1,
            'created_at': now,
            'updated_at': now
        })
    
    if vouchers_data:
        op.bulk_insert(sa.table('vouchers',
            sa.column('id', sa.String),
            sa.column('code', sa.String),
            sa.column('discount', sa.Float),
            sa.column('description', sa.String),
            sa.column('quantity', sa.Integer),
            sa.column('min_order_amount', sa.Float),
            sa.column('max_discount', sa.Float),
            sa.column('limit', sa.Integer),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), vouchers_data)
    
    # ===== SEED ADDRESSES (10 records) =====
    addresses_data = []
    address_ids = []
    
    for i in range(10):
        address_id = gen_uuid()
        address_ids.append(address_id)
        addresses_data.append({
            'id': address_id,
            'full_name': f'{users_data[i]["first_name"]} {users_data[i]["last_name"]}',
            'phone_number': users_data[i]['phone_number'],
            'province': 'Ho Chi Minh',
            'district': f'District {i+1}',
            'ward': f'Ward {i+1}',
            'detail': f'{i+1} Nguyen Van Linh Street',
            'is_default': i == 0,
            'user_id': user_ids[i],
            'created_at': now,
            'updated_at': now
        })
    
    if addresses_data:
        op.bulk_insert(sa.table('addresses',
            sa.column('id', sa.String),
            sa.column('full_name', sa.String),
            sa.column('phone_number', sa.String),
            sa.column('province', sa.String),
            sa.column('district', sa.String),
            sa.column('ward', sa.String),
            sa.column('detail', sa.String),
            sa.column('is_default', sa.Boolean),
            sa.column('user_id', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), addresses_data)
    
    # ===== SEED CARTS (10 records) =====
    carts_data = []
    cart_ids = []
    
    for i in range(10):
        cart_id = gen_uuid()
        cart_ids.append(cart_id)
        carts_data.append({
            'id': cart_id,
            'user_id': user_ids[i],
            'created_at': now,
            'updated_at': now
        })
    
    if carts_data:
        op.bulk_insert(sa.table('carts',
            sa.column('id', sa.String),
            sa.column('user_id', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), carts_data)
    
    # ===== SEED CART_ITEMS (10 records) =====
    cart_items_data = []
    
    for i in range(10):
        cart_items_data.append({
            'id': gen_uuid(),
            'cart_id': cart_ids[i],
            'product_type_id': product_type_ids[i],
            'quantity': (i % 5) + 1,
            'created_at': now,
            'updated_at': now
        })
    
    if cart_items_data:
        op.bulk_insert(sa.table('cart_items',
            sa.column('id', sa.String),
            sa.column('cart_id', sa.String),
            sa.column('product_type_id', sa.String),
            sa.column('quantity', sa.Integer),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), cart_items_data)
    
    # ===== SEED WISHLISTS (10 records) =====
    wishlists_data = []
    wishlist_ids = []
    
    for i in range(10):
        wishlist_id = gen_uuid()
        wishlist_ids.append(wishlist_id)
        wishlists_data.append({
            'id': wishlist_id,
            'user_id': user_ids[i],
            'created_at': now,
            'updated_at': now
        })
    
    if wishlists_data:
        op.bulk_insert(sa.table('wishlists',
            sa.column('id', sa.String),
            sa.column('user_id', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), wishlists_data)
    
    # ===== SEED WISHLIST_ITEMS (10 records) =====
    wishlist_items_data = []
    
    for i in range(10):
        wishlist_items_data.append({
            'id': gen_uuid(),
            'wishlist_id': wishlist_ids[i],
            'product_type_id': product_type_ids[i],
            'created_at': now,
            'updated_at': now
        })
    
    if wishlist_items_data:
        op.bulk_insert(sa.table('wishlist_items',
            sa.column('id', sa.String),
            sa.column('wishlist_id', sa.String),
            sa.column('product_type_id', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), wishlist_items_data)
    
    # ===== SEED ORDERS (10 records) =====
    orders_data = []
    order_ids = []
    
    for i in range(10):
        order_id = gen_uuid()
        order_ids.append(order_id)
        orders_data.append({
            'id': order_id,
            'user_id': user_ids[i],
            'address_id': address_ids[i],
            'voucher_id': voucher_ids[i] if i % 3 == 0 else None,
            'status': ['pending', 'processing', 'shipped', 'delivered'][i % 4],
            'payment_method': 'COD' if i % 2 == 0 else 'Online',
            'total_amount': 500000 + (i * 100000),
            'discount_amount': 50000 if i % 3 == 0 else 0,
            'final_amount': (500000 + (i * 100000)) - (50000 if i % 3 == 0 else 0),
            'note': f'Order note {i+1}',
            'created_at': now,
            'updated_at': now
        })
    
    if orders_data:
        op.bulk_insert(sa.table('orders',
            sa.column('id', sa.String),
            sa.column('user_id', sa.String),
            sa.column('address_id', sa.String),
            sa.column('voucher_id', sa.String),
            sa.column('status', sa.String),
            sa.column('payment_method', sa.String),
            sa.column('total_amount', sa.Float),
            sa.column('discount_amount', sa.Float),
            sa.column('final_amount', sa.Float),
            sa.column('note', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), orders_data)
    
    # ===== SEED ORDER_DETAILS (10 records) =====
    order_details_data = []
    
    for i in range(10):
        order_details_data.append({
            'id': gen_uuid(),
            'order_id': order_ids[i],
            'product_type_id': product_type_ids[i],
            'price': product_types_data[i]['price'],
            'number': (i % 3) + 1,
            'created_at': now,
            'updated_at': now
        })
    
    if order_details_data:
        op.bulk_insert(sa.table('order_details',
            sa.column('id', sa.String),
            sa.column('order_id', sa.String),
            sa.column('product_type_id', sa.String),
            sa.column('price', sa.Float),
            sa.column('number', sa.Integer),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), order_details_data)
    
    # ===== SEED PAYMENTS (10 records) =====
    payments_data = []
    
    for i in range(10):
        payments_data.append({
            'id': gen_uuid(),
            'order_id': order_ids[i],
            'method': 'COD' if i % 2 == 0 else 'Online',
            'status': 'paid' if i % 2 == 0 else 'pending',
            'transaction_id': f'TXN{i+1:08d}',
            'amount': orders_data[i]['final_amount'],
            'created_at': now,
            'updated_at': now
        })
    
    if payments_data:
        op.bulk_insert(sa.table('payments',
            sa.column('id', sa.String),
            sa.column('order_id', sa.String),
            sa.column('method', sa.String),
            sa.column('status', sa.String),
            sa.column('transaction_id', sa.String),
            sa.column('amount', sa.Float),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), payments_data)
    
    # ===== SEED REVIEWS (10 records) =====
    reviews_data = []
    review_ids = []
    
    for i in range(10):
        review_id = gen_uuid()
        review_ids.append(review_id)
        reviews_data.append({
            'id': review_id,
            'product_id': product_ids[i],
            'user_id': user_ids[i],
            'order_id': order_ids[i],
            'rating': (i % 5) + 1,
            'comment': f'Great product! Review {i+1}',
            'created_at': now,
            'updated_at': now
        })
    
    if reviews_data:
        op.bulk_insert(sa.table('reviews',
            sa.column('id', sa.String),
            sa.column('product_id', sa.String),
            sa.column('user_id', sa.String),
            sa.column('order_id', sa.String),
            sa.column('rating', sa.Integer),
            sa.column('comment', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), reviews_data)
    
    # ===== SEED REVIEW_MEDIAS (10 records) =====
    review_medias_data = []
    
    for i in range(10):
        review_medias_data.append({
            'id': gen_uuid(),
            'review_id': review_ids[i],
            'path': f'/uploads/reviews/review_{i+1}.jpg',
            'created_at': now,
            'updated_at': now
        })
    
    if review_medias_data:
        op.bulk_insert(sa.table('review_medias',
            sa.column('id', sa.String),
            sa.column('review_id', sa.String),
            sa.column('path', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), review_medias_data)
    
    # ===== SEED CONVERSATIONS (10 records) =====
    conversations_data = []
    conversation_ids = []
    
    for i in range(10):
        conversation_id = gen_uuid()
        conversation_ids.append(conversation_id)
        conversations_data.append({
            'id': conversation_id,
            'customer_id': user_ids[i],
            'admin_id': user_ids[0] if i > 0 else None,  # First user is admin
            'last_message': f'Last message in conversation {i+1}',
            'is_read': i % 2 == 0,
            'created_at': now,
            'updated_at': now
        })
    
    if conversations_data:
        op.bulk_insert(sa.table('conversations',
            sa.column('id', sa.String),
            sa.column('customer_id', sa.String),
            sa.column('admin_id', sa.String),
            sa.column('last_message', sa.String),
            sa.column('is_read', sa.Boolean),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), conversations_data)
    
    # ===== SEED MESSAGES (10 records) =====
    messages_data = []
    
    for i in range(10):
        messages_data.append({
            'id': gen_uuid(),
            'conversation_id': conversation_ids[i],
            'sender_id': user_ids[i],
            'message': f'Message content {i+1}',
            'is_read': i % 2 == 0,
            'created_at': now,
            'updated_at': now
        })
    
    if messages_data:
        op.bulk_insert(sa.table('messages',
            sa.column('id', sa.String),
            sa.column('conversation_id', sa.String),
            sa.column('sender_id', sa.String),
            sa.column('message', sa.String),
            sa.column('is_read', sa.Boolean),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), messages_data)
    
    # ===== SEED NOTIFICATIONS (10 records) =====
    notifications_data = []
    notification_ids = []
    
    for i in range(10):
        notification_id = gen_uuid()
        notification_ids.append(notification_id)
        notifications_data.append({
            'id': notification_id,
            'title': f'Notification {i+1}',
            'content': f'Notification content {i+1}',
            'type': ['order', 'promotion', 'system'][i % 3],
            'sender_id': user_ids[0],
            'order_id': order_ids[i] if i % 3 == 0 else None,
            'is_global': i % 2 == 0,
            'created_at': now,
            'updated_at': now
        })
    
    if notifications_data:
        op.bulk_insert(sa.table('notifications',
            sa.column('id', sa.String),
            sa.column('title', sa.String),
            sa.column('content', sa.String),
            sa.column('type', sa.String),
            sa.column('sender_id', sa.String),
            sa.column('order_id', sa.String),
            sa.column('is_global', sa.Boolean),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), notifications_data)
    
    # ===== SEED USER_NOTIFICATIONS (10 records) =====
    user_notifications_data = []
    
    for i in range(10):
        user_notifications_data.append({
            'id': gen_uuid(),
            'user_id': user_ids[i],
            'notification_id': notification_ids[i],
            'is_read': i % 2 == 0,
            'read_at': now if i % 2 == 0 else None,
            'created_at': now,
            'updated_at': now
        })
    
    if user_notifications_data:
        op.bulk_insert(sa.table('user_notifications',
            sa.column('id', sa.String),
            sa.column('user_id', sa.String),
            sa.column('notification_id', sa.String),
            sa.column('is_read', sa.Boolean),
            sa.column('read_at', sa.DateTime),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), user_notifications_data)
    
    # ===== SEED ORDER_VOUCHERS (10 records) =====
    order_vouchers_data = []
    
    for i in range(10):
        if i % 3 == 0:  # Only for orders that have vouchers
            order_vouchers_data.append({
                'id': gen_uuid(),
                'order_id': order_ids[i],
                'voucher_id': voucher_ids[i],
                'created_at': now,
                'updated_at': now
            })
    
    if order_vouchers_data:
        op.bulk_insert(sa.table('order_vouchers',
            sa.column('id', sa.String),
            sa.column('order_id', sa.String),
            sa.column('voucher_id', sa.String),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ), order_vouchers_data)


def downgrade() -> None:
    # Delete all seeded data in reverse order
    conn = op.get_bind()
    
    conn.execute(sa.text("DELETE FROM order_vouchers"))
    conn.execute(sa.text("DELETE FROM user_notifications"))
    conn.execute(sa.text("DELETE FROM review_medias"))
    conn.execute(sa.text("DELETE FROM notifications"))
    conn.execute(sa.text("DELETE FROM messages"))
    conn.execute(sa.text("DELETE FROM conversations"))
    conn.execute(sa.text("DELETE FROM reviews"))
    conn.execute(sa.text("DELETE FROM payments"))
    conn.execute(sa.text("DELETE FROM order_details"))
    conn.execute(sa.text("DELETE FROM orders"))
    conn.execute(sa.text("DELETE FROM wishlist_items"))
    conn.execute(sa.text("DELETE FROM wishlists"))
    conn.execute(sa.text("DELETE FROM cart_items"))
    conn.execute(sa.text("DELETE FROM carts"))
    conn.execute(sa.text("DELETE FROM addresses"))
    conn.execute(sa.text("DELETE FROM vouchers"))
    conn.execute(sa.text("DELETE FROM product_types"))
    conn.execute(sa.text("DELETE FROM products"))
    conn.execute(sa.text("DELETE FROM user_roles"))
    conn.execute(sa.text("DELETE FROM type_values"))
    conn.execute(sa.text("DELETE FROM types"))
    conn.execute(sa.text("DELETE FROM categories"))
    conn.execute(sa.text("DELETE FROM brands"))
    conn.execute(sa.text("DELETE FROM users"))
    conn.execute(sa.text("DELETE FROM roles"))
