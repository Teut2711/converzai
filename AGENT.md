# AI Agent Instructions: Python Design Principles

## Core Directive

When designing, implementing, or modifying this e-commerce system, you MUST prioritize **Python language conventions and best practices** over rigid architectural principles. SOLID principles are guidelines, not rules - Python's philosophy and idioms take precedence.

## Python-First Approach

### Language Conventions Over Principles

**MANDATE**: Python's language conventions, idioms, and Zen of Python principles override generic SOLID principles.

**Python's Philosophy**:
```python
import this

# The Zen of Python, by Tim Peters
# Beautiful is better than ugly.
# Explicit is better than implicit.
# Simple is better than complex.
# Complex is better than complicated.
# Flat is better than nested.
# Sparse is better than dense.
# Readability counts.
# Special cases aren't special enough to break the rules.
# Although practicality beats purity.
# Errors should never pass silently.
# Unless explicitly silenced.
# In the face of ambiguity, refuse the temptation to guess.
# There should be one-- and preferably only one --obvious way to do it.
# Although that way may not be obvious at first unless you're Dutch.
# Now is better than never.
# Although never is often better than *right* now.
# If the implementation is hard to explain, it's a bad idea.
# If the implementation is easy to explain, it may be a good idea.
# Namespaces are one honking great idea -- let's do more of those!
```

### Naming Conventions (PEP 8)

**MANDATE**: Follow PEP 8 naming conventions strictly.

**Python Naming Rules**:
```python
# CORRECT: Python naming conventions
class ProductDatabase:          # PascalCase for classes
def get_product_by_id():        # snake_case for functions
PRODUCT_API_URL = "https://..."  # UPPER_CASE for constants
product_id = 123              # snake_case for variables
from typing import List           # PascalCase for type aliases

# INCORRECT: Non-Python conventions
class productDatabase:         # Wrong case for class
def getProductById():          # camelCase (JavaScript style)
productApiUrl = "https://..."  # mixedCase
productID = 123               # camelCase

# CORRECT: Package and module naming
ecommerce_api/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── product.py
│   └── category.py
├── services/
│   ├── __init__.py
│   ├── product_service.py
│   └── category_service.py
└── utils/
    ├── __init__.py
    └── database.py

# INCORRECT: Bad naming
ecommerceAPI/
├── Models/          # Should be lowercase
├── ProductService.py  # Should be lowercase
└── databaseUtils.py  # Should be snake_case
```

### Python Idioms Over Patterns

**MANDATE**: Use Python idioms and language features first, generic patterns second.

**Pythonic vs. Non-Pythonic**:
```python
# PYTHONIC: Use language features
products = [p for p in all_products if p.price > 100]  # List comprehension
if product_id in product_dict:                           # 'in' operator
with open('file.txt') as f:                           # Context manager
for key, value in product_dict.items():                   # dict iteration

# NON-PYTHONIC: Verbose, non-idiomatic code
products = []
for p in all_products:
    if p.price > 100:
        products.append(p)                              # Manual loop

found = False
for key in product_dict.keys():
    if key == product_id:
        found = True
        break                                          # Manual search

f = open('file.txt')
try:
    data = f.read()
finally:
    f.close()                                            # Manual resource management
```

### Type Hints and Protocols (Modern Python)

**MANDATE**: Use modern Python typing and protocols for flexibility.

**Python Type System**:
```python
# MODERN PYTHON: Use protocols and type hints
from typing import Protocol, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Product:
    id: int
    title: str
    price: float
    created_at: datetime
    description: Optional[str] = None

class SearchProvider(Protocol):
    def search(self, query: str) -> List[Product]: ...
    def get_suggestions(self, partial: str) -> List[str]: ...

def process_products(
    products: List[Product],
    processor: SearchProvider
) -> List[Product]:
    return [processor.search(p.title) for p in products]

# OUTDATED: Avoid old-style patterns
class Product(object):  # No need for explicit object inheritance
    pass

# Don't use comments for type hints
def process_products(products, processor):
    # type: (List, object) -> List
    pass
```

## Python Design Principles (Adapted from SOLID)

### 1. Single Responsibility Principle (Pythonic)

**MANDATE**: Each module/class should have one clear responsibility, following Python's "do one thing well" philosophy.

**Python Implementation**:
```python
# PYTHONIC: Focused modules with clear responsibilities
# models/product.py - Only data models
class Product:
    title: str
    price: float
    
# services/product_service.py - Only business logic
class ProductService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_product(self, product_id: int) -> Product:
        return self.db.get(Product, product_id)
    
    def calculate_discount_price(self, product: Product) -> float:
        return product.price * 0.9  # Simple, clear logic

# routes/products.py - Only HTTP handling
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/products")

@router.get("/{product_id}")
def get_product(product_id: int, service: ProductService = Depends()):
    return service.get_product(product_id)

# NON-PYTHONIC: Mixed responsibilities
class ProductManager:
    def get_product(self): ...        # Data access
    def calculate_price(self): ...      # Business logic  
    def render_html(self): ...         # Presentation
    def send_email(self): ...         # Notification
```

