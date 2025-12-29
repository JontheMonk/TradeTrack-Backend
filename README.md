# TradeTrack Backend

FastAPI backend for TradeTrack, an employee time tracking application with face recognition.

## Features

- **Employee Management**: Register and search employees
- **Face Verification**: Verify employee identity using face embeddings
- **Time Tracking**: Clock in/out and track time entries
- **Vector Search**: Efficient similarity search using PostgreSQL with pgvector

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 16 with pgvector extension
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Logging**: structlog
- **Rate Limiting**: slowapi

## Prerequisites

- Python 3.13+
- PostgreSQL 16+ (with pgvector extension)
- Docker & Docker Compose (for local development)

## Quick Start

### Local Development with Docker

1. **Start the database:**
  
   docker-compose up -d

2. **Create a virtual environment:**
 
   python -m venv venv

   source venv/bin/activate  # On Windows: venv\Scripts\activate

4. **Install dependencies:**
   
   pip install -r requirements.txt

5. **Set up environment variables:**

   Create a `.env` file in the root directory:
   
   DATABASE_URL=your-database-url

   ADMIN_API_KEY=your-dev-admin-key-here

   ENV=dev

6. **Run database migrations:**

   alembic upgrade head

7. **Start the server:**
   
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

## Environment Variables

### Required

- `DATABASE_URL`: PostgreSQL connection string
- `ADMIN_API_KEY`: Secret key for admin-only endpoints (employee registration)
- `ENV`: Environment identifier (`dev`, `test`, or `prod`)

### Optional

- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: `*`)
- `FACE_MATCH_THRESHOLD`: Similarity threshold for face matching (default: `0.5`)
- `EMBEDDING_DIM`: Face embedding dimension (default: `512`)

## Project Structure

## API Endpoints

### Health
- `GET /health` - Health check endpoint

### Employees
- `POST /employees/` - Register new employee (requires `X-Admin-Key` header)
- `GET /employees/search?prefix={prefix}` - Search employees by ID or name
- `POST /employees/verify` - Verify face embedding against employee

### Time Tracking
- `POST /clock/{employee_id}/in` - Clock in
- `POST /clock/{employee_id}/out` - Clock out
- `GET /clock/{employee_id}/status` - Get current clock status


### Code Style

This project follows PEP 8. Consider using:
- `black` for code formatting
- `ruff` for linting
- `mypy` for type checking

### Adding New Endpoints

1. Create a router in `routers/`
2. Define Pydantic schemas in `schemas/`
3. Implement business logic in `services/`
4. Add data access in `data/*_repository.py`
5. Register router in `main.py`

## License

Jon Snider
