# EduNote

A comprehensive educational note-taking application designed for students and educators. EduNote combines powerful markdown editing, document management, and AI-assisted learning tools in a modern, intuitive interface.

## Features

### Core Functionality
- **Advanced Markdown Editor**: Rich text editing with Milkdown editor featuring syntax highlighting and live preview
- **Document Management**: Upload, view, and organize PDF, Word, text, and markdown files with integrated PDF viewer
- **User Authentication**: Secure JWT-based authentication system with user registration and login
- **Note Organization**: Create, edit, and manage notes with document linking and archival capabilities
- **Multi-format Support**: Handle various document types including PDF, DOCX, TXT, and MD files

### Advanced Features
- **Document-Note Integration**: Link notes to uploaded documents for contextual learning
- **Quiz Integration**: Support for embedding quiz references within notes
- **Flashcard System**: Integration with flashcard functionality for enhanced learning
- **Chat Integration**: Built-in chat system for collaborative learning
- **Search and Filter**: Efficient note and document search capabilities
- **Responsive Design**: Modern UI with Tailwind CSS, optimized for all devices

## Architecture

EduNote follows a microservices architecture with clear separation of concerns:

![System Architecture](design/CS%20520%20System%20Architecture.drawio.png)


```

### Services Overview
- **Auth Service** (Port 8000): User authentication, JWT token management
- **Notes Service** (Port 8001): Note CRUD operations, markdown processing
- **Document Service** (Port 8002): File upload, storage, and retrieval
- **Frontend** (Port 5173): React application with modern UI components

## Prerequisites

### Required Software
- **Python 3.13+**: For backend services
- **Node.js 16+**: For frontend development
- **Docker Desktop**: For database management

### Platform Support
- Windows 10/11 (with PowerShell)
- macOS 10.15+
- Linux (Ubuntu 18.04+)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd EduNote
```

### 2. Database Setup
```bash
# Navigate to database directory
cd database

# Start PostgreSQL with Docker
docker-compose up -d

# Verify database is running
docker-compose ps
```

### 3. Backend Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm run dev --dry-run
```

## Running the Application

### Quick Start (All Platforms)
Use the Python service manager to start all backend services:
```bash
cd backend
# Activate your virtual environment first:
# Windows: ..\venv\Scripts\activate
# macOS/Linux: source ../venv/bin/activate
python start_services.py
```

This will automatically start all three backend services (Auth, Notes, Document) on their respective ports.

### Manual Startup

#### 1. Start Database
```bash
cd database
docker-compose up -d
```

#### 2. Start Backend Services

**Option A: All services at once**
```bash
cd backend
python start_services.py
```

**Option B: Individual services**
```bash
# Terminal 1 - Auth Service
cd backend/auth_service
# Activate virtual environment first (see setup instructions above)
python main.py --port 8000

# Terminal 2 - Notes Service  
cd backend/note_service
# Activate virtual environment first
python main.py --port 8001

# Terminal 3 - Document Service
cd backend/document_service
# Activate virtual environment first
python main.py --port 8002
```

#### 3. Start Frontend
```bash
cd frontend
npm run dev
```

### Service URLs
After successful startup, access the application at:
- **Main Application**: http://localhost:5173
- **Auth API Documentation**: http://localhost:8000/docs
- **Notes API Documentation**: http://localhost:8001/docs  
- **Document API Documentation**: http://localhost:8002/docs

## Default Login Credentials

For testing and development:
- **Email**: `demo@user.com`
- **Password**: `password123`

## API Documentation

### Authentication Service (Port 8000)
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user profile

### Notes Service (Port 8001)
- `GET /notes` - List user notes (with filters)
- `POST /notes` - Create new note
- `GET /notes/{id}` - Get specific note
- `PUT /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note

### Document Service (Port 8002)
- `POST /documents/upload` - Upload document
- `GET /documents` - List user documents
- `GET /documents/{id}` - Get document metadata
- `GET /documents/{id}/download` - Download document
- `GET /documents/{id}/view` - View document (PDF)
- `PUT /documents/{id}` - Update document metadata
- `DELETE /documents/{id}` - Delete document

## Database Configuration

### Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: app_db
- **Username**: app_user
- **Password**: app_pass

### Schema Overview
- **app_user**: User authentication and profiles
- **note**: Note storage with markdown content and metadata
- **document**: File metadata and storage information

### Migrations
```bash
cd database

# Run pending migrations
python scripts/migrate.py migrate

# Create new migration
python scripts/migrate.py create "description"
```

## Development

### Adding New Backend Services
1. Create service directory in `backend/`
2. Add `main.py` with FastAPI app and port argument parsing
3. Add `requirements.txt` with service dependencies
4. Update `backend/start_services.py` to include new service
5. Assign next available port (8003, 8004, etc.)

### Frontend Development
```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

### Environment Variables

#### Backend Services
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: app_db)
- `DB_USER` (default: app_user)
- `DB_PASSWORD` (default: app_pass)

## File Storage

Documents are stored locally in `backend/document_service/uploads/` with:
- UUID-based filenames to prevent conflicts
- Maximum file size: 50MB per upload
- Supported formats: PDF, DOCX, DOC, TXT, MD
- Database metadata tracking for all uploads

## Troubleshooting

### Database Issues
```bash
# Check if database is running
docker-compose ps

# View database logs
docker-compose logs db -f

# Reset database (WARNING: Data loss)
docker-compose down -v
docker-compose up -d
```

### Backend Service Issues
```bash
# Check if ports are available
netstat -an | grep :8000
netstat -an | grep :8001
netstat -an | grep :8002

# Check virtual environment
# Make sure you're in the activated virtual environment
python --version
pip list

# Verify database connection
python -c "import psycopg2; print('PostgreSQL connection available')"
```

### Frontend Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
netstat -an | grep :5173
```

### Common Solutions
1. **Port conflicts**: Change service ports in respective `main.py` files
2. **Database connection**: Ensure Docker is running and database is started
3. **Module not found**: Verify virtual environment is activated and dependencies are installed
4. **File upload errors**: Check `uploads/` directory permissions
5. **CORS issues**: Verify Vite proxy configuration in `vite.config.js`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)  
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Technology Stack

### Frontend
- **React 19.1.1**: Modern UI library with hooks
- **Vite 7.1.6**: Fast build tool and development server
- **Milkdown 7.16.0**: Advanced markdown editor
- **Tailwind CSS 3.4.17**: Utility-first CSS framework
- **Lucide React**: Beautiful SVG icon library

### Backend
- **FastAPI 0.118.0**: Modern Python web framework
- **Uvicorn**: ASGI server for FastAPI applications
- **Pydantic**: Data validation and serialization
- **Psycopg2**: PostgreSQL database adapter
- **BCrypt**: Password hashing
- **JWT**: Token-based authentication

### Database & Infrastructure
- **PostgreSQL 16**: Robust relational database
- **Docker Compose**: Container orchestration
- **UUID Extensions**: Unique identifier generation
- **Migrations**: Database schema version control

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
1. Check the troubleshooting section above
2. Review API documentation at service `/docs` endpoints
3. Create an issue in the project repository
4. Check Docker and service logs for detailed error information