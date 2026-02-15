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

## 📐 Data Models (UML)

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────┐
│    Product     │◄──────┤  ProductDimensions  │
├─────────────────┤ 1:1   ├─────────────────────┤
│ - id (PK)      │       │ - id (PK)          │
│ - title         │       │ - width             │
│ - description   │       │ - height            │
│ - price         │       │ - depth             │
│ - discount_%    │       └─────────────────────┘
│ - rating        │
│ - stock         │       ┌─────────────────────┐
│ - sku          │◄──────┤   ProductImage     │
│ - weight        │ 1:N   ├─────────────────────┤
│ - warranty     │       │ - id (PK)          │
│ - shipping     │       │ - image_url         │
│ - availability │       └─────────────────────┘
│ - return_policy │
│ - min_order    │       ┌─────────────────────┐
│ - category     │◄──────┤   ProductReview    │
│ - brand        │ 1:N   ├─────────────────────┤
│ - thumbnail    │       │ - id (PK)          │
│ - barcode      │       │ - rating            │
│ - qr_code      │       │ - comment           │
└─────────────────┘       │ - reviewer_name     │
        │                │ - reviewer_email    │
        │                │ - review_date       │
        │                └─────────────────────┘
        │
        │                ┌─────────────────────┐
        └───────────────┤    ProductTag      │
          N:M           ├─────────────────────┤
                        │ - id (PK)          │
                        │ - name             │
                        └─────────────────────┘
```

### Model Details

#### Product (Main Entity)
- **Primary Key**: `id` (Integer)
- **Core Fields**: `title`, `description`, `price`, `rating`, `stock`
- **Business Fields**: `sku`, `category`, `brand`, `thumbnail`
- **Metadata**: `discount_percentage`, `warranty_information`, `shipping_information`
- **Constraints**: `barcode` (unique), `sku` (unique, indexed)

#### ProductDimensions (One-to-One)
- **Purpose**: Physical product measurements
- **Fields**: `width`, `height`, `depth` (Float)
- **Relationship**: One-to-one with Product

#### ProductImage (One-to-Many)
- **Purpose**: Product gallery images
- **Fields**: `image_url` (String, max 500 chars)
- **Relationship**: Many images per Product

#### ProductReview (One-to-Many)
- **Purpose**: Customer reviews and ratings
- **Fields**: `rating`, `comment`, `reviewer_name`, `reviewer_email`, `review_date`
- **Relationship**: Many reviews per Product
- **Index**: Composite index on (`product_id`, `rating`)

#### ProductTag (Many-to-Many)
- **Purpose**: Product categorization and tagging
- **Fields**: `name` (String, unique, max 50 chars)
- **Relationship**: Many-to-many with Products via junction table

### TimestampMixin
All models inherit from `TimestampMixin` providing:
- `created_at` - Auto-generated timestamp
- `updated_at` - Auto-updated timestamp

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


## 📊 Monitoring

### Kibana Dashboard
Access at http://localhost:5601
- Visualize search analytics
- Monitor index performance
- Query Elasticsearch data


 

### Port Conflicts
Default ports:
- API: 8100
- MySQL: 3306
- Elasticsearch: 9200
- Kibana: 5601

Modify in `docker-compose.yml` if needed.
 