# E-Commerce REST API Design Document

## SOLID Principles in Design

### Applying SOLID Principles

This e-commerce API design adheres to SOLID principles to ensure maintainable, scalable, and robust architecture:

#### 1. Single Responsibility Principle (SRP)
- **Service Separation**: Each service handles one responsibility
  - `ProductService`: Product CRUD operations
  - `CategoryService`: Category management
  - `SearchService`: Elasticsearch operations
  - `DataIngestionService`: ETL pipeline
- **Controller Separation**: Each endpoint handles specific functionality
  - `ProductController`: Product-related endpoints
  - `CategoryController`: Category endpoints
  - `SearchController`: Search and filtering

#### 2. Open/Closed Principle (OCP)
- **Abstract Base Classes**: Extensible database models and services
- **Plugin Architecture**: Easy addition of new search providers
- **Strategy Pattern**: Configurable indexing strategies
- **Interface Segregation**: Specific interfaces for different operations

#### 3. Liskov Substitution Principle (LSP)
- **Database Abstractions**: Interchangeable database implementations
- **Search Providers**: Swappable search engines (Elasticsearch, Algolia, etc.)
- **Cache Implementations**: Multiple caching strategies supported

#### 4. Interface Segregation Principle (ISP)
- **Focused Interfaces**: Small, specific interfaces
  - `IProductRepository`: Product data access
  - `ISearchProvider`: Search functionality
  - `IDataProcessor`: ETL operations
- **Client-Specific**: No forced implementation of unused methods

#### 5. Dependency Inversion Principle (DIP)
- **Dependency Injection**: FastAPI's dependency injection system
- **Abstract Dependencies**: Services depend on abstractions, not concretions
- **Configuration**: External dependencies injected through environment

### Skills Integration with SOLID Principles

When using AI skills, maintain SOLID principles through these guidelines:

#### Docker Setup Skill Usage
```bash
# Create modular, single-responsibility services
@docker-setup create project_name="products-service" service_type="fastapi"
@docker-setup create project_name="search-service" service_type="elasticsearch"
@docker-setup create project_name="categories-service" service_type="fastapi"

# Each service handles one responsibility
# - products-service: Product CRUD only
# - search-service: Search functionality only  
# - categories-service: Category management only
```

#### Python Environment Skill Usage
```bash
# Create isolated environments for each service
@python-venv create venv_name="products-service" python_version="3.11"
@python-venv create venv_name="search-service" python_version="3.11"
@python-venv create venv_name="categories-service" python_version="3.11"

# Install only required dependencies per service
@python-venv install packages="fastapi, sqlalchemy, pymysql"  # products-service
@python-venv install packages="elasticsearch, fastapi"          # search-service
```

## Quick Start with Skills

### Using Docker Setup Skill for Complete ELK Stack

Instead of manually creating all these Docker configurations, use the **docker-setup skill** to generate the complete e-commerce stack automatically:

```bash
# Generate complete ELK stack with FastAPI
@docker-setup create project_name="ecommerce-api" service_type="fastapi"

# This single command creates:
# - Complete docker-compose.yml with MySQL, Elasticsearch, Logstash, Kibana, FastAPI
# - Optimized Dockerfile for FastAPI with Python 3.11
# - Proper entrypoint.sh for container startup
# - .dockerignore for optimized builds
# - requirements.txt with all dependencies
# - Environment configuration files
# - Logstash pipeline configuration
# - Kibana connection settings
```

#### Skill Benefits Over Manual Setup
- **Time Saving**: Reduces setup from hours to minutes
- **Best Practices**: Automatically applies security and optimization patterns
- **Consistency**: Ensures all services use compatible configurations
- **Version Alignment**: Automatically matches versions across all services
- **Error Prevention**: Avoids common configuration mistakes

