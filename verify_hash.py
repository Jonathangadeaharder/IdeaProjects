from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
import sqlite3

password = "TestPassword123!"
try:
    conn = sqlite3.connect(r'e:\Users\Jonandrop\IdeaProjects\LangPlug\src\backend\core\data\langplug.db')
    row = conn.execute("SELECT hashed_password FROM users WHERE email='e2etest@example.com'").fetchone()
    if not row:
        print("User not found")
        exit(1)
    hash = row[0]
    print(f"Hash: {hash}")

    ph = PasswordHash([Argon2Hasher()])
    valid = ph.verify(password, hash)
    print(f"Valid: {valid}")
except Exception as e:
    import traceback
    traceback.print_exc()
