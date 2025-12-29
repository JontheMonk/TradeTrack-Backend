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
   3. **Install dependencies:**
   
   pip install -r requirements.txt
   4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tradetrack_dev
   ADMIN_API_KEY=your-dev-admin-key-here
   ENV=dev
   CORS_ORIGINS=*
   5. **Run database migrations:**h
   alembic upgrade head
   6. **Start the server:**
   
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

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