#### Generated Structure
```
ecommerce-api/
├── docker-compose.yml         # Complete ELK stack + FastAPI
├── Dockerfile                 # Optimized multi-stage build
├── entrypoint.sh            # Container startup script
├── .dockerignore           # Build optimization
├── requirements.txt        # All dependencies
├── .env                    # Environment variables
├── logstash/
│   ├── config/
│   │   └── pipeline.conf    # ETL pipeline
│   └── logstash.yml          # Logstash settings
└── kibana/
    └── kibana.yml            # Kibana configuration
```

#### Manual Customization After Skill Generation
```bash
# After skill generates the base setup, you can customize:

# 1. Modify environment variables
# Edit .env file for your specific settings
DATABASE_URL=mysql://user:password@localhost:3306/your_db
ELASTICSEARCH_URL=http://localhost:9200

# 2. Adjust resource limits
# Edit docker-compose.yml for memory/CPU allocation
environment:
  ES_JAVA_OPTS: "-Xms1g -Xmx1g"  # Increase ES memory

# 3. Add custom Logstash filters
# Edit logstash/config/pipeline.conf for your data transformation needs

# 4. Customize Kibana dashboards
# Access http://localhost:5601 to create custom dashboards
```

### Using Python Virtual Environment Skill

For local development of the API service:

```bash
# Create development environment
@python-venv create venv_name="ecommerce-dev" python_version="3.11"

# Install dependencies with smart typo detection
@python-venv install packages="fastapi, uvicorn, sqlalchemy, pymysql, elasticsearch, pydantic, requests"

# The skill will:
# - Detect and correct any typos (e.g., "sqlachemy" → "sqlalchemy")
# - Validate packages exist on PyPI
# - Install with proper versions
# - Create requirements.txt automatically
```

## Project Overview

This document outlines the design and architecture for a simple e-commerce REST API built with modern AI-assisted development tools. The system demonstrates backend architecture, data modeling, database design, Elasticsearch integration, and API design principles.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │    │   MySQL DB      │    │   Logstash      │    │  Elasticsearch  │    │     Kibana      │
│   (FastAPI)     │◄──►│   (Products)    │◄──►│  (Processing)   │◄──►│   (Search)      │◄──►│  (Visualization)│
│                 │    │                 │    │                 │    │                 │    │                 │
│ /products       │    │ - products      │    │ - Data Pipeline  │    │ - products_idx  │    │ - Dashboards    │
│ /categories     │    │ - categories    │    │ - Transforms     │    │ - search mappings│    │ - Dev Tools     │
│ /search         │    │ - product_cats  │    │ - Enrichment     │    │                 │    │ - Index Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │                       │
         └───────────────────────┼───────────────────────┼───────────────────────┼───────────────────────┘
                                 │                       │                       │
                    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                    │  Docker Compose │    │                 │    │                 │
                    │   Orchestration │    │                 │    │                 │
                    │                 │    │                 │    │                 │
                    │ - API Service   │    │ - Logstash Pipe  │    │ - Kibana UI     │
                    │ - MySQL         │    │ - Data Transforms│    │ - Index Analysis│
                    │ - Elasticsearch │    │ - ETL Processing │    │ - Query Builder │
                    │ - Kibana       │    │                 │    │                 │
                    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Backend Framework
- **FastAPI**: Modern, fast Python web framework
- **Python 3.11**: Latest stable Python version
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: ORM for database operations
- **Elasticsearch-py**: Python client for Elasticsearch

#### Database & Search
- **MySQL 8.0**: Primary relational database
- **Elasticsearch 8.x**: Full-text search and analytics
- **Logstash 8.x**: Data processing and ETL pipeline
- **Kibana 8.x**: Data visualization and dashboarding for Elasticsearch
- **Redis**: Optional caching layer (future enhancement)

#### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration
- **Dockerize**: Multi-stage builds for optimization
- **Nginx**: Reverse proxy (future enhancement)

### Logstash Integration

#### Logstash Configuration Files

**logstash/logstash.yml**:
```yaml
http.host: "0.0.0.0"
xpack.monitoring.elasticsearch.hosts: [ "http://elasticsearch:9200" ]
path.config: /usr/share/logstash/pipeline
pipeline.workers: 2
pipeline.batch.size: 125
pipeline.batch.delay: 50
```

