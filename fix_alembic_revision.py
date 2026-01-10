"""
Fix Alembic revision mismatch
This script helps sync database revision with migration files after git pull/merge
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_revision():
    """Update alembic_version table to v13 (current head before ver14)"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check current revision
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current = result.fetchone()
        
        print(f"Current revision in DB: {current[0] if current else 'None'}")
        print("Expected revision: v13")
        print("\nThis will update alembic_version table to v13")
        print("After this, you can run: alembic upgrade head")
        
        response = input("\nContinue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Aborted.")
            return
        
        # Update to v13
        conn.execute(text("UPDATE alembic_version SET version_num = 'v13'"))
        conn.commit()
        
        print("✅ Updated to v13")
        print("\nNext step: alembic upgrade head")

if __name__ == "__main__":
    fix_revision()
