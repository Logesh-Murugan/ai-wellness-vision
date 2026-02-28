#!/usr/bin/env python3
"""
SQLite database setup for authentication data
"""

import sqlite3
import json
from datetime import datetime
import uuid

class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with user table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                name TEXT,
                avatar TEXT,
                preferences TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                access_token TEXT,
                refresh_token TEXT,
                expires_at TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def create_user(self, email, password_hash, first_name=None, last_name=None):
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        name = f"{first_name or ''} {last_name or ''}".strip() or email.split('@')[0].title()
        
        try:
            cursor.execute('''
                INSERT INTO users (id, email, password_hash, first_name, last_name, name, preferences, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                email,
                password_hash,
                first_name,
                last_name,
                name,
                json.dumps({"language": "en", "notifications": True, "theme": "light"}),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None  # User already exists
        finally:
            conn.close()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'email': row[1],
                'password_hash': row[2],
                'firstName': row[3],
                'lastName': row[4],
                'name': row[5],
                'avatar': row[6],
                'preferences': json.loads(row[7]) if row[7] else {},
                'created_at': row[8],
                'updated_at': row[9]
            }
        return None
    
    def save_session(self, user_id, access_token, refresh_token, expires_at):
        """Save user session tokens"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        session_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO user_sessions (id, user_id, access_token, refresh_token, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, access_token, refresh_token, expires_at, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return session_id

if __name__ == "__main__":
    # Test the database
    db = UserDatabase()
    print("🗄️ Database setup complete!")
    print("📍 Database location: users.db")