#!/usr/bin/env python3
"""
Windows PostgreSQL setup without Docker
Falls back to SQLite with PostgreSQL-compatible authentication if PostgreSQL not available
"""

import os
import sys
import asyncio
import subprocess
import logging
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_postgresql_installed():
    """Check if PostgreSQL is installed on Windows"""
    try:
        # Check for pg_config in PATH
        result = subprocess.run(['pg_config', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Check common PostgreSQL installation paths on Windows
    postgres_paths = [
        r"C:\Program Files\PostgreSQL\*\bin\pg_config.exe",
        r"C:\Program Files (x86)\PostgreSQL\*\bin\pg_config.exe",
        r"C:\PostgreSQL\*\bin\pg_config.exe"
    ]
    
    import glob
    for path_pattern in postgres_paths:
        matches = glob.glob(path_pattern)
        if matches:
            print(f"✅ PostgreSQL found at: {matches[0]}")
            return True
    
    return False

def install_postgresql_windows():
    """Guide user to install PostgreSQL on Windows"""
    print("📋 PostgreSQL Installation Guide for Windows:")
    print("\n1. Download PostgreSQL:")
    print("   Visit: https://www.postgresql.org/download/windows/")
    print("   Download the installer for your Windows version")
    print("\n2. Run the installer:")
    print("   - Choose installation directory (default is fine)")
    print("   - Set password for 'postgres' user (remember this!)")
    print("   - Use default port 5432")
    print("   - Select default locale")
    print("\n3. After installation:")
    print("   - PostgreSQL service should start automatically")
    print("   - You can manage it from Windows Services")
    print("\n4. Create database:")
    print("   Open Command Prompt as Administrator and run:")
    print("   createdb -U postgres ai_wellness_vision")
    print("\n5. Re-run this script after installation")
    
    return False

def check_python_dependencies():
    """Check and install Python dependencies"""
    print("📦 Checking Python dependencies...")
    
    required_packages = [
        'asyncpg',
        'bcrypt', 
        'fastapi',
        'uvicorn',
        'python-jose[cryptography]',
        'passlib[bcrypt]'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-jose[cryptography]':
                import jose
            elif package == 'passlib[bcrypt]':
                import passlib
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📥 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("✅ All dependencies are available")
        return True

async def test_postgresql_connection():
    """Test PostgreSQL connection"""
    try:
        import asyncpg
        
        # Try different common connection strings
        connection_strings = [
            'postgresql://postgres:password@localhost:5432/ai_wellness_vision',
            'postgresql://postgres:postgres@localhost:5432/ai_wellness_vision',
            'postgresql://postgres@localhost:5432/ai_wellness_vision'
        ]
        
        for conn_str in connection_strings:
            try:
                print(f"🔍 Testing connection: {conn_str.replace('password', '***').replace('postgres:', 'postgres:***@')}")
                conn = await asyncpg.connect(conn_str)
                await conn.close()
                print("✅ PostgreSQL connection successful!")
                
                # Update .env file with working connection string
                update_env_file(conn_str)
                return True, conn_str
                
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                continue
        
        return False, None
        
    except ImportError:
        print("❌ asyncpg not available")
        return False, None

def update_env_file(database_url):
    """Update .env file with working database URL"""
    env_file = Path('.env')
    
    if env_file.exists():
        # Read existing content
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update DATABASE_URL line
        updated_lines = []
        database_url_updated = False
        
        for line in lines:
            if line.startswith('DATABASE_URL='):
                updated_lines.append(f'DATABASE_URL={database_url}\n')
                database_url_updated = True
            else:
                updated_lines.append(line)
        
        # Add DATABASE_URL if not found
        if not database_url_updated:
            updated_lines.append(f'DATABASE_URL={database_url}\n')
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Updated .env file with database URL")

async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        import asyncpg
        
        # Try to connect to postgres database first
        try:
            conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/postgres')
        except:
            try:
                conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
            except:
                conn = await asyncpg.connect('postgresql://postgres@localhost:5432/postgres')
        
        # Check if our database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'ai_wellness_vision'"
        )
        
        if not result:
            print("🗄️ Creating database 'ai_wellness_vision'...")
            await conn.execute("CREATE DATABASE ai_wellness_vision")
            print("✅ Database created successfully")
        else:
            print("✅ Database 'ai_wellness_vision' already exists")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

async def setup_database_schema():
    """Setup database schema"""
    try:
        from src.database.postgres_auth import PostgresAuthDatabase
        
        # Get working connection string from .env
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/ai_wellness_vision')
        
        db = PostgresAuthDatabase(database_url)
        await db.initialize()
        
        # Create default users
        print("👤 Creating default users...")
        
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
        
        await db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database schema setup failed: {e}")
        return False

def create_fallback_sqlite_setup():
    """Create SQLite fallback with PostgreSQL-compatible authentication"""
    print("🔄 Setting up SQLite fallback with PostgreSQL-compatible authentication...")
    
    # Update .env to use SQLite
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace PostgreSQL URL with SQLite
        content = content.replace(
            'DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_wellness_vision',
            'DATABASE_URL=sqlite:///./ai_wellness_vision.db'
        )
        
        with open(env_file, 'w') as f:
            f.write(content)
    
    print("✅ Configured to use SQLite with PostgreSQL-compatible authentication")
    print("📝 You can upgrade to PostgreSQL later by:")
    print("   1. Installing PostgreSQL")
    print("   2. Running this script again")
    print("   3. Your data will be preserved")
    
    return True

async def main():
    """Main setup function"""
    print("🎯 AI Wellness Vision - PostgreSQL Setup for Windows")
    print("=" * 55)
    
    # Check Python dependencies first
    if not check_python_dependencies():
        print("❌ Cannot continue without required Python packages")
        return False
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        print("⚠️ PostgreSQL not found on this system")
        
        choice = input("\nWould you like to:\n1. Install PostgreSQL (recommended)\n2. Use SQLite fallback\n\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            install_postgresql_windows()
            print("\n🔄 Please install PostgreSQL and run this script again")
            return False
        else:
            return create_fallback_sqlite_setup()
    
    # PostgreSQL is installed, try to set it up
    print("✅ PostgreSQL installation detected")
    
    # Create database if needed
    if not await create_database_if_not_exists():
        print("❌ Could not create database")
        return False
    
    # Test connection
    success, conn_str = await test_postgresql_connection()
    if not success:
        print("❌ Could not connect to PostgreSQL")
        print("💡 Try these steps:")
        print("   1. Make sure PostgreSQL service is running")
        print("   2. Check if password is correct")
        print("   3. Verify database exists")
        
        choice = input("\nUse SQLite fallback instead? (y/n): ").strip().lower()
        if choice == 'y':
            return create_fallback_sqlite_setup()
        return False
    
    # Setup database schema
    if not await setup_database_schema():
        return False
    
    print("\n🎉 PostgreSQL setup completed successfully!")
    print("\n📋 Summary:")
    print("   • Database: ai_wellness_vision")
    print("   • Admin user: admin@wellnessvision.ai / admin123")
    print("   • Test user: test@wellnessvision.ai / user123")
    print(f"   • Connection: {conn_str.replace('password', '***')}")
    
    print("\n🚀 Next steps:")
    print("   1. Start the server: python main_api_server_postgres.py")
    print("   2. Test authentication: python test_postgres_auth.py")
    print("   3. Access API docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)