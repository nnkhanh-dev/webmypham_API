
import sys
from passlib.context import CryptContext

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash_val = pwd_context.hash("test")
    print(f"Bcrypt success! Hash: {hash_val}")
except Exception as e:
    print(f"Bcrypt failed: {e}")

try:
    import bcrypt
    print(f"Bcrypt module found: {bcrypt.__file__}")
except ImportError:
    print("Bcrypt module NOT found")
