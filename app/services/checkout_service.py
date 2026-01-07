from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid

from app.models.order import Order
from app.models.payment import Payment
from app.models.productType import ProductType
from app.models.voucher import Voucher
from app.models.cartItem import CartItem
from app.models.address import Address
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.request.checkout import CheckoutItemRequest

# Thời gian timeout thanh toán SEPAY (phút)
PAYMENT_TIMEOUT_MINUTES = 15


class CheckoutService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.payment_repo = PaymentRepository(db)

    def validate_voucher(self, code: str, subtotal: float) -> Tuple[bool, float, str]:
        """
        Validate mã voucher
        Returns: (valid, discount_amount, message)
        """
        voucher = self.db.query(Voucher).filter(
            Voucher.code == code,
            Voucher.deleted_at.is_(None)
        ).first()

        if not voucher:
            return False, 0, "Mã voucher không tồn tại."

        if voucher.quantity <= 0:
            return False, 0, "Mã voucher đã hết lượt sử dụng."

        if voucher.min_order_amount and subtotal < voucher.min_order_amount:
            return False, 0, f"Đơn hàng tối thiểu {voucher.min_order_amount:,.0f}₫ để sử dụng mã này."


        # Tính discount_amount từ phần trăm (10 = 10%)
        discount_amount = subtotal * (voucher.discount / 100)
        
        # Áp dụng giới hạn max_discount nếu có
        if voucher.max_discount and discount_amount > voucher.max_discount:
            discount_amount = voucher.max_discount

        # Không giảm quá subtotal
        if discount_amount > subtotal:
            discount_amount = subtotal

        return True, discount_amount, f"Áp dụng mã {code} thành công!"



    def preview_order(
        self,
        items: List[CheckoutItemRequest],
        voucher_code: Optional[str] = None,
        address_id: Optional[str] = None
    ) -> dict:
        """Xem trước đơn hàng trước khi checkout"""
        checkout_items = []
        subtotal = 0

        for item in items:
            pt = self.db.query(ProductType).filter(
                ProductType.id == item.product_type_id,
                ProductType.deleted_at.is_(None)
            ).first()

            if not pt:
                raise Exception(f"Sản phẩm không tồn tại: {item.product_type_id}")

            if pt.stock is not None and pt.stock < item.quantity:
                raise Exception(f"Sản phẩm {pt.product.name} chỉ còn {pt.stock} trong kho.")

            price = pt.price or 0
            discount_price = pt.discount_price
            line_total = (discount_price or price) * item.quantity
            subtotal += line_total

            checkout_items.append({
                "cart_item_id": item.cart_item_id,
                "product_type_id": pt.id,
                "product_name": pt.product.name if pt.product else "Sản phẩm",
                "variant_name": pt.type_value.name if pt.type_value else pt.volume,
                "image": pt.image_path or (pt.product.thumbnail if pt.product else None),
                "quantity": item.quantity,
                "price": price,
                "discount_price": discount_price,
                "line_total": line_total
            })

        # Validate voucher nếu có
        discount = 0
        voucher_info = None
        if voucher_code:
            valid, discount_amount, message = self.validate_voucher(voucher_code, subtotal)
            if valid:
                discount = discount_amount
                voucher = self.db.query(Voucher).filter(Voucher.code == voucher_code).first()
                voucher_info = {
                    "code": voucher_code,
                    "discount_amount": discount_amount,
                    "description": voucher.description if voucher else None
                }

        shipping_fee = 0  # Miễn phí vận chuyển
        total = subtotal - discount + shipping_fee

        return {
            "items": checkout_items,
            "subtotal": subtotal,
            "discount": discount,
            "shipping_fee": shipping_fee,
            "total": total,
            "voucher": voucher_info,
            "address_id": address_id
        }

    def create_order(
        self,
        user_id: str,
        items: List[CheckoutItemRequest],
        address_id: str,
        payment_method: str,
        voucher_code: Optional[str] = None,
        note: Optional[str] = None
    ) -> Order:
        """Tạo đơn hàng mới"""
        # Validate address
        address = self.db.query(Address).filter(
            Address.id == address_id,
            Address.user_id == user_id,
            Address.deleted_at.is_(None)
        ).first()
        if not address:
            raise Exception("Địa chỉ giao hàng không hợp lệ.")

        # Tính toán preview
        preview = self.preview_order(items, voucher_code)

        # Lấy voucher_id nếu có
        voucher_id = None
        if voucher_code:
            voucher = self.db.query(Voucher).filter(
                Voucher.code == voucher_code,
                Voucher.deleted_at.is_(None)
            ).first()
            if voucher:
                voucher_id = voucher.id
                # Trừ số lượng voucher
                voucher.quantity -= 1

        # Tạo order data
        order_id = str(uuid.uuid4())
        order_data = {
            "id": order_id,
            "user_id": user_id,
            "address_id": address_id,
            "voucher_id": voucher_id,
            "status": "pending",
            "payment_method": payment_method.upper(),
            "total_amount": preview["subtotal"],
            "discount_amount": preview["discount"],
            "final_amount": preview["total"],
            "note": note
        }
        
        # Tạo order details data + trừ stock
        order_details = []
        for item_data in preview["items"]:
            pt = self.db.query(ProductType).filter(
                ProductType.id == item_data["product_type_id"]
            ).first()
            
            # Trừ stock
            if pt.stock is not None:
                pt.stock -= item_data["quantity"]

            order_details.append({
                "id": str(uuid.uuid4()),
                "product_type_id": item_data["product_type_id"],
                "price": item_data["discount_price"] or item_data["price"],
                "number": item_data["quantity"]
            })

        # Sử dụng repository để tạo order
        order = self.order_repo.create_order(order_data, order_details)

        # Tạo payment record
        payment_data = {
            "id": str(uuid.uuid4()),
            "order_id": order.id,
            "method": payment_method.upper(),
            "status": "pending" if payment_method.upper() == "SEPAY" else "cod_pending",
            "amount": preview["total"]
        }
        self.payment_repo.create_payment(payment_data)

        # Xóa cart items đã đặt
        cart_item_ids = [item.cart_item_id for item in items]
        self.db.query(CartItem).filter(CartItem.id.in_(cart_item_ids)).delete(synchronize_session=False)

        self.db.commit()
        self.db.refresh(order)

        return order

    def get_order_payment_status(self, order_id: str) -> dict:
        """Lấy trạng thái thanh toán của đơn hàng"""
        order = self.order_repo.get(order_id)
        if not order:
            return None

        payment = self.payment_repo.get_active_by_order_id(order_id)

        return {
            "order_id": order.id,
            "order_status": order.status,
            "payment_status": payment.status if payment else None,
            "transaction_id": payment.transaction_id if payment else None
        }

    def update_payment_status(self, order_id: str, status: str, transaction_id: str = None) -> bool:
        """
        Cập nhật trạng thái thanh toán
        
        Flow:
        - SePay: pending → success → order.status = 'confirmed'
        - SePay: pending → cancelled (timeout) → order.status = 'cancelled'
        - COD: cod_pending → success (khi giao + thu tiền thành công)
        """
        payment = self.payment_repo.get_pending_by_order_id(order_id)
        order = self.order_repo.get(order_id)

        if not payment or not order:
            return False

        payment.status = status
        if transaction_id:
            payment.transaction_id = transaction_id

        # Cập nhật order status theo flow
        if status == "success":
            if order.payment_method == "SEPAY" and order.status == "pending":
                order.status = "confirmed"
        elif status == "cancelled":
            order.status = "cancelled"
            self._restore_stock(order)

        self.db.commit()
        return True

    def cancel_order(self, order_id: str, user_id: str) -> dict:
        """
        Hủy đơn hàng - Chỉ cho phép với đơn COD chưa được admin xác nhận
        """
        order = self.order_repo.get_by_id_and_user(order_id, user_id)

        if not order:
            return {"success": False, "message": "Không tìm thấy đơn hàng."}

        if order.payment_method not in ["COD", "SEPAY"]:
            return {"success": False, "message": "Phương thức thanh toán này không hỗ trợ hủy tự động."}

        if order.status != "pending":
            return {"success": False, "message": "Không thể hủy đơn hàng đã được xác nhận hoặc đang xử lý."}

        # Cập nhật trạng thái
        order.status = "cancelled"
        
        payment = self.payment_repo.get_pending_by_order_id(order_id)
        if payment:
            payment.status = "cancelled"

        # Hoàn lại stock
        self._restore_stock(order)

        self.db.commit()
        return {"success": True, "message": "Đã hủy đơn hàng thành công."}

    def change_payment_method(self, order_id: str, user_id: str, new_method: str) -> dict:
        """
        Đổi phương thức thanh toán - Tạo Payment mới, đánh dấu cũ là failed
        """
        order = self.order_repo.get_by_id_and_user(order_id, user_id)

        if not order:
            return {"success": False, "message": "Không tìm thấy đơn hàng."}

        if order.status != "pending":
            return {"success": False, "message": "Không thể đổi phương thức thanh toán cho đơn hàng này."}

        new_method = new_method.upper()
        if new_method not in ["COD", "SEPAY"]:
            return {"success": False, "message": "Phương thức thanh toán không hợp lệ."}

        if order.payment_method == new_method:
            return {"success": False, "message": "Đơn hàng đã sử dụng phương thức này."}

        # Đánh dấu payment cũ là failed
        old_payment = self.payment_repo.get_pending_by_order_id(order_id)
        if old_payment:
            old_payment.status = "failed"

        # Tạo payment mới
        new_payment_data = {
            "id": str(uuid.uuid4()),
            "order_id": order.id,
            "method": new_method,
            "status": "pending" if new_method == "SEPAY" else "cod_pending",
            "amount": order.final_amount
        }
        new_payment = self.payment_repo.create_payment(new_payment_data)

        # Cập nhật order
        order.payment_method = new_method

        self.db.commit()

        return {
            "success": True,
            "message": f"Đã đổi sang thanh toán {'khi nhận hàng' if new_method == 'COD' else 'chuyển khoản'}.",
            "payment_id": new_payment.id
        }

    def is_payment_expired(self, order: Order) -> bool:
        """Kiểm tra xem đơn hàng SEPAY đã hết thời gian thanh toán chưa"""
        if order.status != "pending" or order.payment_method != "SEPAY":
            return False
        
        if not order.created_at:
            return False
        
        # Đảm bảo created_at có timezone, nếu không thì gán UTC
        created_at = order.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        expire_time = created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
        now = datetime.now(timezone.utc)
        return now > expire_time

    def get_payment_remaining_time(self, order: Order) -> int:
        """Lấy thời gian còn lại để thanh toán (giây)"""
        if order.status != "pending" or order.payment_method != "SEPAY":
            return 0
        
        if not order.created_at:
            return 0
        
        # Đảm bảo created_at có timezone, nếu không thì gán UTC
        created_at = order.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        expire_time = created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
        now = datetime.now(timezone.utc)
        remaining = (expire_time - now).total_seconds()
        return max(0, int(remaining))

    def expire_pending_payments(self) -> int:
        """Hủy các đơn hàng SEPAY đã quá thời gian thanh toán"""
        expired_orders = self.order_repo.get_pending_sepay_expired(PAYMENT_TIMEOUT_MINUTES)
        
        count = 0
        for order in expired_orders:
            order.status = "cancelled"
            
            payment = self.payment_repo.get_pending_by_order_id(order.id)
            if payment:
                payment.status = "cancelled"
            
            self._restore_stock(order)
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count

    def _restore_stock(self, order: Order):
        """Helper: Hoàn lại stock khi hủy đơn"""
        for detail in order.details:
            pt = self.db.query(ProductType).filter(ProductType.id == detail.product_type_id).first()
            if pt and pt.stock is not None:
                pt.stock += detail.number