**logstash/config/pipeline.conf**:
```ruby
input {
  jdbc {
    jdbc_driver_library => "/usr/share/logstash/mysql-connector-java.jar"
    jdbc_driver_class => "com.mysql.cj.jdbc.Driver"
    jdbc_connection_string => "jdbc:mysql://mysql:3306/ecommerce"
    jdbc_user => "app_user"
    jdbc_password => "app_password"
    schedule => "* * * * *"
    statement => "SELECT p.*, c.name as category_name FROM products p LEFT JOIN product_categories pc ON p.id = pc.product_id LEFT JOIN categories c ON pc.category_id = c.id WHERE p.updated_at > :sql_last_value"
    use_column_value => true
    tracking_column => "updated_at"
    tracking_column_type => "timestamp"
    last_run_metadata_path => "/usr/share/logstash/last_run_metadata"
  }
  
  http {
    port => 8080
    codec => json
  }
}

filter {
  # Parse product data
  if [category_name] {
    mutate {
      add_field => { "categories" => "%{category_name}" }
    }
  }
  
  # Calculate final price
  if [discount_percentage] and [price] {
    ruby {
      code => "
        discount = event.get('discount_percentage').to_f
        price = event.get('price').to_f
        final_price = price * (1 - discount / 100)
        event.set('final_price', final_price.round(2))
      "
    }
  }
  
  # Parse tags if they exist
  if [tags] {
    split {
      field => "tags"
    }
  }
  
  # Add processing timestamp
  mutate {
    add_field => { "[@metadata][processed_at]" => "%{+yyyy-MM-dd'T'HH:mm:ss.SSSZ}" }
  }
  
  # Remove sensitive fields
  mutate {
    remove_field => [ "jdbc_fetch_columns", "jdbc_page_size" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "products-%{+YYYY.MM.dd}"
    document_id => "%{id}"
    template_name => "products"
    template_pattern => "products-*"
    template => {
      "index_patterns" => ["products-*"],
      "settings" => {
        "number_of_shards" => 1,
        "number_of_replicas" => 0
      },
      "mappings" => {
        "properties" => {
          "id" => { "type" => "integer" },
          "title" => { 
            "type" => "text",
            "fields" => {
              "keyword" => { "type" => "keyword" }
            }
          },
          "description" => { "type" => "text" },
          "price" => { "type" => "double" },
          "final_price" => { "type" => "double" },
          "discount_percentage" => { "type" => "double" },
          "rating" => { "type" => "double" },
          "brand" => { 
            "type" => "text",
            "fields" => {
              "keyword" => { "type" => "keyword" }
            }
          },
          "categories" => { "type" => "keyword" },
          "tags" => { "type" => "keyword" },
          "availability_status" => { "type" => "keyword" },
          "created_at" => { "type" => "date" },
          "updated_at" => { "type" => "date" }
        }
      }
    }
  }
  
  # Debug output (remove in production)
  stdout {
    codec => rubydebug
  }
}
```

#### Logstash Features for E-Commerce
- **Data Synchronization**: Real-time MySQL to Elasticsearch sync
- **Data Transformation**: Price calculations, field mapping, enrichment
- **ETL Processing**: Extract, Transform, Load pipeline automation
- **Change Data Capture**: Incremental updates based on timestamps
- **HTTP Input**: Direct API ingestion for real-time updates

#### Logstash Use Cases
```bash
# Monitor Logstash processing
docker logs ecommerce_logstash -f

# Send data directly to Logstash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "id": 999,
    "title": "New Product",
    "price": 299.99,
    "category": "electronics"
  }'

# Check pipeline status
curl http://localhost:9600/_node/stats/pipelines
```

### Kibana Integration

