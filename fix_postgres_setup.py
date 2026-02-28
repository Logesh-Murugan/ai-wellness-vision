#!/usr/bin/env python3
"""
Fix PostgreSQL setup - Create database schema properly
"""

import os
import sys
import asyncio
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def fix_database_setup():
    """Fix database setup with proper schema creation"""
    print("🔧 Fixing PostgreSQL database setup...")
    
    try:
        from src.database.postgres_auth import PostgresAuthDatabase
        
        # Initialize database with proper connection
        database_url = 'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
        db = PostgresAuthDatabase(database_url)
        
        print("📡 Connecting to PostgreSQL...")
        await db.initialize()
        
        print("✅ Database schema created successfully")
        
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
        
        # Verify users exist
        admin_user = await db.get_user_by_email("admin@wellnessvision.ai")
        test_user = await db.get_user_by_email("test@wellnessvision.ai")
        
        if admin_user and test_user:
            print("✅ All users verified successfully")
        else:
            print("❌ User verification failed")
        
        await db.close()
        
        print("\n🎉 Database setup fixed successfully!")
        print("\n📋 Summary:")
        print("   • Database: ai_wellness_vision")
        print("   • Tables: users, user_sessions, analysis_history, chat_conversations, chat_messages")
        print("   • Admin user: admin@wellnessvision.ai / admin123")
        print("   • Test user: test@wellnessvision.ai / user123")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database_setup())
    if success:
        print("\n🚀 You can now start the server with:")
        print("   python main_api_server_postgres.py")
    else:
        sys.exit(1)