import asyncpg
from config import DATABASE_URL

async def get_conn():
    return await asyncpg.connect(DATABASE_URL)

async def init_db():
    conn = await get_conn()
    await conn.execute('''CREATE TABLE IF NOT EXISTS users
        (id BIGINT PRIMARY KEY, username TEXT, balance REAL DEFAULT 0,
        is_active INTEGER DEFAULT 0, current_level INTEGER DEFAULT 0,
        usdt_address TEXT, activation_ss TEXT)''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS withdraws
        (id SERIAL PRIMARY KEY, user_id BIGINT, level INTEGER,
        amount REAL, address TEXT, status TEXT DEFAULT 'pending')''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS activations
        (id SERIAL PRIMARY KEY, user_id BIGINT, ss_file_id TEXT,
        status TEXT DEFAULT 'pending', time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    await conn.close()

async def create_user(user_id, username):
    conn = await get_conn()
    await conn.execute("INSERT INTO users (id, username) VALUES ($1, $2) ON CONFLICT (id) DO NOTHING", user_id, username)
    await conn.close()

async def get_user(user_id):
    conn = await get_conn()
    user = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
    await conn.close()
    return user