#### Kibana Features for E-Commerce
- **Index Management**: Visual inspection of products index structure
- **Dev Tools**: Query builder and testing Elasticsearch queries
- **Dashboards**: Custom analytics dashboards for product insights
- **Discover**: Real-time search and filtering of product data
- **Visualizations**: Charts and graphs for product analytics

#### Access Points
- **Kibana UI**: http://localhost:5601
- **Dev Tools**: Direct query interface for testing search functionality
- **Index Patterns**: Define `products*` pattern for product data
- **Dashboard Templates**: Pre-built visualizations for common e-commerce metrics

#### Example Kibana Use Cases
```bash
# Access Kibana after docker-compose up
open http://localhost:5601

# Create index pattern in Kibana:
# Pattern: products*
# Time field: created_at

# Sample queries in Dev Tools:
GET products/_search
{
  "query": {
    "match": {
      "title": "wireless headphones"
    }
  },
  "aggs": {
    "categories": {
      "terms": {
        "field": "categories.name.keyword"
      }
    },
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          {"to": 50, "key": "Budget"},
          {"from": 50, "to": 200, "key": "Mid-range"},
          {"from": 200, "key": "Premium"}
        ]
      }
    }
  }
}
```

## Data Modeling

### MySQL Schema Design

#### Core Tables

```sql
-- Categories table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_slug (slug)
);

-- Products table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    discount_percentage DECIMAL(5, 2) DEFAULT 0.00,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    stock INT DEFAULT 0,
    brand VARCHAR(100),
    sku VARCHAR(100) UNIQUE,
    weight DECIMAL(8, 2),
    dimensions_width DECIMAL(8, 2),
    dimensions_height DECIMAL(8, 2),
    dimensions_depth DECIMAL(8, 2),
    warranty_information VARCHAR(255),
    shipping_information VARCHAR(255),
    availability_status ENUM('in_stock', 'out_of_stock', 'limited') DEFAULT 'in_stock',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_title (title),
    INDEX idx_brand (brand),
    INDEX idx_price (price),
    INDEX idx_rating (rating),
    INDEX idx_availability (availability_status)
);

-- Product-Category relationship (many-to-many)
CREATE TABLE product_categories (
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Product images
CREATE TABLE product_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_primary (product_id, is_primary)
);

-- Product tags
CREATE TABLE product_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    tag VARCHAR(50) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_tag (product_id, tag),
    INDEX idx_tag (tag)
);
```

#### Design Rationale

1. **Normalization**: Proper normalization to reduce data redundancy
2. **Indexing Strategy**: Strategic indexes for common query patterns
3. **Scalability**: Design supports future growth and features
4. **Data Integrity**: Foreign keys and constraints ensure consistency

### Elasticsearch Mapping

#### Products Index Mapping

```json
{
  "mappings": {
    "properties": {
      "id": {"type": "integer"},
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {"type": "keyword"},
          "suggest": {"type": "completion"}
        }
      },
      "description": {
        "type": "text",
        "analyzer": "english"
      },
      "price": {"type": "double"},
      "discount_percentage": {"type": "double"},
      "rating": {"type": "double"},
      "brand": {
        "type": "text",
        "fields": {"keyword": {"type": "keyword"}}
      },
      "categories": {
        "type": "nested",
        "properties": {
          "id": {"type": "integer"},
          "name": {
            "type": "text",
            "fields": {"keyword": {"type": "keyword"}}
          },
          "slug": {"type": "keyword"}
        }
      },
      "tags": {"type": "keyword"},
      "availability_status": {"type": "keyword"},
      "images": {
        "type": "nested",
        "properties": {
          "url": {"type": "keyword"},
          "alt_text": {"type": "text"},
          "is_primary": {"type": "boolean"}
        }
      },
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "product_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  }
}
```

## API Design

### RESTful Endpoints

#### Categories Endpoints

```http
GET /api/v1/categories
Content-Type: application/json

Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices and gadgets",
      "product_count": 150
    }
  ],
  "pagination": {
    "total": 25,
    "page": 1,
    "per_page": 20
  }
}
```

