# E-commerce API

A simple e-commerce REST API built with FastAPI, MySQL, and Elasticsearch, using data from dummyjson.com.

## Architecture

- **FastAPI**: Modern Python web framework for the REST API
- **MySQL**: Primary relational database for structured data
- **Elasticsearch**: Full-text search and analytics engine
- **Logstash**: Data processing and ETL pipeline
- **Kibana**: Data visualization and dashboarding
- **Docker Compose**: Container orchestration

## Features

- ✅ RESTful API endpoints
- ✅ Full-text search with Elasticsearch
- ✅ Category-based filtering
- ✅ Product CRUD operations
- ✅ Data ingestion from dummyjson.com
- ✅ Dockerized setup
- ✅ Pythonic design following SOLID principles

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd ecommerce-api
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Wait for services to be ready** (this may take a few minutes):
   - API: http://localhost:8000
   - MySQL: localhost:3306
   - Elasticsearch: http://localhost:9200
   - Kibana: http://localhost:5601

4. **Ingest sample data:**
   ```bash
   docker-compose exec api python scripts/ingest_data.py 100
   ```

### Local Development

1. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (Linux/Mac)
   source venv/bin/activate
   ```

2. **Install project dependencies:**
   ```bash
   # Install from requirements.txt
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Elasticsearch URLs
   ```

4. **Initialize database:**
   ```bash
   # Generate Tortoise ORM schemas (first time only)
   python -c "import asyncio; from app.database.database import init_db; asyncio.run(init_db())"
   ```

5. **Ingest sample data:**
   ```bash
   python scripts/ingest_data.py 100
   ```

6. **Start the API:**
   ```bash
   # Development server with auto-reload
   uvicorn main:app --reload
   
   # Production server
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Categories
- `GET /categories` - List all categories

### Products
- `GET /products` - List all products
- `GET /products/{id}` - Get product by ID
- `GET /products/search?query={query}` - Full-text search
- `GET /products?category={category}` - Filter by category

### Health
- `GET /health` - Health check

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Data Ingestion

The system can automatically ingest product data from dummyjson.com:

```bash
# Ingest 100 products
python scripts/ingest_data.py 100

# Ingest 500 products
python scripts/ingest_data.py 500
```

The ingestion script:
1. Fetches categories and products from dummyjson.com
2. Creates categories in MySQL
3. Creates products with proper relationships
4. Handles duplicate detection

## Kibana Dashboard

Access Kibana at http://localhost:5601 to:
- Visualize product data
- Create custom dashboards
- Monitor search analytics
- Debug Elasticsearch queries

### Setting up Kibana

1. Open http://localhost:5601
2. Go to **Stack Management > Index Patterns**
3. Create index pattern: `products-*`
4. Select time field: `created_at`
5. Go to **Discover** to explore data

## Project Structure

```
ecommerce-api/
├── api/                          # FastAPI application
│   └── Dockerfile              # API container build
├── ingest/                        # Data ingestion service
│   └── Dockerfile              # Ingestion container build
├── frontend/                      # Frontend application (placeholder)
│   └── Dockerfile              # Frontend container build
├── app/                          # Application code
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py           # Category models
│   │   └── product.py            # Product models
│   └── services/
│       ├── __init__.py
│       ├── category_service.py   # Category business logic
│       ├── product_service.py    # Product business logic
│       └── search_service.py     # Elasticsearch integration
├── infrastructure/               # External services configuration
│   ├── kibana/
│   │   └── kibana.yml           # Kibana configuration
│   └── logstash/
│       ├── logstash.yml         # Logstash configuration
│       └── config/
│           └── pipeline.conf    # ETL pipeline
├── scripts/                      # Utility scripts
│   └── ingest_data.py           # Data ingestion script
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # All services orchestration
├── init.sql                      # Database initialization
└── .env                         # Environment variables
```

### Microservices Architecture

Each component has its own Dockerfile:
- **`api/`** - FastAPI web service
- **`ingest/`** - Data ingestion service  
- **`frontend/`** - Frontend application (placeholder)
- **`infrastructure/`** - External service configs (Kibana, Logstash)

## Design Principles

This project follows Pythonic design principles:

- **Single Responsibility**: Each service has one clear purpose
- **Open/Closed**: Extensible through protocols and duck typing
- **Liskov Substitution**: Interchangeable components
- **Interface Segregation**: Small, focused protocols
- **Dependency Inversion**: Depend on abstractions, not concretions

See `AGENT.md` for detailed guidelines.

## Development

### Adding New Endpoints

1. Define Pydantic models in `app/models/`
2. Create service logic in `app/services/`
3. Add routes in `main.py`
4. Write tests

### Running Tests

#### Quick Test Commands

```bash
# Run all tests locally (SQLite)
python run_tests.py

# Run tests with Docker (MySQL + Elasticsearch)
docker-compose --profile test up --build --abort-on-container-exit

# Run unit tests only
python run_tests.py unit

# Run integration tests only
python run_tests.py integration
```

#### Detailed Testing Options

**Local Testing (SQLite)**
```bash
cd api
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
```

**Docker Testing (Full Stack)**
```bash
# Start test services
docker-compose --profile test up --build

# View test results
docker-compose logs api-test

# Clean up
docker-compose --profile test down -v
```

**Test Categories**
- **Unit Tests**: Test individual services and models with mocked dependencies
- **Integration Tests**: Test database models and relationships
- **API Tests**: Test HTTP endpoints and request/response handling

**Coverage Report**
- HTML coverage report generated in `api/htmlcov/`
- Minimum coverage requirement: 80%

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Monitoring

### Logs

View logs for all services:
```bash
docker-compose logs -f
```

View logs for specific service:
```bash
docker-compose logs -f api
docker-compose logs -f elasticsearch
```

### Health Checks

- API Health: http://localhost:8000/health
- Elasticsearch: http://localhost:9200/_cluster/health
- Kibana: http://localhost:5601/api/status

## Troubleshooting

### Common Issues

1. **MySQL connection error**: Wait for MySQL container to fully start
2. **Elasticsearch not ready**: Check Elasticsearch logs, ensure sufficient memory
3. **Port conflicts**: Ensure ports 8000, 3306, 9200, 5601 are available

### Reset Environment

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Restart
docker-compose up --build
```

## Performance

### Optimization Tips

1. Use Elasticsearch for search queries
2. Implement caching for frequently accessed data
3. Use database connection pooling
4. Enable gzip compression in production
5. Monitor resource usage in Kibana

## Contributing

1. Follow Pythonic design principles (see AGENT.md)
2. Write tests for new features
3. Update documentation
4. Use proper git commit messages

## License

This project is for educational purposes.
