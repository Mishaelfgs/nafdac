"""Create or reset an admin login. Run: python -m scripts.create_admin you@example.com"""
import getpass
import sys

from sqlalchemy import select

from app.admin.auth import hash_password
from app.db import SessionLocal, init_db
from app.models import AdminUser

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m scripts.create_admin EMAIL")
    email = sys.argv[1].strip().lower()
    pw = getpass.getpass("Password (min 10 chars): ")
    if len(pw) < 10:
        sys.exit("Password too short.")
    init_db()
    with SessionLocal() as db:
        u = db.scalar(select(AdminUser).where(AdminUser.email == email)) or AdminUser(email=email)
        u.password_hash = hash_password(pw)
        db.add(u)
        db.commit()
    print("Admin saved:", email)