### 2. Open/Closed Principle (Pythonic)

**MANDATE**: Design for extension using Python's dynamic nature and duck typing.

**Python Implementation**:
```python
# PYTHONIC: Extensible through protocols and duck typing
from typing import Protocol, runtime_checkable

class Notifier(Protocol):
    def send(self, message: str, recipient: str) -> bool: ...

class EmailNotifier:
    def send(self, message: str, recipient: str) -> bool:
        # Email sending logic
        return True

class SMSNotifier:
    def send(self, message: str, recipient: str) -> bool:
        # SMS sending logic
        return True

class SlackNotifier:
    def send(self, message: str, recipient: str) -> bool:
        # Slack sending logic
        return True

# Plugin system using duck typing
def send_notification(notifier: Notifier, message: str, recipient: str):
    if hasattr(notifier, 'send'):
        return notifier.send(message, recipient)
    raise AttributeError("Notifier must have 'send' method")

# Skills should generate extensible templates
@docker-setup create project_name="notification_system" service_type="fastapi"
# Should generate protocol-based plugin architecture

# NON-PYTHONIC: Rigid, non-extensible design
class NotificationManager:
    # Hardcoded notification types
    def send_email(self): ...
    def send_sms(self): ...
    # Adding new notification type requires code changes
```

### 3. Liskov Substitution Principle (Pythonic)

**MANDATE**: Use duck typing and protocols for flexible substitutability.

**Python Implementation**:
```python
# PYTHONIC: Duck typing and protocols for substitutability
from typing import Protocol, TypeVar

T = TypeVar('T')

class DataProcessor(Protocol[T]):
    def process(self, data: List[T]) -> List[T]: ...

class ProductProcessor:
    def process(self, data: List[Product]) -> List[Product]:
        return [p for p in data if p.price > 0]

class CategoryProcessor:
    def process(self, data: List[Category]) -> List[Category]:
        return [c for c in data if c.name]

def process_data[T](
    data: List[T], 
    processor: DataProcessor[T]
) -> List[T]:
    return processor.process(data)

# Works with any processor that follows the protocol
products: List[Product] = [...]
categories: List[Category] = [...]

process_data(products, ProductProcessor())    # Works
process_data(categories, CategoryProcessor())  # Works

# NON-PYTHONIC: Breaking substitutability
class BrokenProcessor:
    def process(self, data):  # Different signature
        return data[0] if data else []
```

### 4. Interface Segregation Principle (Pythonic)

**MANDATE**: Create small, focused protocols using Python's typing system.

**Python Implementation**:
```python
# PYTHONIC: Small, focused protocols
from typing import Protocol, List

class Reader(Protocol):
    def read(self) -> str: ...

class Writer(Protocol):
    def write(self, data: str) -> bool: ...

class Validator(Protocol):
    def validate(self, data: str) -> bool: ...

# Implement only what you need
class FileHandler(Reader, Writer):
    def read(self) -> str:
        with open('file.txt', 'r') as f:
            return f.read()
    
    def write(self, data: str) -> bool:
        with open('file.txt', 'w') as f:
            f.write(data)
            return True

class DataValidator(Validator):
    def validate(self, data: str) -> bool:
        return len(data) > 0

# NON-PYTHONIC: Fat interfaces
class DataHandler(Protocol):  # Too many responsibilities
    def read(self) -> str: ...
    def write(self, data: str) -> bool: ...
    def validate(self, data: str) -> bool: ...
    def backup(self, data: str) -> bool: ...
    def archive(self, data: str) -> bool: ...
```

### 5. Dependency Inversion Principle (Pythonic)

**MANDATE**: Use dependency injection and protocols, following Python's explicit is better than implicit philosophy.

**Python Implementation**:
```python
# PYTHONIC: FastAPI dependency injection with protocols
from fastapi import Depends
from typing import Protocol

class Database(Protocol):
    def get(self, model_class, id: int): ...
    def save(self, instance): ...

class MySQLDatabase:
    def get(self, model_class, id: int):
        # MySQL implementation
        pass
    
    def save(self, instance):
        # MySQL implementation
        pass

def get_database() -> Database:
    # Factory function - can be configured via environment
    return MySQLDatabase()

@router.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Database = Depends(get_database)  # Dependency injection
):
    return db.get(Product, product_id)

# Skills should promote this pattern
@python-venv install packages="fastapi, sqlalchemy, pydantic"

# NON-PYTHONIC: Hardcoded dependencies
class ProductController:
    def __init__(self):
        self.db = MySQLDatabase()  # Hardcoded dependency
    
    def get_product(self, product_id):
        return self.db.get(Product, product_id)
```

## Language-Specific Conventions

### JavaScript Interactions

