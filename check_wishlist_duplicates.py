"""
Check for duplicate wishlist data before running migration ver14
This script identifies any duplicate wishlists or wishlist items that would violate
the new unique constraints.

Run this before executing: alembic upgrade head
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


def check_duplicate_wishlists(session):
    """Check for users with multiple wishlists"""
    print("\n=== Checking for duplicate wishlists per user ===")
    
    query = text("""
        SELECT user_id, COUNT(*) as count
        FROM wishlists
        WHERE deleted_at IS NULL
        GROUP BY user_id
        HAVING COUNT(*) > 1
    """)
    
    result = session.execute(query)
    duplicates = result.fetchall()
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} users with multiple wishlists:")
        for row in duplicates:
            print(f"   User ID: {row.user_id}, Count: {row.count}")
        return False
    else:
        print("✅ No duplicate wishlists found")
        return True


def check_duplicate_wishlist_items(session):
    """Check for duplicate products in wishlists"""
    print("\n=== Checking for duplicate items in wishlists ===")
    
    query = text("""
        SELECT wishlist_id, product_type_id, COUNT(*) as count
        FROM wishlist_items
        WHERE deleted_at IS NULL
        GROUP BY wishlist_id, product_type_id
        HAVING COUNT(*) > 1
    """)
    
    result = session.execute(query)
    duplicates = result.fetchall()
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate items:")
        for row in duplicates:
            print(f"   Wishlist: {row.wishlist_id}, Product: {row.product_type_id}, Count: {row.count}")
        return False
    else:
        print("✅ No duplicate wishlist items found")
        return True


def check_null_values(session):
    """Check for NULL foreign keys"""
    print("\n=== Checking for NULL foreign keys ===")
    
    issues = []
    
    # Check wishlists.user_id
    query = text("SELECT COUNT(*) FROM wishlists WHERE user_id IS NULL")
    null_user_ids = session.execute(query).scalar()
    if null_user_ids > 0:
        print(f"❌ Found {null_user_ids} wishlists with NULL user_id")
        issues.append(f"wishlists.user_id: {null_user_ids} NULLs")
    else:
        print("✅ No NULL user_id in wishlists")
    
    # Check wishlist_items.wishlist_id
    query = text("SELECT COUNT(*) FROM wishlist_items WHERE wishlist_id IS NULL")
    null_wishlist_ids = session.execute(query).scalar()
    if null_wishlist_ids > 0:
        print(f"❌ Found {null_wishlist_ids} items with NULL wishlist_id")
        issues.append(f"wishlist_items.wishlist_id: {null_wishlist_ids} NULLs")
    else:
        print("✅ No NULL wishlist_id in wishlist_items")
    
    # Check wishlist_items.product_type_id
    query = text("SELECT COUNT(*) FROM wishlist_items WHERE product_type_id IS NULL")
    null_product_ids = session.execute(query).scalar()
    if null_product_ids > 0:
        print(f"❌ Found {null_product_ids} items with NULL product_type_id")
        issues.append(f"wishlist_items.product_type_id: {null_product_ids} NULLs")
    else:
        print("✅ No NULL product_type_id in wishlist_items")
    
    return len(issues) == 0, issues


def main():
    """Main function to run all checks"""
    print("=" * 60)
    print("Wishlist Database Integrity Check")
    print("=" * 60)
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Run all checks
        no_dup_wishlists = check_duplicate_wishlists(session)
        no_dup_items = check_duplicate_wishlist_items(session)
        no_nulls, null_issues = check_null_values(session)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if no_dup_wishlists and no_dup_items and no_nulls:
            print("✅ All checks passed! Safe to run migration.")
            print("\nNext step: alembic upgrade head")
            return 0
        else:
            print("❌ Issues found! Please fix before running migration.")
            if not no_dup_wishlists or not no_dup_items:
                print("\nRun cleanup script: python cleanup_wishlist_duplicates.py")
            if not no_nulls:
                print("\nNULL value issues:")
                for issue in null_issues:
                    print(f"  - {issue}")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during check: {str(e)}")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
