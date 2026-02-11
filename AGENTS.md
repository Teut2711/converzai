# Development Guidelines

## Code Standards
- NO comments in code
- Use readable names 
- MVC in backend
- Follow Pythonic design principles
- Use type hints consistently
- Keep functions and classes focused on single responsibility

## Architecture
- Models: Database entities with Tortoise ORM
- Views: FastAPI endpoints and HTTP handling  
- Controllers: Business logic in services layer
- Use dependency injection for services
- Separate concerns properly

## Performance
- Use Tortoise queryset creators for bulk operations
- Implement proper database indexing
- Use async/await consistently
- Optimize database queries with prefetch_related

## Elasticsearch Usage
- Use Elasticsearch for full-text search and analytics
- Implement proper indexing strategies for products
- Use search service layer for Elasticsearch operations
- Handle Elasticsearch connection errors gracefully
- Index data automatically on product creation/update
- Use proper mapping for search relevance
- Implement search result pagination
- Cache frequent search queries when appropriate

## Testing
- Write comprehensive tests for all endpoints
- Use pytest with async support
- Mock external dependencies including Elasticsearch
- Test both happy path and error cases
- Test search functionality with mocked Elasticsearch