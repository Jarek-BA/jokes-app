# jokes_app/test_db_connection.py
import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# -----------------------
# DATABASE CONFIGURATION
# -----------------------
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Detect SSL usage
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
USE_SSL = ENVIRONMENT in ("production", "render", "supabase")
ssl_flag = "require" if USE_SSL else None

# Construct asyncpg connection params
conn_params = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": int(DB_PORT),
    "database": DB_NAME,
    "ssl": ssl_flag,
}

print("Connection params:", conn_params)

# -----------------------
# TEST CONNECTION
# -----------------------
async def test_connection():
    try:
        conn = await asyncpg.connect(**conn_params)
        result = await conn.fetch("SELECT NOW();")
        print("✅ Connection successful! Current time:", result[0]["now"])
        await conn.close()
    except Exception as e:
        print("❌ Failed to connect:", e)


if __name__ == "__main__":
    asyncio.run(test_connection())