#### Products Endpoints

```http
GET /api/v1/products
Query Parameters:
- page: int (default: 1)
- per_page: int (default: 20, max: 100)
- category: string (category slug)
- min_price: decimal
- max_price: decimal
- brand: string
- sort: string (price_asc, price_desc, rating_desc, created_desc)
- availability: string (in_stock, out_of_stock, limited)

Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Wireless Headphones",
      "description": "High-quality wireless headphones...",
      "price": 99.99,
      "discount_percentage": 10.0,
      "final_price": 89.99,
      "rating": 4.5,
      "stock": 50,
      "brand": "TechBrand",
      "categories": [
        {"id": 1, "name": "Electronics", "slug": "electronics"}
      ],
      "images": [
        {
          "url": "https://example.com/image1.jpg",
          "alt_text": "Wireless headphones",
          "is_primary": true
        }
      ],
      "availability_status": "in_stock",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 500,
    "page": 1,
    "per_page": 20,
    "total_pages": 25
  },
  "filters": {
    "categories": ["electronics", "clothing"],
    "brands": ["TechBrand", "FashionBrand"],
    "price_range": {"min": 10.0, "max": 1000.0}
  }
}
```

```http
GET /api/v1/products/{id}
Content-Type: application/json

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Wireless Headphones",
    "description": "Detailed product description...",
    "price": 99.99,
    "discount_percentage": 10.0,
    "final_price": 89.99,
    "rating": 4.5,
    "stock": 50,
    "brand": "TechBrand",
    "sku": "WH-001",
    "weight": 0.5,
    "dimensions": {
      "width": 15.0,
      "height": 20.0,
      "depth": 10.0
    },
    "warranty_information": "2 years manufacturer warranty",
    "shipping_information": "Free shipping on orders over $50",
    "categories": [...],
    "images": [...],
    "tags": ["wireless", "bluetooth", "noise-cancelling"],
    "availability_status": "in_stock",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Search Endpoints

```http
GET /api/v1/products/search
Query Parameters:
- q: string (search query)
- category: string (category slug)
- min_price: decimal
- max_price: decimal
- brand: string
- sort: string (relevance, price_asc, price_desc, rating_desc)
- page: int (default: 1)
- per_page: int (default: 20)

Response:
{
  "success": true,
  "data": [...],
  "pagination": {...},
  "search_meta": {
    "query": "wireless headphones",
    "total_hits": 45,
    "search_time": 0.015,
    "aggregations": {
      "categories": [
        {"key": "electronics", "doc_count": 40},
        {"key": "accessories", "doc_count": 5}
      ],
      "brands": [
        {"key": "TechBrand", "doc_count": 15},
        {"key": "AudioPro", "doc_count": 10}
      ],
      "price_ranges": [
        {"key": "0-50", "doc_count": 10},
        {"key": "50-100", "doc_count": 25},
        {"key": "100-500", "doc_count": 10}
      ]
    }
  }
}
```

## Data Ingestion Pipeline

### Data Fetch Script

```python
# data_ingestion.py
import requests
import mysql.connector
from elasticsearch import Elasticsearch
import json
import logging
from typing import List, Dict

