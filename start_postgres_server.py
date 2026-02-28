#!/usr/bin/env python3
"""
Start AI Wellness Vision server with PostgreSQL authentication
"""

import os
import sys
import asyncio
import subprocess
import time
import signal
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_postgres_running():
    """Check if PostgreSQL is running"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            if 'postgres' in proc.info['name'].lower():
                return True
        return False
    except ImportError:
        # Fallback: try to connect
        try:
            import asyncpg
            async def test_connection():
                try:
                    conn = await asyncpg.connect(
                        'postgresql://postgres:password@localhost:5432/postgres'
                    )
                    await conn.close()
                    return True
                except:
                    return False
            
            return asyncio.run(test_connection())
        except ImportError:
            return False

def start_postgres_docker():
    """Start PostgreSQL using Docker Compose"""
    print("🐳 Starting PostgreSQL with Docker Compose...")
    try:
        subprocess.run([
            "docker-compose", "-f", "docker-compose.postgres.yml", "up", "-d", "postgres"
        ], check=True)
        
        # Wait for PostgreSQL to be ready
        print("⏳ Waiting for PostgreSQL to be ready...")
        for i in range(30):
            try:
                result = subprocess.run([
                    "docker", "exec", "ai_wellness_postgres", 
                    "pg_isready", "-U", "postgres", "-d", "ai_wellness_vision"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ PostgreSQL is ready")
                    return True
                    
            except subprocess.CalledProcessError:
                pass
            
            time.sleep(2)
        
        print("❌ PostgreSQL failed to start within timeout")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start PostgreSQL: {e}")
        return False
    except FileNotFoundError:
        print("❌ Docker Compose not found. Please install Docker and Docker Compose.")
        return False

def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "asyncpg", "bcrypt", "fastapi", "uvicorn", "python-jose[cryptography]", "passlib[bcrypt]"
        ], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

async def setup_database():
    """Setup database if needed"""
    print("🗄️ Setting up database...")
    try:
        from setup_postgres import setup_database as setup_db
        await setup_db()
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def start_api_server():
    """Start the API server"""
    print("🚀 Starting AI Wellness Vision API server...")
    try:
        # Set environment variables
        os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/ai_wellness_vision'
        os.environ['ENVIRONMENT'] = 'development'
        
        # Start the server
        subprocess.run([
            sys.executable, "main_api_server_postgres.py"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

def print_startup_info():
    """Print startup information"""
    print("🎯 AI Wellness Vision - PostgreSQL Edition")
    print("=" * 50)
    print("🗄️ Database: PostgreSQL")
    print("🔐 Authentication: JWT with bcrypt")
    print("🌐 API Server: FastAPI")
    print("📱 Flutter Integration: Ready")
    print("=" * 50)

def print_usage():
    """Print usage instructions"""
    print("\n📋 Usage Instructions:")
    print("\n1. Ensure PostgreSQL is running:")
    print("   • Local: Start PostgreSQL service")
    print("   • Docker: docker-compose -f docker-compose.postgres.yml up -d")
    print("\n2. Run this script:")
    print("   python start_postgres_server.py")
    print("\n3. Test the API:")
    print("   python test_postgres_auth.py")
    print("\n4. Access API documentation:")
    print("   http://localhost:8000/docs")

async def main():
    """Main startup function"""
    print_startup_info()
    
    # Check if PostgreSQL is running
    if not check_postgres_running():
        print("⚠️ PostgreSQL not detected. Attempting to start with Docker...")
        if not start_postgres_docker():
            print("\n❌ Could not start PostgreSQL automatically.")
            print_usage()
            return False
    else:
        print("✅ PostgreSQL is running")
    
    # Install dependencies if needed
    try:
        import asyncpg
        import bcrypt
        print("✅ Dependencies are available")
    except ImportError:
        if not install_dependencies():
            return False
    
    # Setup database
    if not await setup_database():
        print("❌ Database setup failed")
        return False
    
    # Start API server
    print("\n🎉 Setup complete! Starting API server...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n💡 Test the authentication with: python test_postgres_auth.py")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    start_api_server()
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)