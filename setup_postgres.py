#!/usr/bin/env python3
"""
PostgreSQL setup script for AI Wellness Vision
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import asyncpg
    from src.database.postgres_auth import PostgresAuthDatabase
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("❌ PostgreSQL dependencies not installed")
    print("Install with: pip install asyncpg bcrypt")
    sys.exit(1)

async def setup_database():
    """Setup PostgreSQL database"""
    print("🗄️ Setting up PostgreSQL database for AI Wellness Vision...")
    
    try:
        # Database connection parameters
        database_url = os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
        )
        
        print(f"📡 Connecting to: {database_url}")
        
        # Initialize database
        db = PostgresAuthDatabase(database_url)
        await db.initialize()
        
        print("✅ Database initialized successfully")
        
        # Create default users
        print("👤 Creating default users...")
        
        # Admin user
        admin_id = await db.create_user(
            email="admin@wellnessvision.ai",
            password="admin123",
            first_name="Admin",
            last_name="User"
        )
        
        if admin_id:
            print("✅ Admin user created: admin@wellnessvision.ai / admin123")
        else:
            print("ℹ️ Admin user already exists")
        
        # Test user
        test_id = await db.create_user(
            email="test@wellnessvision.ai",
            password="user123",
            first_name="Test",
            last_name="User"
        )
        
        if test_id:
            print("✅ Test user created: test@wellnessvision.ai / user123")
        else:
            print("ℹ️ Test user already exists")
        
        # Verify setup
        print("\n🔍 Verifying setup...")
        admin_user = await db.get_user_by_email("admin@wellnessvision.ai")
        test_user = await db.get_user_by_email("test@wellnessvision.ai")
        
        if admin_user and test_user:
            print("✅ All users verified successfully")
        else:
            print("❌ User verification failed")
        
        await db.close()
        
        print("\n🎉 PostgreSQL setup completed successfully!")
        print("\n📋 Summary:")
        print("   • Database: ai_wellness_vision")
        print("   • Admin user: admin@wellnessvision.ai / admin123")
        print("   • Test user: test@wellnessvision.ai / user123")
        print("\n🚀 You can now start the server with:")
        print("   python main_api_server_postgres.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

async def test_connection():
    """Test database connection"""
    print("🔍 Testing PostgreSQL connection...")
    
    try:
        database_url = os.getenv(
            'DATABASE_URL', 
            'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
        )
        
        conn = await asyncpg.connect(database_url)
        result = await conn.fetchval('SELECT version()')
        await conn.close()
        
        print(f"✅ Connection successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions"""
    print("📋 PostgreSQL Setup Instructions:")
    print("\n1. Install PostgreSQL:")
    print("   • Windows: Download from https://www.postgresql.org/download/")
    print("   • macOS: brew install postgresql")
    print("   • Ubuntu: sudo apt-get install postgresql postgresql-contrib")
    print("\n2. Start PostgreSQL service:")
    print("   • Windows: Start from Services or pgAdmin")
    print("   • macOS/Linux: sudo service postgresql start")
    print("\n3. Create database:")
    print("   createdb ai_wellness_vision")
    print("\n4. Set environment variable (optional):")
    print("   export DATABASE_URL='postgresql://username:password@localhost:5432/ai_wellness_vision'")
    print("\n5. Install Python dependencies:")
    print("   pip install asyncpg bcrypt")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test connection only
        asyncio.run(test_connection())
    elif len(sys.argv) > 1 and sys.argv[1] == "help":
        # Show setup instructions
        print_setup_instructions()
    else:
        # Full setup
        asyncio.run(setup_database())