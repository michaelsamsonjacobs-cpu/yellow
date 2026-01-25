# Yellow Backend

News integrity platform backend - Python/FastAPI

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

## Environment Variables

See `.env.example` for required configuration.

## API Documentation

After starting the server, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
