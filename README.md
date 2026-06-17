# CineBook 🎬

A movie ticket booking system built with Flask, featuring ML-powered recommendations, sentiment analysis, dynamic pricing, and interactive seat selection.

## Features

- **Browse Movies** — 33 curated titles with real posters, genre filters, and search
- **Seat Selection** — Interactive grid with Standard / VIP / Recliner tiers and dynamic pricing
- **Booking Flow** — Select seats → confirm → printable e-ticket with cancellation
- **Reviews & Sentiment** — Star ratings + text reviews analyzed via TextBlob, aggregated sentiment bars
- **Personalised Recommendations** — Hybrid engine factoring in your search history, bookings, reviews, and collaborative filtering
- **Dynamic Pricing** — ML model adjusts seat prices based on demand and historical data
- **Authentication** — Register / login / logout with Flask-Login

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | Flask 3.0 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ML | scikit-learn, pandas, NumPy, TextBlob |
| Frontend | Jinja2 templates, vanilla CSS/JS |
| Auth | Flask-Login + Werkzeug |

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

Visit **http://127.0.0.1:5000**

**Demo account:** `demo` / `password`

On first run, the database is automatically created and seeded with 33 movies, 5 theatres, 10 screens, 500 seats, and 165 shows.

## Environment Variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask secret key |
| `POSTGRES_URL` | PostgreSQL connection string (production) |
| `DATABASE_URL` | Fallback database URL |
| `PORT` | Server port (default 5000) |

Omitting `POSTGRES_URL` / `DATABASE_URL` defaults to local SQLite.

## Project Structure

```
├── api/index.py           # Vercel serverless entry
├── app/
│   ├── __init__.py        # App factory, auto-seed
│   ├── extensions.py      # db, login_manager
│   ├── models.py          # 10 ORM models
│   ├── ml/
│   │   ├── recommender.py # Collaborative + content-based recommendations
│   │   ├── pricing.py     # Dynamic seat pricing
│   │   └── sentiment.py   # TextBlob review sentiment
│   ├── routes/
│   │   ├── auth.py        # Register, login, logout
│   │   ├── movies.py      # Browse, search, recommendations
│   │   ├── bookings.py    # Seat select, confirm, cancel, ticket
│   │   └── reviews.py     # Submit reviews with sentiment
│   ├── static/            # CSS, JS, poster images
│   └── templates/         # Jinja2 templates
├── config.py              # Configuration
├── run.py                 # Local entry point
├── seed_db.py             # Database seeder
├── Dockerfile             # Hugging Face Spaces
├── render.yaml            # Render deployment
└── vercel.json            # Vercel deployment
```

## Deployment

### Vercel

1. Push to GitHub
2. Import project at [vercel.com/new](https://vercel.com/new)
3. Add `POSTGRES_URL` environment variable
4. Deploy

### Render

1. Connect GitHub repo to [render.com](https://render.com)
2. Use `render.yaml` blueprint or create a Web Service with start command `gunicorn run:app`
3. Set `POSTGRES_URL` environment variable

### Docker / Hugging Face Spaces

```bash
docker build -t cinebook .
docker run -p 7860:7860 cinebook
```

## API Endpoints

| Route | Description |
|---|---|
| `GET /api/recommendations` | Personalised movie recommendations (JSON) |
| `GET /api/train` | Train collaborative filtering model |
| `GET /api/seed` | Seed database (if empty) |

## License

MIT
