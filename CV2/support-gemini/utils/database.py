"""
utils/database.py
SQLite database manager for storing OTT support conversations.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "conversations.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT UNIQUE NOT NULL,
            language    TEXT DEFAULT 'en',
            mode        TEXT DEFAULT 'chat',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL,         -- 'user' or 'assistant'
            content     TEXT NOT NULL,
            language    TEXT DEFAULT 'en',
            mode        TEXT DEFAULT 'chat',   -- 'chat' or 'voice'
            timestamp   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            rating      INTEGER,               -- 1-5
            comment     TEXT,
            timestamp   TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()

def create_session(session_id: str, language: str = "en", mode: str = "chat"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO sessions (session_id, language, mode) VALUES (?, ?, ?)",
        (session_id, language, mode)
    )
    conn.commit()
    conn.close()

def save_message(session_id: str, role: str, content: str, language: str = "en", mode: str = "chat"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content, language, mode) VALUES (?, ?, ?, ?, ?)",
        (session_id, role, content, language, mode)
    )
    conn.commit()
    conn.close()

def get_session_messages(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_sessions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.session_id, s.language, s.mode, s.created_at,
               COUNT(m.id) AS message_count
        FROM sessions s
        LEFT JOIN messages m ON s.session_id = m.session_id
        GROUP BY s.session_id
        ORDER BY s.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_feedback(session_id: str, rating: int, comment: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (session_id, rating, comment) VALUES (?, ?, ?)",
        (session_id, rating, comment)
    )
    conn.commit()
    conn.close()

def get_all_messages_flat():
    """Return all messages for Google Sheets export."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.session_id, m.role, m.content, m.language, m.mode, m.timestamp
        FROM messages m
        ORDER BY m.id DESC
        LIMIT 1000
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
