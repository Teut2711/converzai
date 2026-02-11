---
name: docker-setup
description: Creates complete Docker Compose setup with Dockerfile, entrypoint.sh, and docker-compose.yml with customizable arguments
---

# Docker Compose Setup Skill

## Usage

This skill creates a complete Docker Compose project structure with Dockerfile, entrypoint script, and docker-compose.yml. Perfect for containerizing applications quickly.

### Arguments
- `project_name` (optional): Name of the project (default: "my-app")
- `service_type` (optional): Type of service (any Docker Hub image name)
- `app_port` (optional): Port for the application (auto-detected or defaults to 8080)
- `base_image` (optional): Base Docker image (defaults to service_type with latest tag)
- `service_name` (optional): Docker service name (default: derived from project_name)
- `environment` (optional): Environment variables (auto-detected from image documentation)
- `volumes` (optional): Volume mappings (auto-detected based on service type)

### Intelligent Service Detection

The skill uses multiple strategies to determine optimal configurations:

#### 1. Common Service Recognition
Recognizes popular services and their standard configurations:
- **Web Frameworks**: fastapi, django, flask, express, spring, rails
- **Frontend**: react, vue, angular, next, nuxt
- **Databases**: postgres, mysql, redis, mongodb, elasticsearch
- **Infrastructure**: nginx, apache, haproxy, traefik
- **Message Queues**: rabbitmq, kafka, nats
- **Caching**: redis, memcached

#### 2. Docker Hub Intelligence
- Fetches image metadata from Docker Hub
- Reads EXPOSE instructions from Dockerfile
- Analyzes image documentation for default ports
- Detects official vs community images

#### 3. Heuristic Analysis
- Analyzes image names for patterns (e.g., `-alpine`, `-slim`, `-buster`)
- Detects language-specific images (python, node, java, go)
- Identifies database images by common naming conventions

#### 4. Smart Defaults
When service is unknown:
- **Port**: 8080 (common for web apps)
- **Base Image**: `{service_type}:latest`
- **User**: `appuser` (for security)
- **Workdir**: `/app`

### Dynamic Examples
```
# Any Docker Hub image - skill auto-detects
@docker-setup create project_name="my-app" service_type="redis"
# → Detects port 6379, uses redis:latest

@docker-setup create project_name="api" service_type="tiangolo/uvicorn"
# → Detects Python web server, port 8000

@docker-setup create project_name="db" service_type="postgres:15-alpine"
# → Uses specified image, detects port 5432

@docker-setup create project_name="custom" service_type="myorg/myservice:2.1"
# → Falls back to defaults, port 8080

# Override auto-detection
@docker-setup create project_name="custom-redis" service_type="redis" app_port="6380"
```

## Generated Structure

```
{project_name}/
├── Dockerfile
├── entrypoint.sh
├── docker-compose.yml
├── .dockerignore
└── requirements.txt (if Python)
```

## Files Created

### Dynamic Dockerfile Generation

The skill generates Dockerfiles based on intelligent analysis of the service type:

#### Language Detection & Optimization
```dockerfile
# Auto-generated based on {base_image} analysis
FROM {base_image}

# Smart working directory detection
WORKDIR {workdir}

# Language-specific dependency installation
{dependency_installation}

# Security best practices
{security_setup}

# Copy application code
COPY . .

# Service-specific entrypoint
{entrypoint_setup}
```

#### Service-Specific Templates

**Python Services** (detected by "python" in image name):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

**Node.js Services** (detected by "node" in image name):
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
CMD ["npm", "start"]
```

**Database Services** (detected by database patterns):
```dockerfile
FROM {base_image}
# Database-specific configuration
{database_config}
```

**Unknown/Custom Services**:
```dockerfile
FROM {base_image}
WORKDIR /app
COPY . .
# Generic entrypoint - user can customize
CMD ["/bin/sh", "-c", "echo 'Custom service - please update CMD in Dockerfile'"]
```

### Intelligent Environment Variables

The skill auto-detects common environment variables:

#### Database Services
```yaml
environment:
  POSTGRES_DB: {project_name}
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: password
  # MySQL
  MYSQL_DATABASE: {project_name}
  MYSQL_USER: app
  MYSQL_PASSWORD: password
  # Redis
  REDIS_PASSWORD: password
```

#### Web Services
```yaml
environment:
  PORT: {app_port}
  HOST: 0.0.0.0
  DEBUG: "true"
  # Python-specific
  PYTHONPATH: /app
  # Node.js-specific
  NODE_ENV: development
```

### Smart Volume Detection

Based on service type analysis:
```yaml
volumes:
  # Databases - data persistence
  - {project_name}_data:/var/lib/postgresql/data  # PostgreSQL
  - {project_name}_data:/data                     # Redis
  - {project_name}_data:/var/lib/mysql           # MySQL
  
  # Web apps - code mounting for development
  - .:/app
  - /app/__pycache__  # Python
  - /app/node_modules  # Node.js
  
  # Static files
  - static_files:/app/static
```

### entrypoint.sh
```bash
#!/bin/bash
set -e

echo "Starting {project_name}..."

# Wait for database (if needed)
# python manage.py wait_for_db

# Run migrations (if Django/Flask)
# python manage.py migrate

# Collect static files (if Django)
# python manage.py collectstatic --noinput

# Start the application
exec "$@"
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  {service_name}:
    build: .
    ports:
      - "{app_port}:8000"
    environment:
      - DEBUG=1
      - ENVIRONMENT=development
    volumes:
      - .:/app
      - /app/__pycache__
    restart: unless-stopped
    command: python main.py

  # Optional: Add database service
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: {project_name}
  #     POSTGRES_USER: postgres
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
```

### .dockerignore
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.vscode
.idea
```

### requirements.txt (Python)
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

## Usage Examples

### Example 1: Basic Web App
```
@docker-setup create project_name="web-app" app_port="8080"
```
Creates:
- `web-app/` directory
- Port 8080 mapping
- Python 3.11 base image

### Example 2: Node.js Application
```
@docker-setup create project_name="node-api" base_image="node:18-alpine" app_port="3000"
```
Creates:
- `node-api/` directory
- Node.js 18 Alpine image
- Port 3000 mapping

### Example 3: Production Setup
```
@docker-setup create project_name="prod-app" environment="production" volumes="static_data:/app/static"
```
Creates:
- Production environment variables
- Persistent volume for static files

## Commands After Setup

### Build and Run
```bash
cd {project_name}
docker-compose up --build
```

### Run in Background
```bash
docker-compose up -d --build
```

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Clean Up
```bash
docker-compose down -v --remove-orphans
```

## Customization Options

### Environment Variables
Add to docker-compose.yml:
```yaml
environment:
  - DATABASE_URL=postgresql://user:pass@db:5432/dbname
  - SECRET_KEY=your-secret-key
  - REDIS_URL=redis://redis:6379
```

### Additional Services
Uncomment and customize:
- PostgreSQL database
- Redis cache
- Nginx reverse proxy
- Worker services

### Volume Types
- **Bind Mount**: `./local:/container` (development)
- **Named Volume**: `data:/container` (production)
- **Tmpfs**: `tmpfs:/tmp` (temporary files)

## Best Practices

1. **Use .dockerignore** to exclude unnecessary files
2. **Multi-stage builds** for production images
3. **Health checks** for container monitoring
4. **Resource limits** for production
5. **Security scanning** of images

## Advanced Features

### Multi-Stage Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["npm", "start"]
```

### Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```
