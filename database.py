import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    content TEXT
)
""")

conn.commit()

def add_user(user_id):
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()

def save_message(user_id, role, content):
    cursor.execute('INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)', (user_id, role, content))
    conn.commit()

def get_messages(user_id):
    cursor.execute('SELECT role, content FROM messages WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()

    messages = [{"role": role, "content": content} for role, content in rows]
    return list(reversed(messages))

def clear_messages(user_id):
    cursor.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
    conn.commit()