class DataIngestionPipeline:
    def __init__(self, mysql_config: Dict, es_config: Dict):
        self.mysql_conn = mysql.connector.connect(**mysql_config)
        self.es_client = Elasticsearch([es_config['host']])
        self.logger = logging.getLogger(__name__)
    
    def fetch_dummy_data(self) -> Dict:
        """Fetch product data from dummyjson.com"""
        response = requests.get('https://dummyjson.com/products')
        response.raise_for_status()
        return response.json()
    
    def transform_data(self, raw_data: Dict) -> List[Dict]:
        """Transform raw data to match our schema"""
        products = []
        for product in raw_data['products']:
            # Transform categories
            categories = []
            for cat in product.get('category', '').split(','):
                cat_slug = cat.strip().lower().replace(' ', '-')
                categories.append({
                    'name': cat.strip(),
                    'slug': cat_slug
                })
            
            # Transform product
            transformed = {
                'title': product['title'],
                'description': product['description'],
                'price': product['price'],
                'discount_percentage': product.get('discountPercentage', 0),
                'rating': product.get('rating', 0),
                'stock': product.get('stock', 0),
                'brand': product.get('brand'),
                'categories': categories,
                'images': product.get('images', []),
                'tags': product.get('tags', []),
                'availability_status': 'in_stock' if product.get('stock', 0) > 0 else 'out_of_stock'
            }
            products.append(transformed)
        
        return products
    
    def insert_into_mysql(self, products: List[Dict]) -> None:
        """Insert transformed data into MySQL"""
        cursor = self.mysql_conn.cursor()
        
        try:
            # Insert categories
            categories = set()
            for product in products:
                for cat in product['categories']:
                    categories.add((cat['name'], cat['slug']))
            
            cursor.executemany(
                "INSERT IGNORE INTO categories (name, slug) VALUES (%s, %s)",
                list(categories)
            )
            
            # Insert products
            for product in products:
                cursor.execute("""
                    INSERT INTO products (
                        title, description, price, discount_percentage,
                        rating, stock, brand, availability_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    product['title'], product['description'],
                    product['price'], product['discount_percentage'],
                    product['rating'], product['stock'],
                    product['brand'], product['availability_status']
                ))
                
                product_id = cursor.lastrowid
                
                # Link categories
                for cat in product['categories']:
                    cursor.execute("""
                        INSERT INTO product_categories (product_id, category_id)
                        SELECT %s, id FROM categories WHERE slug = %s
                    """, (product_id, cat['slug']))
            
            self.mysql_conn.commit()
            self.logger.info(f"Inserted {len(products)} products into MySQL")
            
        except Exception as e:
            self.mysql_conn.rollback()
            self.logger.error(f"Error inserting into MySQL: {e}")
            raise
        finally:
            cursor.close()
    
    def index_into_elasticsearch(self, products: List[Dict]) -> None:
        """Index products into Elasticsearch"""
        for product in products:
            # Get full product data with IDs from MySQL
            cursor = self.mysql_conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, GROUP_CONCAT(c.name) as category_names
                FROM products p
                LEFT JOIN product_categories pc ON p.id = pc.product_id
                LEFT JOIN categories c ON pc.category_id = c.id
                WHERE p.title = %s
                GROUP BY p.id
            """, (product['title'],))
            
            result = cursor.fetchone()
            if result:
                # Prepare document for Elasticsearch
                doc = {
                    'id': result['id'],
                    'title': result['title'],
                    'description': result['description'],
                    'price': float(result['price']),
                    'discount_percentage': float(result['discount_percentage']),
                    'rating': float(result['rating']),
                    'brand': result['brand'],
                    'categories': product['categories'],
                    'tags': product['tags'],
                    'availability_status': result['availability_status'],
                    'created_at': result['created_at'].isoformat()
                }
                
                # Index document
                self.es_client.index(
                    index='products',
                    id=result['id'],
                    body=doc
                )
            
            cursor.close()
        
        self.logger.info(f"Indexed {len(products)} products into Elasticsearch")
    
    def run_pipeline(self):
        """Run the complete data ingestion pipeline"""
        try:
            # Fetch data
            raw_data = self.fetch_dummy_data()
            self.logger.info(f"Fetched {len(raw_data['products'])} products")
            
            # Transform data
            products = self.transform_data(raw_data)
            self.logger.info(f"Transformed {len(products)} products")
            
            # Insert into MySQL
            self.insert_into_mysql(products)
            
            # Index into Elasticsearch
            self.index_into_elasticsearch(products)
            
            self.logger.info("Data ingestion pipeline completed successfully")
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            raise
        finally:
            self.mysql_conn.close()
