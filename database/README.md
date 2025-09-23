# Database Setup - PostgreSQL with Docker

This directory contains the PostgreSQL database configuration for the EduNote application, running in a Docker container for easy development and deployment.

## Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (included with Docker Desktop)

### Optional: PostgreSQL Client

For direct database access from your host machine:

```bash
# macOS
brew install libpq && brew link --force libpq

# Ubuntu/Debian
sudo apt-get install postgresql-client

# Windows
# Download from https://www.postgresql.org/download/windows/
```

## Quick Start

1. **Navigate to the database directory:**
   ```bash
   cd database/
   ```

2. **Start the database:**
   ```bash
   docker compose up -d
   ```

3. **Verify the database is running:**
   ```bash
   docker compose ps
   ```

## Database Configuration

- **Database Name:** `app_db`
- **Username:** `app_user`
- **Password:** `app_pass`
- **Port:** `5432`
- **Host:** `localhost` (from host machine)

## Common Commands

### Start/Stop Database

```bash
# Start the database
docker compose up -d

# Stop the database
docker compose stop

# Restart the database
docker compose start

# Stop and remove containers
docker compose down
```

### Monitor Database

```bash
# View container status
docker compose ps

# View database logs
docker compose logs db -f

# View all logs
docker compose logs -f
```

### Database Access

#### From Host Machine (if psql is installed)
```bash
psql "postgresql://app_user:app_pass@localhost:5432/app_db"
```

#### From Docker Container
```bash
# Access the database container
docker exec -it app-postgres psql -U app_user -d app_db

# Test database connection
docker exec -it app-postgres pg_isready -U app_user -d app_db
```

#### Quick Connection Test
```bash
psql "postgresql://app_user:app_pass@localhost:5432/app_db" -c "SELECT 1;"
```

## Troubleshooting

### Database Won't Start
- Ensure Docker Desktop is running
- Check if port 5432 is already in use: `lsof -i :5432`
- View logs for errors: `docker compose logs db`

### Connection Issues
- Verify the database is running: `docker compose ps`
- Check if the container is healthy: `docker exec -it app-postgres pg_isready -U app_user -d app_db`
- Ensure you're using the correct connection string

### Reset Database
```bash
# Stop and remove containers and volumes
docker compose down -v

# Start fresh
docker compose up -d
```

## Development Notes

- The database data persists in a Docker volume
- To completely reset the database, use `docker compose down -v`
- The `docker-compose.yml` file contains all database configuration
- Database is accessible from both the host machine and other Docker containers

## Integration with Application

The backend application should connect to the database using:
- **Host:** `localhost` (from host) or `app-postgres` (from Docker)
- **Port:** `5432`
- **Database:** `app_db`
- **Username:** `app_user`
- **Password:** `app_pass`