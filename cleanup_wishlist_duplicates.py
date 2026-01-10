"""
Cleanup duplicate wishlist data before running migration ver14
This script soft-deletes duplicate wishlists and wishlist items, keeping only the oldest ones.

Run this ONLY if check_wishlist_duplicates.py reports duplicates.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


def cleanup_duplicate_wishlists(session):
    """Soft delete duplicate wishlists, keeping the oldest one for each user"""
    print("\n=== Cleaning up duplicate wishlists ===")
    
    # Find duplicates
    query = text("""
        SELECT user_id, COUNT(*) as count
        FROM wishlists
        WHERE deleted_at IS NULL
        GROUP BY user_id
        HAVING COUNT(*) > 1
    """)
    
    result = session.execute(query)
    users_with_duplicates = [row.user_id for row in result.fetchall()]
    
    if not users_with_duplicates:
        print("✅ No duplicate wishlists to clean up")
        return 0
    
    cleaned_count = 0
    now = datetime.utcnow()
    
    for user_id in users_with_duplicates:
        # Get all wishlists for this user, ordered by creation date
        query = text("""
            SELECT id, created_at
            FROM wishlists
            WHERE user_id = :user_id AND deleted_at IS NULL
            ORDER BY created_at ASC
        """)
        
        result = session.execute(query, {"user_id": user_id})
        wishlists = result.fetchall()
        
        # Keep the first (oldest), soft delete the rest
        keep_id = wishlists[0].id
        delete_ids = [w.id for w in wishlists[1:]]
        
        print(f"User {user_id}:")
        print(f"  Keeping wishlist: {keep_id} (created: {wishlists[0].created_at})")
        print(f"  Deleting {len(delete_ids)} duplicate(s): {delete_ids}")
        
        # Soft delete duplicates
        for delete_id in delete_ids:
            update_query = text("""
                UPDATE wishlists
                SET deleted_at = :deleted_at, deleted_by = 'system_cleanup'
                WHERE id = :id
            """)
            session.execute(update_query, {"deleted_at": now, "id": delete_id})
            cleaned_count += 1
    
    session.commit()
    print(f"\n✅ Cleaned up {cleaned_count} duplicate wishlist(s)")
    return cleaned_count


def cleanup_duplicate_wishlist_items(session):
    """Soft delete duplicate wishlist items, keeping the oldest one"""
    print("\n=== Cleaning up duplicate wishlist items ===")
    
    # Find duplicates
    query = text("""
        SELECT wishlist_id, product_type_id, COUNT(*) as count
        FROM wishlist_items
        WHERE deleted_at IS NULL
        GROUP BY wishlist_id, product_type_id
        HAVING COUNT(*) > 1
    """)
    
    result = session.execute(query)
    duplicates = [(row.wishlist_id, row.product_type_id) for row in result.fetchall()]
    
    if not duplicates:
        print("✅ No duplicate wishlist items to clean up")
        return 0
    
    cleaned_count = 0
    now = datetime.utcnow()
    
    for wishlist_id, product_type_id in duplicates:
        # Get all items, ordered by creation date
        query = text("""
            SELECT id, created_at
            FROM wishlist_items
            WHERE wishlist_id = :wishlist_id 
                AND product_type_id = :product_type_id
                AND deleted_at IS NULL
            ORDER BY created_at ASC
        """)
        
        result = session.execute(query, {
            "wishlist_id": wishlist_id,
            "product_type_id": product_type_id
        })
        items = result.fetchall()
        
        # Keep the first (oldest), soft delete the rest
        keep_id = items[0].id
        delete_ids = [i.id for i in items[1:]]
        
        print(f"Wishlist {wishlist_id}, Product {product_type_id}:")
        print(f"  Keeping item: {keep_id} (created: {items[0].created_at})")
        print(f"  Deleting {len(delete_ids)} duplicate(s): {delete_ids}")
        
        # Soft delete duplicates
        for delete_id in delete_ids:
            update_query = text("""
                UPDATE wishlist_items
                SET deleted_at = :deleted_at, deleted_by = 'system_cleanup'
                WHERE id = :id
            """)
            session.execute(update_query, {"deleted_at": now, "id": delete_id})
            cleaned_count += 1
    
    session.commit()
    print(f"\n✅ Cleaned up {cleaned_count} duplicate item(s)")
    return cleaned_count


def main():
    """Main function to run cleanup"""
    print("=" * 60)
    print("Wishlist Duplicate Cleanup")
    print("=" * 60)
    print("\n⚠️  WARNING: This will soft-delete duplicate data!")
    print("Make sure you have a database backup before proceeding.\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Aborted.")
        return 0
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Run cleanup
        wishlist_count = cleanup_duplicate_wishlists(session)
        item_count = cleanup_duplicate_wishlist_items(session)
        
        # Summary
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Wishlists cleaned: {wishlist_count}")
        print(f"Items cleaned: {item_count}")
        print("\n✅ Cleanup complete!")
        print("\nNext step: python check_wishlist_duplicates.py (verify)")
        return 0
            
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during cleanup: {str(e)}")
        print("Transaction rolled back. No changes were made.")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