```

## Docker Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  # MySQL Database
  mysql:
    image: mysql:8.0
    container_name: ecommerce_mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: ecommerce
      MYSQL_USER: app_user
      MYSQL_PASSWORD: app_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ecommerce_network
    restart: unless-stopped

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: ecommerce_elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - ecommerce_network
    restart: unless-stopped

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: ecommerce_logstash
    volumes:
      - ./logstash/config:/usr/share/logstash/pipeline
      - ./logstash/logstash.yml:/usr/share/logstash/config/logstash.yml
    ports:
      - "5044:5044"
      - "9600:9600"
    depends_on:
      - elasticsearch
    networks:
      - ecommerce_network
    restart: unless-stopped

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: ecommerce_kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - XPACK_SECURITY_ENABLED=false
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - ecommerce_network
    restart: unless-stopped

  # FastAPI Application
  api:
    build: .
    container_name: ecommerce_api
    environment:
      - DATABASE_URL=mysql://app_user:app_password@mysql:3306/ecommerce
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - PYTHONPATH=/app
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - /app/__pycache__
    depends_on:
      - mysql
      - elasticsearch
    networks:
      - ecommerce_network
    restart: unless-stopped
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  mysql_data:
  es_data:

networks:
  ecommerce_network:
    driver: bridge
```

### Dockerfile
Use the skill docker-setup to generate the 

### requirements.txt

```txt
fastapi[standard-no-fastapi-cloud-cli]
tortoise-orm
elasticsearch
pydantic
aiohttp
pydantic-settings
```

## Design Choices & Trade-offs

### Architecture Decisions

1. **FastAPI over Django/FastAPI**: Chosen for performance and automatic OpenAPI documentation
2. **MySQL + Elasticsearch**: Hybrid approach for structured data + full-text search
3. **Docker Compose**: Simplified development and deployment
4. **SQLAlchemy ORM**: Database abstraction and migration support

### Trade-offs

1. **Complexity vs. Performance**: 
   - Pro: Elasticsearch provides powerful search capabilities
   - Con: Additional infrastructure complexity and memory usage

2. **Normalization vs. Query Performance**:
   - Pro: Normalized schema reduces data redundancy
   - Con: Requires JOINs for complex queries

3. **Real-time vs. Batch Indexing**:
   - Pro: Simple batch indexing for demo purposes
   - Con: Not suitable for real-time production updates

### Known Limitations

1. **Authentication**: No user authentication implemented
2. **Caching**: No caching layer implemented
3. **Rate Limiting**: No API rate limiting
4. **Error Handling**: Basic error handling, needs improvement
5. **Testing**: No automated tests included
6. **Monitoring**: No logging or monitoring setup

## Future Enhancements

1. **Authentication & Authorization**: JWT-based auth system
2. **Caching Layer**: Redis for frequently accessed data
3. **Real-time Updates**: WebSocket for live inventory updates
4. **Advanced Search**: Faceted search, autocomplete, recommendations
5. **API Versioning**: Proper versioning strategy
6. **Monitoring**: Comprehensive logging and metrics
7. **Testing**: Unit and integration tests
8. **CI/CD**: Automated deployment pipeline

## Conclusion

This e-commerce API demonstrates modern backend development practices with a focus on scalability, maintainability, and performance. The architecture supports future growth while maintaining simplicity for the current requirements. The combination of relational database and search engine provides both structured data integrity and powerful search capabilities.

---

*This design document serves as the foundation for implementing the e-commerce REST API with modern development practices and tools.*

```

### Using Python Virtual Environment Skill

For local development of the API service:

```bash
# Create development environment
@python-venv create venv_name="ecommerce-dev" python_version="3.11"

# Install dependencies with smart typo detection
@python-venv install packages="fastapi, uvicorn, sqlalchemy, pymysql, elasticsearch, pydantic, requests"

# The skill will:
# - Detect and correct any typos (e.g., "sqlachemy" → "sqlalchemy")
# - Validate packages exist on PyPI
# - Install with proper versions
# - Create requirements.txt automatically
```

## Project Overview
