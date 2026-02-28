#!/usr/bin/env python3
"""
AI Wellness Vision - Database Setup Script
Creates the required database tables for the application
"""

import asyncio
import asyncpg
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_wellness_vision',
    'user': 'wellness_user',
    'password': 'wellness_pass123'
}

# SQL to create tables
CREATE_TABLES_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    profile_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    result TEXT NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    recommendations TEXT[],
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat conversations table
CREATE TABLE IF NOT EXISTS chat_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    conversation_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_id ON chat_conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
"""

# Insert demo user
INSERT_DEMO_USER_SQL = """
INSERT INTO users (email, password_hash, name) 
VALUES ($1, $2, $3)
ON CONFLICT (email) DO NOTHING
RETURNING id;
"""

async def setup_database():
    """Setup the database with required tables and demo data"""
    
    print("🎯 AI Wellness Vision - Database Setup")
    print("=" * 50)
    
    try:
        # Connect to database
        print("📡 Connecting to PostgreSQL...")
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Connected to database successfully!")
        
        # Create tables
        print("🏗️ Creating database tables...")
        await conn.execute(CREATE_TABLES_SQL)
        print("✅ Database tables created successfully!")
        
        # Insert demo user (password is 'admin123' hashed with bcrypt)
        print("👤 Creating demo user...")
        import bcrypt
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_id = await conn.fetchval(
            INSERT_DEMO_USER_SQL,
            'admin@wellnessvision.ai',
            password_hash,
            'Demo Admin User'
        )
        
        if user_id:
            print(f"✅ Demo user created with ID: {user_id}")
        else:
            print("ℹ️ Demo user already exists")
        
        # Insert sample analysis data
        print("📊 Adding sample analysis data...")
        await conn.execute("""
            INSERT INTO analysis_results (user_id, type, result, confidence, recommendations)
            SELECT 1, 'skin', 'Healthy skin detected with good hydration', 0.92, 
                   ARRAY['Continue current routine', 'Use sunscreen daily', 'Stay hydrated']
            WHERE NOT EXISTS (SELECT 1 FROM analysis_results WHERE type = 'skin' LIMIT 1);
        """)
        
        await conn.execute("""
            INSERT INTO analysis_results (user_id, type, result, confidence, recommendations)
            SELECT 1, 'food', 'Nutritious meal with balanced macronutrients', 0.88,
                   ARRAY['Great protein source', 'Add more vegetables', 'Consider portion size']
            WHERE NOT EXISTS (SELECT 1 FROM analysis_results WHERE type = 'food' LIMIT 1);
        """)
        
        print("✅ Sample data added successfully!")
        
        # Verify setup
        print("🔍 Verifying database setup...")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        analysis_count = await conn.fetchval("SELECT COUNT(*) FROM analysis_results")
        
        print(f"📊 Database Statistics:")
        print(f"   Users: {user_count}")
        print(f"   Analysis Results: {analysis_count}")
        
        await conn.close()
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📋 Demo Login Credentials:")
        print("   Email: admin@wellnessvision.ai")
        print("   Password: admin123")
        print("\n🚀 You can now start the backend server:")
        print("   python working_postgres_server.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    # Install bcrypt if not available
    try:
        import bcrypt
    except ImportError:
        print("📦 Installing bcrypt...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
        import bcrypt
    
    # Run setup
    success = asyncio.run(setup_database())
    sys.exit(0 if success else 1)