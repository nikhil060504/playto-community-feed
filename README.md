# Community Feed - Playto Internship Assignment

A full-stack community feed application with threaded discussions and a dynamic leaderboard, built with Django REST Framework and React.

## 🎯 Project Overview

This project demonstrates:
- **Complex Backend Architecture**: Django + DRF with PostgreSQL
- **Race Condition Handling**: Database-level constraints prevent double-likes
- **N+1 Query Optimization**: Efficient comment tree fetching
- **Dynamic Aggregation**: 24h leaderboard calculated from transaction history, not stored fields

## 🚀 Features

### Core Functionality
- ✅ **User Authentication**: JWT-based register/login with secure token management
- ✅ **Post Feed**: Create and view text posts with like counts
- ✅ **Threaded Comments**: Reddit-style nested comments with depth tracking
- ✅ **Gamification**: 
  - 1 Like on Post = 5 Karma points
  - 1 Like on Comment = 1 Karma point
- ✅ **Leaderboard**: Top 5 users by karma earned in last 24 hours only

### Technical Highlights
- ✅ **Race Condition Prevention**: Atomic transactions + unique constraints
- ✅ **N+1 Query Prevention**: `select_related` and `prefetch_related` optimization
- ✅ **Dynamic 24h Karma**: Calculated from `Like` model timestamps, no stored daily_karma field

## 📁 Project Structure

```
playto-community-feed/
├── backend/                    # Django REST Framework API
│   ├── config/                 # Django settings
│   ├── core/                   # Main application
│   │   ├── models/            # User, Post, Comment, Like
│   │   ├── serializers/       # DRF serializers
│   │   ├── views/             # API endpoints
│   │   ├── services/          # Business logic layer
│   │   └── admin.py           # Django admin config
│   ├── seed_data.py           # Sample data script
│   ├── test_api.py            # API testing script
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + Tailwind CSS
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   └── utils/             # Helper functions
│   ├── package.json
│   └── vite.config.js
│
├── README.md                   # This file
└── EXPLAINER.md               # Technical deep-dive
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 6.0 + Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **CORS**: django-cors-headers

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Routing**: React Router v6

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (for production)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Load seed data
python seed_data.py

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173/`

## 🧪 Testing the API

Run the comprehensive API test suite:

```bash
cd backend
python test_api.py
```

This tests:
- User registration and login
- Post CRUD operations
- Comment threading with depth tracking
- Like toggle (verifies race condition handling)
- Dynamic 24h leaderboard calculation

## 🔐 Test Credentials

The seed data creates 5 test users:

| Username | Password | Email |
|----------|----------|-------|
| alice | password123 | alice@example.com |
| bob | password123 | bob@example.com |
| charlie | password123 | charlie@example.com |
| diana | password123 | diana@example.com |
| eve | password123 | eve@example.com |

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user profile

### Posts
- `GET /api/posts/` - List all posts (paginated)
- `POST /api/posts/` - Create new post (auth required)
- `GET /api/posts/:id/` - Get single post
- `POST /api/posts/:id/like/` - Toggle like on post (auth required)

### Comments
- `GET /api/comments/?post=:id` - Get comments for post
- `POST /api/comments/` - Create comment (auth required)
- `POST /api/comments/:id/like/` - Toggle like on comment (auth required)

### Leaderboard
- `GET /api/leaderboard/` - Get top 5 users by 24h karma

## 🔧 Environment Variables

Create a `.env` file in the backend directory:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for dev)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# For PostgreSQL in production:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=community_feed_db
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=your_db_host
# DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🚀 Deployment

### Backend (Render)
1. Create new Web Service on Render
2. Connect GitHub repository
3. Add PostgreSQL database
4. Set environment variables
5. Build command: `pip install -r requirements.txt && python manage.py migrate`
6. Start command: `gunicorn config.wsgi:application`

### Frontend (Vercel)
1. Import GitHub repository to Vercel
2. Set framework preset to "React"
3. Set environment variable: `VITE_API_URL=https://your-backend-url.onrender.com`
4. Deploy!

## 📚 Documentation

For a detailed technical explanation of how we solved the three critical challenges, see [EXPLAINER.md](./EXPLAINER.md):
- Comment tree modeling & serialization (N+1 prevention)
- 24h leaderboard calculation (dynamic aggregation)
- Race condition handling (double-like prevention)

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Clean, modular Django architecture (models, services, views)
- ✅ Complex database relationships and queries
- ✅ Concurrency handling with database constraints
- ✅ N+1 query optimization techniques
- ✅ Dynamic aggregation vs. denormalization trade-offs
- ✅ JWT authentication in a stateless API
- ✅ RESTful API design with DRF
- ✅ React state management and component composition

## 👨‍💻 Author

Built for the Playto internship assignment.

## 📄 License

MIT License - feel free to use this as a reference project!
