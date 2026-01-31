# Community Feed

A Reddit-style discussion platform with threaded comments and a 24-hour leaderboard. Built for the Playto internship assignment.

## What This Does

Think of it as a mini-Reddit. Users can post content, comment on posts (with nested replies), and earn karma points when others like their contributions. The leaderboard shows who's been most active in the past 24 hours.

The interesting part? There were three specific technical challenges I had to solve:
- Making comment threads load fast even with hundreds of nested replies (the N+1 problem)
- Preventing duplicate likes when two people click at the exact same moment (race conditions)
- Calculating a 24-hour leaderboard without storing daily totals in the database

Check out [EXPLAINER.md](./EXPLAINER.md) if you want the technical details on how I solved these.

## Tech Stack

**Backend:**
- Django 6.0 with Django REST Framework
- JWT for authentication
- PostgreSQL in production, SQLite for local dev
- CORS headers for cross-origin requests

**Frontend:**
- React 18
- Vite as the build tool
- Tailwind CSS for styling
- Axios for API calls
- React Router for navigation

## Running It Locally

### Backend

```bash
cd backend

# Set up virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load some test data
python seed_data.py

# Start the server
python manage.py runserver
```

Backend runs on `http://localhost:8000`

### Frontend

```bash
cd frontend

# Install packages
npm install

# Start dev server  
npm run dev
```

Frontend runs on `http://localhost:5173`

## Test Accounts

After running `seed_data.py`, you can log in with any of these:

- Username: `alice`, Password: `password123`
- Username: `bob`, Password: `password123`
- Username: `charlie`, Password: `password123`
- Username: `diana`, Password: `password123`
- Username: `eve`, Password: `password123`

alice and diana already have some karma points to test the leaderboard.

## API Endpoints

### Auth
- `POST /api/auth/register/` - Create account
- `POST /api/auth/login/` - Get JWT tokens
- `POST /api/auth/refresh/` - Refresh your access token
- `GET /api/auth/me/` - Get your profile

### Posts
- `GET /api/posts/` - List posts
- `POST /api/posts/` - Create a post (auth required)
- `GET /api/posts/:id/` - Get one post
- `POST /api/posts/:id/like/` - Like/unlike a post (auth required)

### Comments
- `GET /api/comments/?post=:id` - Get comments for a post
- `POST /api/comments/` - Add a comment (auth required)
- `POST /api/comments/:id/like/` - Like/unlike a comment (auth required)

### Leaderboard
- `GET /api/leaderboard/` - Top 5 users in last 24 hours

## The Three Technical Challenges

This assignment had three specific requirements that make it more interesting than a typical CRUD app:

### 1. Comment Threading Without N+1 Queries

When you have 50 nested comments, a naive implementation would make 50+ database queries to fetch them all. I use Django's `select_related` and `prefetch_related` to get everything in about 3-4 queries regardless of how many comments there are.

### 2. Race Condition Prevention

If two users click "like" at the exact same moment, you could end up with duplicate likes in the database. I prevent this with a database-level unique constraint plus atomic transactions that handle the race condition gracefully.

### 3. Dynamic 24-Hour Leaderboard

The leaderboard only counts karma from the last 24 hours, but I can't just store a "daily_karma" field on the user model. Instead, I aggregate from the Like records using their timestamps. Check out the EXPLAINER for the SQL query this generates.

## Testing

I wrote a script that tests all the endpoints:

```bash
cd backend
python test_api.py
```

This verifies:
- User registration and login
- Post creation and retrieval  
- Comment threading with proper depth tracking
- Like toggle (and that the race condition is handled)
- Leaderboard calculation

## Project Structure

```
backend/
  ├── core/              # Main app
  │   ├── models/       # Database models
  │   ├── serializers/  # DRF serializers
  │   ├── views/        # API views
  │   └── services/     # Business logic
  ├── config/           # Django settings
  ├── seed_data.py     # Generate test data
  └── test_api.py      # API tests

frontend/
  ├── src/
  │   ├── components/   # React components
  │   ├── pages/        # Page-level components
  │   ├── services/     # API client
  │   └── utils/        # Helper functions
  └── package.json
```

## Deployment

**Backend** → Render (with PostgreSQL)  
**Frontend** → Vercel

See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for step-by-step instructions.

Quick version:
1. Push code to GitHub
2. Create a Render web service connected to your repo
3. Add a PostgreSQL database on Render
4. Set environment variables (SECRET_KEY, DATABASE_URL, etc.)
5. Deploy frontend to Vercel with `VITE_API_URL` pointing to your backend

## Environment Variables

Backend needs a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

For production, you'll also need PostgreSQL connection details.

## What I Learned

This project forced me to think about:
- How Django ORM works under the hood (especially `select_related` vs `prefetch_related`)
- Database constraints and when to use them vs application-level validation
- Atomic transactions and why they matter for data consistency
- When to denormalize data vs when to aggregate on the fly
- How JWT authentication works in a stateless API

The EXPLAINER goes into way more detail if you're interested in the implementation specifics.

## License

MIT - feel free to use this as a reference!
