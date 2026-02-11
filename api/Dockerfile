# Stage 1: Build and test stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run tests
RUN python -m pytest app/tests/ -v --tb=short

# Stage 2: Production stage
FROM python:3.11-slim AS production

WORKDIR /app

# Install only runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only application code from builder stage
COPY --from=builder /app .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
