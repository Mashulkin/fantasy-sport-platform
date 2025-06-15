# 🏆 Fantasy Sports Platform

> Advanced fantasy sports management platform with automated data collection and virtual H2H tournaments

## ✨ Features

### Current Features

- 🔄 **Automated Data Parsing** - Real-time data collection from fantasy platforms
- 📊 **Data Visualization** - Interactive charts and tables for player statistics
- 🏃‍♂️ **FPL Integration** - Full Fantasy Premier League data support
- ⚡ **Background Processing** - Celery-powered scheduled tasks
- 🔐 **Authentication** - JWT-based user management
- 📱 **Modern UI** - Vue 3 + Vuetify responsive interface
- 🔍 **API Documentation** - Interactive Swagger/OpenAPI docs

### In Development

- 🎯 **Virtual Tournaments** - Head-to-head fantasy competitions
- 🏟️ **Multi-Platform Support** - Fanteam, Sorare, and other platforms
- 📈 **Advanced Analytics** - Player performance predictions
- 🏆 **Tournament Management** - Create and manage fantasy leagues

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo>
   cd fantasy-sports-platform
   ```

2. **Setup environment**

   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables**
   Edit `.env` file:

   ```env
   SECRET_KEY=your-secure-secret-key-here
   FIRST_SUPERUSER=admin@example.com
   FIRST_SUPERUSER_PASSWORD=your-admin-password
   ```

4. **Start the platform**

   ```bash
   docker-compose up -d
   ```

5. **Verify installation**

   ```bash
   docker-compose ps
   ```

## 🌐 Access Points

| Service              | URL                         | Description                   |
| -------------------- | --------------------------- | ----------------------------- |
| **Frontend**         | http://localhost            | Main application interface    |
| **Backend API**      | http://localhost:8000       | Direct API access             |
| **API Docs**         | http://localhost:8000/docs  | Interactive API documentation |
| **Alternative Docs** | http://localhost:8000/redoc | ReDoc API documentation       |
| **Flower**           | http://localhost:5555       | Celery task monitoring        |

### Database Access

- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │  Vue.js Client  │    │  Fantasy APIs   │
│                 │    │                 │    │    (FPL, etc)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      │
┌─────────────────┐    ┌─────────────────┐              │
│  FastAPI Backend│◄───┤   PostgreSQL    │              │
│                 │    │    Database     │              │
└─────────┬───────┘    └─────────────────┘              │
          │                                             │
          ▼                                             │
┌─────────────────┐    ┌─────────────────┐              │
│ Celery Workers  │◄───┤     Redis       │◄─────────────┘
│   + Scheduler   │    │   Message Broker│
└─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
fantasy-sports-platform/
├── 🐍 backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/             # REST API endpoints
│   │   ├── core/               # Core functionality (config, security, celery)
│   │   ├── models/             # SQLAlchemy database models
│   │   ├── parsers/            # Data parsing modules
│   │   │   └── fpl/            # Fantasy Premier League parsers
│   │   ├── schemas/            # Pydantic request/response models
│   │   └── services/           # Business logic services
│   ├── alembic/                # Database migrations
│   └── scripts/                # Utility scripts
├── 🎨 frontend/                # Vue.js application
│   └── src/
│       ├── api/                # API client
│       ├── views/              # Page components
│       └── stores/             # Pinia state management
├── 🌐 nginx/                   # Reverse proxy configuration
└── 📝 docker-compose.yml       # Development environment
```

## 🛠️ Development

### Backend Development

Start backend in development mode:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

Start frontend in development mode:

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# View migration history
docker-compose exec backend alembic history
```

### Adding New Parsers

1. **Create parser class** in `backend/app/parsers/platform/`
2. **Register in service** at `backend/app/services/parser_service.py`
3. **Configure via API** or admin interface

## 📚 API Documentation

### Authentication

```bash
# Get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=changethis"
```

### Parser Management

```bash
# List all parsers
curl -X GET "http://localhost:8000/api/v1/parsers" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Run parser manually
curl -X POST "http://localhost:8000/api/v1/parsers/1/run" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Check task status
curl -X GET "http://localhost:8000/api/v1/parsers/task/TASK_ID/status" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### Player Data

```bash
# Get players list
curl -X GET "http://localhost:8000/api/v1/players" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Upload player data CSV
curl -X POST "http://localhost:8000/api/v1/upload/csv/players" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@players.csv" \
     -F "platform=FPL"
```

## ⚙️ Configuration

### Environment Variables

| Variable                   | Description           | Default                       |
| -------------------------- | --------------------- | ----------------------------- |
| `SECRET_KEY`               | JWT signing key       | `your-secret-key-change-this` |
| `FIRST_SUPERUSER`          | Admin email           | `admin@example.com`           |
| `FIRST_SUPERUSER_PASSWORD` | Admin password        | `changethis`                  |
| `DATABASE_URL`             | PostgreSQL connection | Auto-configured               |
| `REDIS_URL`                | Redis connection      | Auto-configured               |
| `TZ`                       | Timezone              | `Europe/Moscow`               |

### Parser Scheduling

Parsers use cron format for scheduling:

```
# Format: minute hour day month weekday
0 */4 * * *    # Every 4 hours
0 */2 * * *    # Every 2 hours  
*/15 * * * *   # Every 15 minutes
0 9,21 * * *   # At 9:00 and 21:00
```

## 📊 Monitoring & Logs

### Celery Monitoring (Flower)

- **URL**: http://localhost:5555
- **Features**: Task history, worker status, real-time monitoring

### Container Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
```

### Parser Logs

- **Web UI**: Admin → Parser Management → View Logs
- **API**: `GET /api/v1/parsers/{parser_id}/logs`

## 🐛 Troubleshooting

### Common Issues

**Database connection errors:**

```bash
docker-compose logs db
docker-compose restart backend
```

**Celery tasks not running:**

```bash
docker-compose logs celery_worker
docker-compose logs celery_beat
docker-compose restart celery_worker celery_beat
```

**Frontend not updating:**

```bash
# Clear browser cache or restart
docker-compose restart frontend
```

**Permission errors on Linux:**

```bash
sudo chown -R $USER:$USER .
```

### Performance Tuning

**For Production:**

- Change Celery pool from `solo` to `prefork`
- Increase worker concurrency: `--concurrency=4`
- Set up proper reverse proxy caching
- Use environment-specific settings

**For Windows Development:**

- Keep `--pool=solo` for compatibility
- Reduce `--max-tasks-per-child=10`

## 🔒 Security Notes

1. **Change default secrets** in `.env`
2. **Use strong passwords** for database and admin
3. **Configure CORS** for production
4. **Set up SSL/TLS** for production deployment
5. **Limit Flower access** (add authentication)

## 🚀 Deployment

### Production Checklist

- [ ] Update all default passwords
- [ ] Configure proper domain names
- [ ] Set up SSL certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation
- [ ] Set proper resource limits

### Quick Commands

```bash
# Stop all services
docker-compose down

# Full cleanup (removes data!)
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build

# Update dependencies
docker-compose exec backend pip install -r requirements.txt
docker-compose exec frontend npm install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

---

**Need help?** Check the [API documentation](http://localhost:8000/docs) or open an issue on GitHub.
