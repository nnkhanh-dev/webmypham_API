"""
Seed data script for authentication tables (User, Role, UserRole)
This script creates sample data for testing login functionality
"""
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Import models and database setup
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.role import Role
from app.models.userRole import UserRole

# Password hashing context
# Use argon2 to match the application's auth_service.py configuration
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def clear_existing_data(db: Session):
    """Clear existing data from tables"""
    print("🗑️  Clearing existing data...")
    try:
        # Delete in correct order to avoid foreign key constraints
        db.query(UserRole).delete()
        db.query(User).delete()
        db.query(Role).delete()
        db.commit()
        print("✅ Existing data cleared successfully")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing data: {e}")
        raise


def create_roles(db: Session):
    """Create sample roles"""
    print("\n📝 Creating roles...")
    
    roles_data = [
        {
            "name": "admin",
            "description": "Administrator with full system access"
        },
        {
            "name": "customer",
            "description": "Regular customer who can browse and purchase products"
        },
        {
            "name": "staff",
            "description": "Staff member who can manage products and orders"
        },
        {
            "name": "manager",
            "description": "Manager with elevated permissions"
        }
    ]
    
    roles = []
    for role_data in roles_data:
        role = Role(
            name=role_data["name"],
            description=role_data["description"]
        )
        db.add(role)
        roles.append(role)
        print(f"   ✓ Created role: {role_data['name']}")
    
    db.commit()
    print("✅ Roles created successfully")
    return roles


def create_users(db: Session):
    """Create sample users"""
    print("\n👥 Creating users...")
    
    users_data = [
        {
            "email": "admin@webmypham.com",
            "password": "Admin@123",
            "phone_number": "0901234567",
            "first_name": "Admin",
            "last_name": "System",
            "dob": datetime(1990, 1, 1)
        },
        {
            "email": "customer1@gmail.com",
            "password": "Customer@123",
            "phone_number": "0912345678",
            "first_name": "Nguyễn",
            "last_name": "Văn A",
            "dob": datetime(1995, 5, 15)
        },
        {
            "email": "customer2@gmail.com",
            "password": "Customer@123",
            "phone_number": "0923456789",
            "first_name": "Trần",
            "last_name": "Thị B",
            "dob": datetime(1998, 8, 20)
        },
        {
            "email": "staff@webmypham.com",
            "password": "Staff@123",
            "phone_number": "0934567890",
            "first_name": "Lê",
            "last_name": "Văn C",
            "dob": datetime(1992, 3, 10)
        },
        {
            "email": "manager@webmypham.com",
            "password": "Manager@123",
            "phone_number": "0945678901",
            "first_name": "Phạm",
            "last_name": "Thị D",
            "dob": datetime(1988, 11, 25)
        }
    ]
    
    users = []
    for user_data in users_data:
        password = user_data.pop("password")
        user = User(
            **user_data,
            password_hash=hash_password(password),
            version=1
        )
        db.add(user)
        users.append(user)
        print(f"   ✓ Created user: {user_data['email']} (password: {password})")
    
    db.commit()
    print("✅ Users created successfully")
    return users


def create_user_roles(db: Session, users: list, roles: list):
    """Create user-role relationships"""
    print("\n🔗 Creating user-role relationships...")
    
    # Create a dictionary for easy role lookup
    roles_dict = {role.name: role for role in roles}
    
    # Assign roles to users
    user_role_mappings = [
        # Admin user has admin role
        {"email": "admin@webmypham.com", "role": "admin"},
        
        # Customer 1 has customer role
        {"email": "customer1@gmail.com", "role": "customer"},
        
        # Customer 2 has customer role
        {"email": "customer2@gmail.com", "role": "customer"},
        
        # Staff has both staff and customer roles
        {"email": "staff@webmypham.com", "role": "staff"},
        {"email": "staff@webmypham.com", "role": "customer"},
        
        # Manager has manager, staff, and customer roles
        {"email": "manager@webmypham.com", "role": "manager"},
        {"email": "manager@webmypham.com", "role": "staff"},
        {"email": "manager@webmypham.com", "role": "customer"}
    ]
    
    # Create a dictionary for easy user lookup
    users_dict = {user.email: user for user in users}
    
    for mapping in user_role_mappings:
        user = users_dict[mapping["email"]]
        role = roles_dict[mapping["role"]]
        
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id
        )
        db.add(user_role)
        print(f"   ✓ Assigned role '{role.name}' to user '{user.email}'")
    
    db.commit()
    print("✅ User-role relationships created successfully")


def print_summary(db: Session):
    """Print summary of created data"""
    print("\n" + "="*60)
    print("📊 SEED DATA SUMMARY")
    print("="*60)
    
    # Count records
    roles_count = db.query(Role).count()
    users_count = db.query(User).count()
    user_roles_count = db.query(UserRole).count()
    
    print(f"\n📈 Statistics:")
    print(f"   • Total Roles: {roles_count}")
    print(f"   • Total Users: {users_count}")
    print(f"   • Total User-Role Assignments: {user_roles_count}")
    
    # List all users with their roles
    print(f"\n👤 Users and their credentials:")
    print("-" * 60)
    
    users = db.query(User).all()
    for user in users:
        roles = db.query(Role).join(UserRole).filter(UserRole.user_id == user.id).all()
        role_names = ", ".join([r.name for r in roles])
        print(f"\n📧 Email: {user.email}")
        print(f"   Password: (See printed output above)")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Roles: {role_names}")
    
    print("\n" + "="*60)
    print("✅ SEED DATA CREATED SUCCESSFULLY!")
    print("="*60)
    print("\n💡 Tips:")
    print("   • Use the email and password above to test login")
    print("   • All passwords follow the format: RoleName@123")
    print("   • Admin has full access to the system")
    print("   • Customers can browse and purchase")
    print("   • Staff can manage products and orders")
    print("   • Manager has all permissions")
    print("="*60 + "\n")


def main():
    """Main function to run seed data creation"""
    print("\n" + "="*60)
    print("🌱 STARTING SEED DATA CREATION")
    print("="*60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Clear existing data
        clear_existing_data(db)
        
        # Step 2: Create roles
        roles = create_roles(db)
        
        # Step 3: Create users
        users = create_users(db)
        
        # Step 4: Create user-role relationships
        create_user_roles(db, users, roles)
        
        # Step 5: Print summary
        print_summary(db)
        
        print("🎉 All seed data has been created successfully!\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
