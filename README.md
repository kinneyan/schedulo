# <img src="client/public/schedulo.png" alt="Schedulo Logo" width="40" height="40" align="left">&nbsp;&nbsp;Schedulo

Schedulo is an open-source work tracking application built with modern web technologies and containerized with Docker. It features a React frontend powered by Vite, a Django REST API backend, and a PostgreSQL database.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kinneyan/schedulo.git
   cd schedulo
   ```

2. **Configure environment variables**
   
   Copy the example environment files and configure them:
   
   **For development:**
   ```bash
   cp .env.dev.example .env.dev
   ```
   
   **For production:**
   ```bash
   cp .env.prod.example .env.prod
   ```
   
   Edit the `.env.dev` or `.env.prod` file with your actual configuration values, especially:
   - Database credentials
   - API URLs
   - Any other environment-specific settings

3. **Run the application**
   ```bash
   docker compose up -d --build
   ```

The application will be available at:
- Frontend: http://localhost:5173 (development) or http://localhost:5000 (production)
- Backend API: http://localhost:8000
- Database: localhost:5432

## Docker Commands

### Development & Deployment

```bash
# Run the entire application (development)
docker compose up -d --build

# Run the entire application (production)
docker compose -f docker-compose-prod.yml up -d --build

# Rebuild a specific service
docker compose up -d --build --no-deps <APP_NAME>

# View running containers
docker ps

# Stop the application
docker compose down
```

### Container Management

```bash
# Execute commands inside containers
docker exec -it <CONTAINER_NAME> <COMMAND>

# Examples:
docker exec -it django python manage.py migrate
docker exec -it postgres psql -U postgres -d postgres
```

## Development

### Database Management

```bash
# Generate Django migrations
python manage.py makemigrations

# Apply migrations (automatically done on container rebuild)
docker exec -it django python manage.py migrate
```

### Testing

The project includes comprehensive test coverage with both unit and integration tests.

```bash
# Run all tests
python manage.py test api.tests --settings=server.settings.tests

# Run only integration tests
python manage.py test api.tests.integration --settings=server.settings.tests

# Run only unit tests
python manage.py test api.tests.unit --settings=server.settings.tests

# Run specific integration test areas
python manage.py test api.tests.integration.auth --settings=server.settings.tests
python manage.py test api.tests.integration.roles --settings=server.settings.tests
```

## Project Structure

```
schedulo/
├── client/                 # React frontend
├── server/                 # Django backend
│   ├── api/               # Django API app
│   ├── server/            # Django project settings
│   │   └── settings/      # Environment-specific settings
│   ├── manage.py
│   └── requirements.txt
├── docker-compose.yml     # Development configuration
├── docker-compose-prod.yml # Production configuration
├── .env.dev.example       # Development environment template
├── .env.prod.example      # Production environment template
└── README.md
```

## Environment Configuration

### Development (.env.dev)

- `DJANGO_ENV=development`
- `REACT_ENV=development`
- `REACT_PORT=5173`
- Database configuration
- `VITE_API_URL=http://localhost:8000`

### Production (.env.prod)

- `DJANGO_ENV=production`
- `NODE_ENV=production`
- `REACT_ENV=production`
- `REACT_PORT=5000`
- Production database configuration
- `VITE_API_URL=https://your-domain.com`

## API Documentation

The Django REST API provides endpoints for:
- User authentication and authorization
- Work tracking functionality
- Data management

API endpoints are available at `http://localhost:8000/api/` when running locally.
