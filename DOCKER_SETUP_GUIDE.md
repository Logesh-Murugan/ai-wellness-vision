# 🐳 Docker Setup Guide for AI Wellness Vision

This guide provides multiple ways to run PostgreSQL with Docker for your AI Wellness Vision app.

## 🎯 Quick Start Options

### Option 1: Automated Docker Setup (Recommended)
```bash
python start_docker_postgres.py
```

### Option 2: Simple Docker Compose
```bash
docker-compose -f docker-compose.simple.yml up -d
```

### Option 3: Manual Docker Commands
```bash
# Start PostgreSQL container
docker run -d \
  --name ai_wellness_postgres \
  -e POSTGRES_DB=ai_wellness_vision \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine
```

## 📋 Prerequisites

### Install Docker

**Windows:**
1. Download Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
2. Run installer as Administrator
3. Restart computer if prompted
4. Start Docker Desktop

**macOS:**
1. Download Docker Desktop: https://docs.docker.com/desktop/install/mac-install/
2. Drag Docker to Applications folder
3. Launch Docker from Applications

**Linux (Ubuntu/Debian):**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

### Verify Docker Installation
```bash
docker --version
docker run hello-world
```

## 🚀 Setup Methods

### Method 1: Automated Setup Script

This is the easiest method that handles everything automatically:

```bash
# Run the automated setup
python start_docker_postgres.py
```

**What it does:**
- ✅ Checks Docker installation
- ✅ Creates PostgreSQL container
- ✅ Installs Python dependencies
- ✅ Sets up database schema
- ✅ Creates default users
- ✅ Creates management scripts
- ✅ Starts API server

### Method 2: Docker Compose (Simple)

If you have Docker Compose installed:

```bash
# Start PostgreSQL only
docker-compose -f docker-compose.simple.yml up -d

# Check status
docker-compose -f docker-compose.simple.yml ps

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop services
docker-compose -f docker-compose.simple.yml down
```

### Method 3: Manual Docker Commands

For full control over the setup:

```bash
# 1. Create and start PostgreSQL container
docker run -d \
  --name ai_wellness_postgres \
  -e POSTGRES_DB=ai_wellness_vision \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine

# 2. Wait for PostgreSQL to be ready
docker exec ai_wellness_postgres pg_isready -U postgres -d ai_wellness_vision

# 3. Install Python dependencies
pip install asyncpg bcrypt fastapi uvicorn python-jose[cryptography] passlib[bcrypt]

# 4. Setup database
python setup_postgres.py

# 5. Start API server
python main_api_server_postgres.py
```

## 🔧 Container Management

### Start/Stop PostgreSQL

**Using generated scripts:**

Windows:
```cmd
start_postgres.bat    # Start PostgreSQL
stop_postgres.bat     # Stop PostgreSQL
```

Linux/macOS:
```bash
./start_postgres.sh   # Start PostgreSQL
./stop_postgres.sh    # Stop PostgreSQL
```

**Using Docker commands:**
```bash
# Start container
docker start ai_wellness_postgres

# Stop container
docker stop ai_wellness_postgres

# Restart container
docker restart ai_wellness_postgres

# Remove container (data will be lost)
docker rm ai_wellness_postgres
```

### Check Container Status
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Check PostgreSQL status
docker exec ai_wellness_postgres pg_isready -U postgres -d ai_wellness_vision

# View container logs
docker logs ai_wellness_postgres
```

### Connect to PostgreSQL
```bash
# Connect using docker exec
docker exec -it ai_wellness_postgres psql -U postgres -d ai_wellness_vision

# Connect using external client
psql -h localhost -p 5432 -U postgres -d ai_wellness_vision
```

## 🗄️ Database Management

### Backup Database
```bash
# Create backup
docker exec ai_wellness_postgres pg_dump -U postgres ai_wellness_vision > backup.sql

# Restore backup
docker exec -i ai_wellness_postgres psql -U postgres -d ai_wellness_vision < backup.sql
```

### Reset Database
```bash
# Stop and remove container
docker stop ai_wellness_postgres
docker rm ai_wellness_postgres

# Remove data volume (optional - this deletes all data)
docker volume rm ai_wellness_postgres_data

# Start fresh container
docker run -d --name ai_wellness_postgres \
  -e POSTGRES_DB=ai_wellness_vision \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine

# Setup database again
python setup_postgres.py
```

## 🧪 Testing

### Test Database Connection
```bash
# Test with Python script
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:password@localhost:5432/ai_wellness_vision'))"

# Test with Docker
docker exec ai_wellness_postgres pg_isready -U postgres -d ai_wellness_vision
```

### Test API Authentication
```bash
# Run authentication tests
python test_postgres_auth.py

# Run Flutter integration tests
python test_flutter_postgres_integration.py
```

## 🔐 Security Configuration

### Production Settings

For production, update these settings:

```bash
# Use strong passwords
docker run -d --name ai_wellness_postgres \
  -e POSTGRES_DB=ai_wellness_vision \
  -e POSTGRES_USER=ai_wellness_user \
  -e POSTGRES_PASSWORD=your_strong_password_here \
  -p 5432:5432 \
  postgres:15-alpine
```

### Environment Variables
```env
DATABASE_URL=postgresql://ai_wellness_user:your_strong_password@localhost:5432/ai_wellness_vision
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
```

## 🚨 Troubleshooting

### Common Issues

**Docker not found:**
```bash
# Install Docker following the prerequisites section above
```

**Port 5432 already in use:**
```bash
# Check what's using the port
netstat -tulpn | grep 5432

# Use different port
docker run -d --name ai_wellness_postgres \
  -e POSTGRES_DB=ai_wellness_vision \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5433:5432 \
  postgres:15-alpine

# Update connection string
DATABASE_URL=postgresql://postgres:password@localhost:5433/ai_wellness_vision
```

**Container won't start:**
```bash
# Check Docker logs
docker logs ai_wellness_postgres

# Check Docker daemon status
docker info

# Restart Docker service (Linux)
sudo systemctl restart docker
```

**Connection refused:**
```bash
# Check if container is running
docker ps

# Check if PostgreSQL is ready
docker exec ai_wellness_postgres pg_isready -U postgres -d ai_wellness_vision

# Check port mapping
docker port ai_wellness_postgres
```

**Permission denied:**
```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Windows: Run as Administrator
```

### Reset Everything
```bash
# Stop and remove all containers
docker stop ai_wellness_postgres
docker rm ai_wellness_postgres

# Remove volumes (deletes data)
docker volume prune

# Remove images (optional)
docker image prune

# Start fresh
python start_docker_postgres.py
```

## 📊 Performance Tuning

### PostgreSQL Configuration
```bash
# Connect to container
docker exec -it ai_wellness_postgres psql -U postgres -d ai_wellness_vision

# Check current settings
SHOW all;

# Optimize for development
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
```

### Container Resources
```bash
# Run with resource limits
docker run -d --name ai_wellness_postgres \
  --memory=1g \
  --cpus=1.0 \
  -e POSTGRES_DB=ai_wellness_vision \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine
```

## 🎉 Success!

Once setup is complete, you'll have:

- ✅ PostgreSQL running in Docker
- ✅ Database schema created
- ✅ Default users configured
- ✅ API server ready to start
- ✅ Management scripts created
- ✅ Testing scripts available

### Next Steps:
1. Test the setup: `python test_postgres_auth.py`
2. Start API server: `python main_api_server_postgres.py`
3. Configure Flutter app to use the API
4. Deploy to production when ready

Your AI Wellness Vision app is now ready with Docker PostgreSQL! 🚀