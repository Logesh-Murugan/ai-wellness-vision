#!/usr/bin/env python3
"""
PostgreSQL database setup and authentication for AI Wellness Vision
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

try:
    import asyncpg
    import bcrypt
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logging.warning("PostgreSQL libraries not available - install asyncpg and bcrypt")

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class PostgresAuthDatabase:
    """PostgreSQL database manager for authentication"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
        )
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        if not POSTGRES_AVAILABLE:
            raise RuntimeError("PostgreSQL dependencies not installed")
            
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ PostgreSQL connection pool initialized")
            
            # Ensure tables exist
            await self.create_tables()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        async with self.pool.acquire() as conn:
            # Create tables directly instead of reading SQL file
            try:
                await self._create_basic_tables(conn)
                logger.info("✅ Database tables verified/created")
                
            except Exception as e:
                logger.error(f"Failed to create tables: {e}")
                raise
    
    async def _create_basic_tables(self, conn):
        """Create basic tables"""
        # Create users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                name VARCHAR(200),
                avatar TEXT,
                preferences JSONB DEFAULT '{"language": "en", "notifications": true, "theme": "light"}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Create user_sessions table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Create analysis_history table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                analysis_type VARCHAR(50) NOT NULL,
                image_path TEXT,
                result JSONB NOT NULL,
                confidence DECIMAL(3,2),
                recommendations JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Create chat_conversations table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200),
                mode VARCHAR(50) DEFAULT 'general',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Create chat_messages table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                conversation_id UUID REFERENCES chat_conversations(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                is_user BOOLEAN NOT NULL,
                message_type VARCHAR(20) DEFAULT 'text',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Create indexes
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_access_token ON user_sessions(access_token)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id ON chat_conversations(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON chat_messages(conversation_id)')
        
        # Create update trigger function
        await conn.execute('''
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        ''')
        
        # Create triggers
        await conn.execute('''
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
            CREATE TRIGGER update_users_updated_at 
                BEFORE UPDATE ON users
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        ''')
        
        await conn.execute('''
            DROP TRIGGER IF EXISTS update_chat_conversations_updated_at ON chat_conversations;
            CREATE TRIGGER update_chat_conversations_updated_at 
                BEFORE UPDATE ON chat_conversations
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        ''')
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        if not POSTGRES_AVAILABLE:
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()
        
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if not POSTGRES_AVAILABLE:
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest() == hashed
        
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    async def create_user(self, email: str, password: str, first_name: str = None, 
                         last_name: str = None) -> Optional[str]:
        """Create a new user"""
        async with self.pool.acquire() as conn:
            try:
                password_hash = self.hash_password(password)
                name = f"{first_name or ''} {last_name or ''}".strip() or email.split('@')[0].title()
                
                user_id = await conn.fetchval('''
                    INSERT INTO users (email, password_hash, first_name, last_name, name)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                ''', email, password_hash, first_name, last_name, name)
                
                logger.info(f"✅ User created: {email}")
                return str(user_id)
                
            except asyncpg.UniqueViolationError:
                logger.warning(f"User already exists: {email}")
                return None
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('''
                    SELECT id, email, password_hash, first_name, last_name, name, 
                           avatar, preferences, created_at, updated_at
                    FROM users WHERE email = $1
                ''', email)
                
                if row:
                    return {
                        'id': str(row['id']),
                        'email': row['email'],
                        'password_hash': row['password_hash'],
                        'firstName': row['first_name'],
                        'lastName': row['last_name'],
                        'name': row['name'],
                        'avatar': row['avatar'],
                        'preferences': row['preferences'] or {},
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                return None
                
            except Exception as e:
                logger.error(f"Failed to get user: {e}")
                return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('''
                    SELECT id, email, password_hash, first_name, last_name, name, 
                           avatar, preferences, created_at, updated_at
                    FROM users WHERE id = $1
                ''', uuid.UUID(user_id))
                
                if row:
                    return {
                        'id': str(row['id']),
                        'email': row['email'],
                        'password_hash': row['password_hash'],
                        'firstName': row['first_name'],
                        'lastName': row['last_name'],
                        'name': row['name'],
                        'avatar': row['avatar'],
                        'preferences': row['preferences'] or {},
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                return None
                
            except Exception as e:
                logger.error(f"Failed to get user by ID: {e}")
                return None
    
    async def save_session(self, user_id: str, access_token: str, 
                          refresh_token: str, expires_at: datetime) -> Optional[str]:
        """Save user session"""
        async with self.pool.acquire() as conn:
            try:
                session_id = await conn.fetchval('''
                    INSERT INTO user_sessions (user_id, access_token, refresh_token, expires_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                ''', uuid.UUID(user_id), access_token, refresh_token, expires_at)
                
                return str(session_id)
                
            except Exception as e:
                logger.error(f"Failed to save session: {e}")
                return None
    
    async def get_session_by_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get session by access token"""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow('''
                    SELECT s.id, s.user_id, s.access_token, s.refresh_token, 
                           s.expires_at, s.created_at, u.email, u.name
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.access_token = $1 AND s.expires_at > NOW()
                ''', access_token)
                
                if row:
                    return {
                        'id': str(row['id']),
                        'user_id': str(row['user_id']),
                        'access_token': row['access_token'],
                        'refresh_token': row['refresh_token'],
                        'expires_at': row['expires_at'],
                        'created_at': row['created_at'],
                        'user_email': row['email'],
                        'user_name': row['name']
                    }
                return None
                
            except Exception as e:
                logger.error(f"Failed to get session: {e}")
                return None
    
    async def delete_session(self, access_token: str) -> bool:
        """Delete session by access token"""
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute('''
                    DELETE FROM user_sessions WHERE access_token = $1
                ''', access_token)
                
                return result == "DELETE 1"
                
            except Exception as e:
                logger.error(f"Failed to delete session: {e}")
                return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute('''
                    DELETE FROM user_sessions WHERE expires_at < NOW()
                ''')
                
                count = int(result.split()[-1]) if result.startswith("DELETE") else 0
                if count > 0:
                    logger.info(f"Cleaned up {count} expired sessions")
                return count
                
            except Exception as e:
                logger.error(f"Failed to cleanup sessions: {e}")
                return 0
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute('''
                    UPDATE users SET preferences = $1, updated_at = NOW()
                    WHERE id = $2
                ''', json.dumps(preferences), uuid.UUID(user_id))
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to update preferences: {e}")
                return False

    # ─────────────────────────────────────────
    # Analysis history
    # ─────────────────────────────────────────

    async def save_analysis(
        self,
        user_id: Optional[str],
        analysis_type: str,
        image_path: Optional[str],
        result: Dict[str, Any],
        confidence: float,
        recommendations: List[Any],
    ) -> Optional[str]:
        """Persist an analysis result and return its UUID."""
        async with self.pool.acquire() as conn:
            try:
                uid = uuid.UUID(user_id) if user_id else None
                row_id = await conn.fetchval(
                    """
                    INSERT INTO analysis_history
                        (user_id, analysis_type, image_path, result, confidence, recommendations)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                    """,
                    uid,
                    analysis_type,
                    image_path,
                    json.dumps(result),
                    confidence,
                    json.dumps(recommendations),
                )
                return str(row_id)
            except Exception as e:
                logger.error(f"Failed to save analysis: {e}")
                return None

    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get a single analysis result by ID."""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM analysis_history WHERE id = $1",
                    uuid.UUID(analysis_id),
                )
                if row:
                    return self._row_to_analysis(row)
                return None
            except Exception as e:
                logger.error(f"Failed to get analysis: {e}")
                return None

    async def get_analyses_paginated(
        self,
        user_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Return paginated analysis history."""
        offset = (page - 1) * limit
        async with self.pool.acquire() as conn:
            try:
                if user_id:
                    uid = uuid.UUID(user_id)
                    total = await conn.fetchval(
                        "SELECT count(*) FROM analysis_history WHERE user_id = $1", uid
                    )
                    rows = await conn.fetch(
                        "SELECT * FROM analysis_history WHERE user_id = $1 "
                        "ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                        uid, limit, offset,
                    )
                else:
                    total = await conn.fetchval("SELECT count(*) FROM analysis_history")
                    rows = await conn.fetch(
                        "SELECT * FROM analysis_history ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                        limit, offset,
                    )
                return {
                    "results": [self._row_to_analysis(r) for r in rows],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit if total else 0,
                    },
                }
            except Exception as e:
                logger.error(f"Failed to get analyses: {e}")
                return {"results": [], "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0}}

    @staticmethod
    def _row_to_analysis(row) -> Dict[str, Any]:
        """Convert a DB row to the API response dict."""
        result_data = row["result"] if isinstance(row["result"], dict) else json.loads(row["result"])
        recs = row["recommendations"]
        if isinstance(recs, str):
            recs = json.loads(recs)
        return {
            "id": str(row["id"]),
            "type": row["analysis_type"],
            "result": result_data.get("result", "") if isinstance(result_data, dict) else str(result_data),
            "confidence": float(row["confidence"]) if row["confidence"] else 0.0,
            "recommendations": recs if recs else [],
            "timestamp": row["created_at"].isoformat() if row["created_at"] else "",
            "image_path": row["image_path"],
        }

    # ─────────────────────────────────────────
    # Chat conversations & messages
    # ─────────────────────────────────────────

    async def save_conversation(
        self,
        user_id: Optional[str],
        title: str = "New Conversation",
        mode: str = "general",
    ) -> Optional[Dict[str, Any]]:
        """Create a new conversation and return it."""
        async with self.pool.acquire() as conn:
            try:
                uid = uuid.UUID(user_id) if user_id else None
                row = await conn.fetchrow(
                    """
                    INSERT INTO chat_conversations (user_id, title, mode)
                    VALUES ($1, $2, $3)
                    RETURNING *
                    """,
                    uid, title, mode,
                )
                return self._row_to_conversation(row) if row else None
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")
                return None

    async def get_conversations(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List conversations, optionally filtered by user."""
        async with self.pool.acquire() as conn:
            try:
                if user_id:
                    rows = await conn.fetch(
                        """
                        SELECT c.*, (SELECT count(*) FROM chat_messages m WHERE m.conversation_id = c.id) AS message_count
                        FROM chat_conversations c WHERE c.user_id = $1
                        ORDER BY c.updated_at DESC
                        """,
                        uuid.UUID(user_id),
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT c.*, (SELECT count(*) FROM chat_messages m WHERE m.conversation_id = c.id) AS message_count
                        FROM chat_conversations c
                        ORDER BY c.updated_at DESC
                        """
                    )
                return [self._row_to_conversation(r) for r in rows]
            except Exception as e:
                logger.error(f"Failed to get conversations: {e}")
                return []

    @staticmethod
    def _row_to_conversation(row) -> Dict[str, Any]:
        return {
            "id": str(row["id"]),
            "title": row["title"],
            "mode": row["mode"] or "general",
            "created_at": row["created_at"].isoformat() if row["created_at"] else "",
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else "",
            "message_count": row.get("message_count", 0),
        }

    async def save_message(
        self,
        conversation_id: str,
        content: str,
        is_user: bool,
        message_type: str = "text",
    ) -> Optional[Dict[str, Any]]:
        """Insert a chat message and return it."""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO chat_messages (conversation_id, content, is_user, message_type)
                    VALUES ($1, $2, $3, $4)
                    RETURNING *
                    """,
                    uuid.UUID(conversation_id), content, is_user, message_type,
                )
                # Touch conversation updated_at
                await conn.execute(
                    "UPDATE chat_conversations SET updated_at = NOW() WHERE id = $1",
                    uuid.UUID(conversation_id),
                )
                return self._row_to_message(row) if row else None
            except Exception as e:
                logger.error(f"Failed to save message: {e}")
                return None

    async def get_messages_paginated(
        self,
        conversation_id: str,
        page: int = 1,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Return paginated messages for a conversation."""
        offset = (page - 1) * limit
        async with self.pool.acquire() as conn:
            try:
                cid = uuid.UUID(conversation_id)
                total = await conn.fetchval(
                    "SELECT count(*) FROM chat_messages WHERE conversation_id = $1", cid
                )
                rows = await conn.fetch(
                    "SELECT * FROM chat_messages WHERE conversation_id = $1 "
                    "ORDER BY created_at ASC LIMIT $2 OFFSET $3",
                    cid, limit, offset,
                )
                return {
                    "messages": [self._row_to_message(r) for r in rows],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit if total else 0,
                    },
                }
            except Exception as e:
                logger.error(f"Failed to get messages: {e}")
                return {"messages": [], "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0}}

    @staticmethod
    def _row_to_message(row) -> Dict[str, Any]:
        return {
            "id": str(row["id"]),
            "content": row["content"],
            "is_user": row["is_user"],
            "timestamp": row["created_at"].isoformat() if row["created_at"] else "",
            "type": row.get("message_type", "text"),
        }

# Global database instance
postgres_db = PostgresAuthDatabase()

async def get_postgres_db() -> PostgresAuthDatabase:
    """Get the global PostgreSQL database instance"""
    if not postgres_db.pool:
        await postgres_db.initialize()
    return postgres_db

# Utility functions for backward compatibility
async def init_postgres_auth():
    """Initialize PostgreSQL authentication"""
    await postgres_db.initialize()

async def close_postgres_auth():
    """Close PostgreSQL authentication"""
    await postgres_db.close()