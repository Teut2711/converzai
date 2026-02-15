# Converzai E-commerce API

A modern, scalable e-commerce REST API built with FastAPI, featuring MySQL database integration, Elasticsearch search capabilities, and intelligent data caching.

## 🚀 Features

- **FastAPI Framework** - High-performance async web framework
- **MySQL Database** - Persistent data storage with Tortoise ORM
- **Elasticsearch Integration** - Advanced product search and filtering
- **Intelligent Caching** - API response caching to prevent rate limiting
- **Docker Compose** - Complete containerized deployment
- **Comprehensive Testing** - Unit and integration tests with pytest
- **RESTful API Design** - Clean, well-documented endpoints
- **Pydantic Validation** - Robust data validation and serialization

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

## 🛠️ Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd converzai
   ```

2. **Start all services**
   ```bash
   docker compose up --force-recreate
   ```

3. **Verify services are running**
   ```bash
   docker compose ps
   ```

4. **Access the API**
   - API: http://localhost:8100
   - API Documentation: http://localhost:8100/docs
   - Kibana Dashboard: http://localhost:5601
   - Elasticsearch: http://localhost:9200

### Local Development

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp ../.env.example .env
   # Edit .env with your configuration
   ```

3. **Start the API server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📚 API Documentation

### Base URL
```
http://localhost:8100/api/v1
```

### Endpoints

#### Products
- `GET /products` - Get all products (supports `limit` and `offset` query params)
- `GET /products/{id}` - Get product by ID
- `GET /products/search` - Search products (supports `query`, `category`, `use_wildcard` params)
- `GET /products?category={category}` - Filter products by category (supports `limit`, `offset`, `category` params)

#### Categories
- `GET /categories` - Get all categories

#### System
- `GET /` - Root endpoint
- `GET /health` - Health check

### Example Requests

```bash
# Get all products
curl http://localhost:8100/api/v1/products

# Get product by ID
curl http://localhost:8100/api/v1/products/1

# Search products
curl "http://localhost:8100/api/v1/products/search?query=groceries"

# Filter by category
curl "http://localhost:8100/api/v1/products?category=womens-shoes"

# Pagination
curl "http://localhost:8100/api/v1/products?limit=5&offset=0"
```

## 🏗️ Architecture

### Project Structure
```
converzai/
├── backend/
│   ├── app/
│   │   ├── controllers/     # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic models
│   │   ├── connectors/      # Database/ES connections
│   │   ├── utils/           # Utilities
│   │   └── tests/           # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── mysql/
├── elasticsearch/
└── kibana/
```

### Key Components

#### Data Flow
1. **External API** → **DataFetchService** (with caching)
2. **DataFetchService** → **DatabaseService** → **MySQL**
3. **DatabaseService** → **IndexingService** → **Elasticsearch**
4. **Controllers** → **SearchService** → **Elasticsearch**

#### Services
- **DataFetchService** - Fetches and caches product data
- **DatabaseService** - Database operations with Tortoise ORM
- **SearchService** - Elasticsearch search operations
- **IndexingService** - Bulk data indexing
- **DataIngestionService** - Seed data loading

## 🧪 Testing

### Run Tests
```bash
# From backend directory
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_api.py
```

### Test Configuration
- Located in `backend/pytest.ini`
- Coverage target: 80%
- Async test support with pytest-asyncio

## ⚙️ Configuration

### Environment Variables
Key environment variables (see `.env`):

```env
# Database
DB_DATABASE=ecommerce
DB_USER=app_user
DB_PASSWORD=app_password
DB_HOST=mysql
DB_PORT=3306

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200
ELASTICSEARCH_INDEX_NAME=products

# API
PRODUCT_API_URL=https://dummyjson.com/products
PRODUCT_API_URL_LIMIT=100

# Application
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key
```

## 🔧 Development

### Adding New Endpoints
1. Create controller in `app/controllers/v1/`
2. Add router to `app/controllers/v1/__init__.py`
3. Implement business logic in services
4. Add tests in `app/tests/`

### Database Migrations
```bash
# Generate migration (if using aerich)
aerich init -t app.TORTOISE_ORM
aerich migrate --name="migration_name"
aerich upgrade
```

### Caching
- Cache directory: `app/cached_data/`
- Cache files: `{URL_HASH}.json`
- Automatic cache-first loading
- Fallback to API on cache miss

## 🐳 Docker Services

### Services Overview
- **mysql**: MySQL 8.0 database
- **elasticsearch**: Elasticsearch 9.3.0 for search
- **kibana**: Elasticsearch visualization dashboard
- **backend**: FastAPI application

### Service Health Checks
All services include health checks:
- MySQL: `mysqladmin ping`
- Elasticsearch: `curl -f http://localhost:9200/_cluster/health`
- Kibana: `curl -f http://localhost:5601/api/status`

## 📊 Monitoring

### Kibana Dashboard
Access at http://localhost:5601
- Visualize search analytics
- Monitor index performance
- Query Elasticsearch data

### Logs
```bash
# View application logs
docker compose logs backend

# View all services
docker compose logs -f

# Specific service
docker compose logs mysql
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check MySQL container
docker compose logs mysql

# Restart services
docker compose restart mysql backend
```

#### Elasticsearch Connection Issues
```bash
# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Restart Elasticsearch
docker compose restart elasticsearch
```

#### Test Failures
```bash
# Clean test environment
docker compose down -v
docker compose up -d
# Wait for services to be healthy
pytest
```

### Port Conflicts
Default ports:
- API: 8100
- MySQL: 3306
- Elasticsearch: 9200, 9300
- Kibana: 5601

Modify in `docker-compose.yml` if needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tortoise ORM](https://tortoise.github.io/)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)
- [Docker Compose](https://docs.docker.com/compose/)

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check existing documentation
- Review test cases for usage examples
