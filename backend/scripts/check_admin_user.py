"""Quick script to check admin user"""
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "admin@temple.com").first()
    if user:
        print(f"✅ Admin user found:")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        print(f"   Full Name: {user.full_name}")
    else:
        print("❌ Admin user NOT found")
        print("   Creating admin user...")
        from app.core.security import get_password_hash
        admin_user = User(
            email="admin@temple.com",
            password_hash=get_password_hash("admin123"),
            full_name="Admin User",
            role="temple_manager",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created: admin@temple.com / admin123")
finally:
    db.close()






