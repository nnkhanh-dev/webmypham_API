from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.schemas.request.order import OrderCreate
from app.models.order import Order
from app.models.orderDetail import OrderDetail
from app.models.productType import ProductType
from app.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRepository(db)

    def get_user_orders(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        sort_order: str = "desc"
    ) -> Tuple[List[Order], int]:
        """Lấy lịch sử đơn hàng của user"""
        return self.repo.get_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status,
            sort_order=sort_order
        )

    def get_order_detail(self, order_id: str, user_id: Optional[str] = None) -> Optional[Order]:
        """Lấy chi tiết đơn hàng. Nếu có user_id thì kiểm tra quyền sở hữu."""
        if user_id:
            return self.repo.get_user_order_detail(order_id, user_id)
        return self.repo.get_detail(order_id)

    def create_order(self, order_in: OrderCreate):
        # Tính tổng tiền, giảm giá, ... và lưu
        # --- Begin core order logic ---
        product_types = {
            pt.id: pt
            for pt in self.db.query(ProductType).filter(
                ProductType.id.in_([item.product_type_id for item in order_in.items])
            )
        }
        total = 0
        details = []
        for item in order_in.items:
            pt = product_types.get(item.product_type_id)
            if not pt or pt.stock < item.quantity:
                raise Exception("Sản phẩm không đủ hàng")
            line_total = (pt.discount_price or pt.price) * item.quantity
            total += line_total
            details.append({"product_type_id": pt.id, "quantity": item.quantity, "price": pt.price})
            # có thể trừ kho luôn ở đây nếu muốn

        # Gắn logic giảm giá/voucher nếu cần ở đây
        discount = 0
        final = total - discount

        order = Order(
            user_id=order_in.user_id,
            status="pending",
            total_amount=total,
            discount_amount=discount,
            final_amount=final,
            # add trường khác nếu cần
        )
        self.db.add(order)
        self.db.flush()  # để lấy order.id

        for detail in details:
            od = OrderDetail(
                order_id=order.id,
                product_type_id=detail["product_type_id"],
                quantity=detail["quantity"],
                price=detail["price"],
            )
            self.db.add(od)
        self.db.commit()
        self.db.refresh(order)
        # => Sau này gọi payment gateway (VNPay/Momo) thì handle ở đây, chưa cần luôn xử lí ở code này

        # Nên trả về order (kèm list detail)
        return order