import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.voucher import Voucher

def check_vouchers():
    try:
        db = SessionLocal()
        vouchers = db.query(Voucher).all()
        print(f"--- DATABASE VOUCHER CHECK ---")
        print(f"Total vouchers found: {len(vouchers)}")
        for v in vouchers:
            print(f"ID: {v.id}, Code: {v.code}, Qty: {v.quantity}, MinOrder: {v.min_order_amount}, DeletedAt: {v.deleted_at}")
        
        if len(vouchers) == 0:
            print("WARNING: No vouchers found in database 'vouchers' table.")
            
        print("------------------------------")
    except Exception as e:
        print(f"Error checking DB: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    check_vouchers()