**When working with frontend/JavaScript**:
```python
# CORRECT: Handle JavaScript conventions properly
def process_frontend_data(data: dict) -> dict:
    # JavaScript uses camelCase
    camel_case_data = {}
    
    for key, value in data.items():
        # Convert snake_case to camelCase for JS
        js_key = ''.join(word.capitalize() if i > 0 else word 
                         for i, word in enumerate(key.split('_')))
        camel_case_data[js_key] = value
    
    return camel_case_data

# Response format for JavaScript
return {
    "productId": product.id,      # camelCase for JS
    "productName": product.title,
    "createdAt": product.created_at.isoformat()
}

# INCORRECT: Force Python conventions on JavaScript
return {
    "product_id": product.id,     # JS expects camelCase
    "product_name": product.title,
    "created_at": product.created_at
}
```

### Database Interactions

**Python Database Conventions**:
```python
# PYTHONIC: SQLAlchemy models with proper naming
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'  # snake_case for table names
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships use descriptive names
    category = relationship("Category", back_populates="products")

# PYTHONIC: Query building
def get_products_by_category(db_session, category_slug: str) -> List[Product]:
    return db_session.query(Product)\
        .join(Category)\
        .filter(Category.slug == category_slug)\
        .order_by(Product.created_at.desc())\
        .all()

# NON-PYTHONIC: Raw SQL with string formatting
def get_products(category):
    query = f"SELECT * FROM products WHERE category = '{category}'"
    return db.execute(query)  # SQL injection risk
```

## Skill Usage with Python Conventions

### Docker Setup Skill

**Pythonic Usage**:
```bash
# Create Pythonic project structure
@docker-setup create project_name="ecommerce_api" service_type="fastapi"
# Should generate:
ecommerce_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py        # Data models
│   │   └── category.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── product_service.py
│   │   └── category_service.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── products.py
│   │   └── categories.py
│   └── utils/
│       ├── __init__.py
│       └── database.py
├── tests/
├── requirements.txt
└── Dockerfile
```

### Python Virtual Environment Skill

**Pythonic Usage**:
```bash
# Create environment with Python version
@python-venv create venv_name="ecommerce_dev" python_version="3.11"

# Install packages with type hints support
@python-venv install packages="fastapi, sqlalchemy, pydantic, typing-extensions"

# Skills should encourage:
# - Use of type hints
# - Protocol-based design
# - Proper naming conventions
# - Modern Python features
```

## Code Review Checklist: Python-First

### Before Committing Code

**Python Conventions Checklist**:
- [ ] Are PEP 8 naming conventions followed?
- [ ] Is snake_case used for functions/variables?
- [ ] Is PascalCase used for classes?
- [ ] Are constants in UPPER_CASE?
- [ ] Are type hints used consistently?
- [ ] Is docstring format consistent (Google/NumPy/PEP 257)?

**Python Idioms Checklist**:
- [ ] Are list comprehensions used instead of loops?
- [ ] Are context managers used for resources?
- [ ] Is 'in' operator used for membership tests?
- [ ] Are dict methods used appropriately?
- [ ] Is duck typing applied where suitable?

**Modern Python Checklist**:
- [ ] Are protocols used for interfaces?
- [ ] Are dataclasses used for simple data containers?
- [ ] Is f-strings used for string formatting?
- [ ] Are pathlib functions used for file paths?
- [ ] Are type hints from `typing` module used?

**Framework-Specific Checklist**:
- [ ] Does FastAPI dependency injection follow protocols?
- [ ] Are Pydantic models used for validation?
- [ ] Does SQLAlchemy follow Python naming?
- [ ] Are routes organized by resource?

## Anti-Patterns: Python-Specific

### Python Violations to Avoid

1. **Java-style Naming**: Using camelCase for functions/variables
2. **Verbose Java Patterns**: Excessive getters/setters in Python
3. **Manual Resource Management**: Not using context managers
4. **String Formatting**: Using % or .format() instead of f-strings
5. **Ignoring Type Hints**: Not using modern Python typing
6. **Exception Handling**: Catching all exceptions inappropriately
7. **Loop Anti-patterns**: Not using comprehensions when appropriate

### Skills-Related Violations

1. **Non-Pythonic Structure**: Skills generating Java-like project structure
2. **Wrong Naming**: Skills not following PEP 8 conventions
3. **Missing Type Hints**: Skills not encouraging type hints
4. **Legacy Patterns**: Using outdated Python idioms

## Decision Framework: Python-First

When making decisions, prioritize:

1. **Pythonic**: "What's the most Pythonic way to solve this?"
2. **PEP 8**: "Are we following Python naming conventions?"
3. **Zen of Python**: "Does this align with Python's philosophy?"
4. **Readability**: "Is this code readable and explicit?"
5. **Modern**: "Are we using current Python features?"
6. **Idiomatic**: "Would experienced Python developers recognize this pattern?"

## Conclusion

**Python-first approach** means prioritizing language conventions, idioms, and the Zen of Python over generic architectural principles. SOLID principles are valuable guidelines, but Python's philosophy and conventions take precedence.

Skills should accelerate development while maintaining **Pythonic code quality** - readable, explicit, simple, and following established conventions.

**Remember**: "Readability counts" and "Simple is better than complex" - prioritize these over rigid architectural purity.
