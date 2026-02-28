#!/usr/bin/env python3
"""
Simple Docker PostgreSQL setup without Docker Compose
Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import time
import os
import asyncio

def run_command(command, description=""):
    """Run a command and return success status"""
    try:
        if description:
            print(f"🔄 {description}...")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            if description:
                print(f"✅ {description} completed")
            return True, result.stdout
        else:
            if description:
                print(f"❌ {description} failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        if description:
            print(f"❌ {description} error: {e}")
        return False, str(e)

def check_docker():
    """Check if Docker is available"""
    print("🐳 Checking Docker...")
    success, output = run_command("docker --version")
    if success:
        print(f"✅ Docker found: {output.strip()}")
        
        # Check if Docker daemon is running
        success, _ = run_command("docker info")
        if success:
            print("✅ Docker daemon is running")
            return True
        else:
            print("❌ Docker daemon is not running. Please start Docker.")
            return False
    else:
        print("❌ Docker not found. Please install Docker.")
        return False

def setup_postgres_container():
    """Setup PostgreSQL container"""
    print("\n🗄️ Setting up PostgreSQL container...")
    
    # Check if container already exists
    success, output = run_command("docker ps -a --filter name=ai_wellness_postgres --format '{{.Names}}'")
    
    if "ai_wellness_postgres" in output:
        print("📦 Container exists, starting it...")
        success, _ = run_command("docker start ai_wellness_postgres", "Starting existing container")
    else:
        print("📦 Creating new PostgreSQL container...")
        command = """docker run -d \
            --name ai_wellness_postgres \
            -e POSTGRES_DB=ai_wellness_vision \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_PASSWORD=password \
            -p 5432:5432 \
            postgres:15-alpine"""
        
        success, _ = run_command(command, "Creating PostgreSQL container")
    
    if not success:
        return False
    
    # Wait for PostgreSQL to be ready
    print("⏳ Waiting for PostgreSQL to be ready...")
    for i in range(30):
        success, _ = run_command(
            "docker exec ai_wellness_postgres pg_isready -U postgres -d ai_wellness_vision"
        )
        if success:
            print("✅ PostgreSQL is ready!")
            return True
        
        time.sleep(2)
        print(f"   Waiting... ({i+1}/30)")
    
    print("❌ PostgreSQL failed to start within timeout")
    return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    dependencies = [
        "asyncpg",
        "bcrypt", 
        "fastapi",
        "uvicorn",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "email-validator"
    ]
    
    for dep in dependencies:
        success, _ = run_command(f"{sys.executable} -m pip install {dep}", f"Installing {dep}")
        if not success:
            print(f"⚠️ Failed to install {dep}, but continuing...")
    
    print("✅ Dependencies installation completed")
    return True

async def setup_database():
    """Setup database schema"""
    print("\n🗄️ Setting up database schema...")
    
    try:
        # Add src to Python path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.database.postgres_auth import PostgresAuthDatabase
        
        db = PostgresAuthDatabase('postgresql://postgres:password@localhost:5432/ai_wellness_vision')
        await db.initialize()
        
        # Create default users
        admin_id = await db.create_user(
            email="admin@wellnessvision.ai",
            password="admin123", 
            first_name="Admin",
            last_name="User"
        )
        
        test_id = await db.create_user(
            email="test@wellnessvision.ai",
            password="user123",
            first_name="Test", 
            last_name="User"
        )
        
        await db.close()
        
        print("✅ Database setup completed")
        print("👤 Default users created:")
        print("   • admin@wellnessvision.ai / admin123")
        print("   • test@wellnessvision.ai / user123")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_management_scripts():
    """Create Docker management scripts"""
    print("\n📝 Creating management scripts...")
    
    # Cross-platform scripts
    if os.name == 'nt':  # Windows
        # start_postgres.bat
        with open('start_postgres.bat', 'w') as f:
            f.write('''@echo off
echo Starting PostgreSQL container...
docker start ai_wellness_postgres
if %ERRORLEVEL% NEQ 0 (
    echo Creating new container...
    docker run -d --name ai_wellness_postgres -e POSTGRES_DB=ai_wellness_vision -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15-alpine
)
echo PostgreSQL is running!
''')
        
        # stop_postgres.bat
        with open('stop_postgres.bat', 'w') as f:
            f.write('''@echo off
echo Stopping PostgreSQL container...
docker stop ai_wellness_postgres
echo PostgreSQL stopped!
''')
        
        print("✅ Created: start_postgres.bat, stop_postgres.bat")
        
    else:  # Linux/macOS
        # start_postgres.sh
        with open('start_postgres.sh', 'w') as f:
            f.write('''#!/bin/bash
echo "Starting PostgreSQL container..."
docker start ai_wellness_postgres || docker run -d --name ai_wellness_postgres -e POSTGRES_DB=ai_wellness_vision -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15-alpine
echo "PostgreSQL is running!"
''')
        
        # stop_postgres.sh
        with open('stop_postgres.sh', 'w') as f:
            f.write('''#!/bin/bash
echo "Stopping PostgreSQL container..."
docker stop ai_wellness_postgres
echo "PostgreSQL stopped!"
''')
        
        # Make scripts executable
        os.chmod('start_postgres.sh', 0o755)
        os.chmod('stop_postgres.sh', 0o755)
        
        print("✅ Created: start_postgres.sh, stop_postgres.sh")

def print_success_info():
    """Print success information"""
    print("\n" + "="*60)
    print("🎉 Docker PostgreSQL Setup Complete!")
    print("="*60)
    print("\n🌐 Your API server will be available at:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Health: http://localhost:8000/health")
    
    print("\n🗄️ PostgreSQL connection:")
    print("   • Host: localhost:5432")
    print("   • Database: ai_wellness_vision")
    print("   • User: postgres")
    print("   • Password: password")
    
    print("\n👤 Default users:")
    print("   • admin@wellnessvision.ai / admin123")
    print("   • test@wellnessvision.ai / user123")
    
    print("\n🧪 Test your setup:")
    print("   python test_postgres_auth.py")
    print("   python test_flutter_postgres_integration.py")
    
    print("\n🔧 Manage PostgreSQL:")
    if os.name == 'nt':
        print("   • Start: start_postgres.bat")
        print("   • Stop: stop_postgres.bat")
    else:
        print("   • Start: ./start_postgres.sh")
        print("   • Stop: ./stop_postgres.sh")
    
    print("\n🚀 Start your API server:")
    print("   python main_api_server_postgres.py")

async def main():
    """Main setup function"""
    print("🎯 AI Wellness Vision - Docker PostgreSQL Setup")
    print("="*60)
    
    # Check Docker
    if not check_docker():
        print("\n❌ Docker is required. Please install Docker and try again.")
        print("\n📋 Install Docker:")
        print("   • Windows: https://docs.docker.com/desktop/install/windows-install/")
        print("   • macOS: https://docs.docker.com/desktop/install/mac-install/")
        print("   • Linux: https://docs.docker.com/engine/install/")
        return False
    
    # Setup PostgreSQL container
    if not setup_postgres_container():
        return False
    
    # Install Python dependencies
    if not install_dependencies():
        return False
    
    # Setup database
    if not await setup_database():
        return False
    
    # Create management scripts
    create_management_scripts()
    
    # Print success info
    print_success_info()
    
    # Ask if user wants to start the server
    try:
        response = input("\n🚀 Start the API server now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n🚀 Starting API server...")
            os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
            os.environ['ENVIRONMENT'] = 'development'
            
            subprocess.run([sys.executable, 'main_api_server_postgres.py'])
    except KeyboardInterrupt:
        print("\n🛑 Setup completed. You can start the server later with:")
        print("   python main_api_server_postgres.py")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)