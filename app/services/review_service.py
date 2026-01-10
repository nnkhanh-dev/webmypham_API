from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from app.repositories.review_repository import ReviewRepository
from app.schemas.request.review import ReviewCreate, ReviewUpdate
from app.models.order import Order
from app.models.orderDetail import OrderDetail
from app.models.review import Review

class ReviewService:
    def __init__(self, db: Session):
        self.repo = ReviewRepository(db)
        self.db = db

    def create(self, review_in: ReviewCreate, user_id: str):
        """
        Tạo review mới với validation:
        - Order phải tồn tại và thuộc về user
        - Order phải ở trạng thái delivered/completed
        - Sản phẩm phải có trong order
        - Chưa review lần nào
        """
        print(f"🔍 Creating review for user {user_id}")
        print(f"📦 Review data: {review_in.dict()}")
        
        # 1. Kiểm tra order
        order = self.db.query(Order).filter(
            Order.id == review_in.order_id,
            Order.user_id == user_id,
            Order.deleted_at.is_(None)
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đơn hàng không tồn tại hoặc không thuộc về bạn"
            )
        
        print(f"✅ Order found: {order.id} - Status: {order.status}")
        
        # 2. Kiểm tra trạng thái order
        if order.status not in ['delivered', 'completed']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chỉ có thể đánh giá khi đơn hàng đã hoàn thành. Trạng thái hiện tại: {order.status}"
            )
        
        # 3. Kiểm tra sản phẩm trong order
        order_detail = self.db.query(OrderDetail).filter(
            OrderDetail.order_id == review_in.order_id,
            OrderDetail.product_type_id == review_in.product_id,  # product_id ở đây thực ra là product_type_id
            OrderDetail.deleted_at.is_(None)
        ).first()
        
        if not order_detail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sản phẩm này không có trong đơn hàng"
            )
        
        print(f"✅ Product found in order")
        
        # Lấy product_id thực sự từ product_type
        from app.models.productType import ProductType
        product_type = self.db.query(ProductType).filter(
            ProductType.id == review_in.product_id
        ).first()
        
        if not product_type or not product_type.product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy thông tin sản phẩm"
            )
        
        actual_product_id = product_type.product_id
        print(f"✅ Actual product_id: {actual_product_id}")
        
        # 4. Kiểm tra đã review chưa (theo product_id thực, không phải product_type_id)
        existing_review = self.db.query(Review).filter(
            Review.order_id == review_in.order_id,
            Review.product_id == actual_product_id,
            Review.user_id == user_id,
            Review.deleted_at.is_(None)
        ).first()
        
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bạn đã đánh giá sản phẩm này trong đơn hàng này rồi"
            )
        
        # 5. Tạo review - Dùng product_id thực
        review = Review(
            id=str(uuid.uuid4()),
            product_id=actual_product_id,  # Dùng product_id thực từ product_type
            user_id=user_id,
            order_id=review_in.order_id,
            rating=review_in.rating,
            comment=review_in.comment,
            created_by=user_id
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        
        print(f"✅ Review created: {review.id}")
        
        # Convert datetime to string for response
        from app.schemas.response.review import ReviewResponse
        return ReviewResponse(
            id=str(review.id),
            product_id=str(review.product_id),
            user_id=str(review.user_id),
            order_id=str(review.order_id) if review.order_id else None,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat() if review.created_at else None,
            updated_at=review.updated_at.isoformat() if review.updated_at else None
        )

    def get(self, review_id: str):
        return self.repo.get(review_id)

    def update(self, review_id: str, review_in: ReviewUpdate, user_id: str):
        """Chỉ cho phép user tự sửa review của mình"""
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id,
            Review.deleted_at.is_(None)
        ).first()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đánh giá không tồn tại hoặc bạn không có quyền sửa"
            )
        
        update_data = review_in.dict(exclude_unset=True)
        update_data['updated_by'] = user_id
        
        return self.repo.update(review_id, update_data)

    def delete(self, review_id: str, user_id: str):
        """Chỉ cho phép user tự xóa review của mình"""
        review = self.db.query(Review).filter(
            Review.id == review_id,
            Review.user_id == user_id,
            Review.deleted_at.is_(None)
        ).first()
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Đánh giá không tồn tại hoặc bạn không có quyền xóa"
            )
        
        return self.repo.delete(review_id)

    def get_by_product(self, product_id: str):
        """Lấy tất cả review của sản phẩm, kèm thông tin user"""
        reviews = self.repo.get_by_product(product_id)
        
        from app.schemas.response.review import ReviewResponse
        result = []
        
        for review in reviews:
            user_name = None
            if review.user:
                user_name = f"{review.user.first_name} {review.user.last_name}".strip()
                if not user_name:
                    user_name = review.user.email or "Người dùng"
            
            result.append(ReviewResponse(
                id=str(review.id),
                product_id=str(review.product_id),
                user_id=str(review.user_id),
                order_id=str(review.order_id) if review.order_id else None,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at.isoformat() if review.created_at else None,
                updated_at=review.updated_at.isoformat() if review.updated_at else None,
                user_name=user_name
            ))
        
        return result
    
    def get_reviewable_products(self, user_id: str):
        """Lấy danh sách sản phẩm có thể đánh giá"""
        print(f"🔍 Getting reviewable products for user: {user_id}")
        
        # Lấy đơn hàng đã hoàn thành (delivered hoặc completed)
        delivered_orders = self.db.query(Order).filter(
            Order.user_id == user_id,
            Order.status.in_(['delivered', 'completed']),  # Chấp nhận cả 2 status
            Order.deleted_at.is_(None)
        ).all()
        
        print(f"📦 Found {len(delivered_orders)} completed orders")
        
        reviewable_products = []
        
        for order in delivered_orders:
            print(f"  📋 Order {order.id} - Status: {order.status}")
            
            order_details = self.db.query(OrderDetail).filter(
                OrderDetail.order_id == order.id,
                OrderDetail.deleted_at.is_(None)
            ).all()
            
            print(f"    📦 Order has {len(order_details)} items")
            
            for detail in order_details:
                # Kiểm tra đã review chưa
                existing_review = self.db.query(Review).filter(
                    Review.order_id == order.id,
                    Review.product_id == detail.product_type_id,
                    Review.user_id == user_id,
                    Review.deleted_at.is_(None)
                ).first()
                
                if existing_review:
                    print(f"      ⏭️  Product {detail.product_type_id} already reviewed")
                    continue
                
                from app.models.productType import ProductType
                product_type = self.db.query(ProductType).filter(
                    ProductType.id == detail.product_type_id
                ).first()
                
                if product_type and product_type.product:
                    print(f"      ✅ Product {product_type.product.name} can be reviewed")
                    reviewable_products.append({
                        "order_id": order.id,
                        "product_type_id": detail.product_type_id,
                        "product_id": product_type.product_id,
                        "product_name": product_type.product.name,
                        "product_thumbnail": product_type.product.thumbnail,
                        "variant_name": product_type.volume or (product_type.type_value.name if product_type.type_value else "Mặc định"),
                        "order_date": order.created_at.isoformat() if order.created_at else None,
                        "price": detail.price,
                        "quantity": detail.number  # OrderDetail uses 'number' not 'quantity'
                    })
                else:
                    print(f"      ❌ Product type {detail.product_type_id} not found or has no product")
        
        print(f"✅ Total reviewable products: {len(reviewable_products)}")
        return reviewable_products
