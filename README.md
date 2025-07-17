# Gemini-Style Backend System

## Table of Contents
- [Features](#features)
- [Setup & Run Instructions](#setup--run-instructions)
- [Architecture Overview](#architecture-overview)
- [Queue System Explanation](#queue-system-explanation)
- [Gemini API Integration Overview](#gemini-api-integration-overview)
- [Assumptions & Design Decisions](#assumptions--design-decisions)
- [Testing via Postman](#testing-via-postman)
- [Access & Deployment Instructions](#access--deployment-instructions)

---

## Features
- OTP-based login (mobile only)
- JWT authentication
- User-specific chatrooms
- Async Gemini API conversations (via Redis queue)
- Stripe-powered subscriptions (Basic/Pro)
- Rate-limiting for Basic users
- Redis caching for chatroom list

---

## Setup & Run Instructions

1. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd backend/app
   ```

2. **Create a `.env` file** in `backend/app` with:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/gemini_db
   REDIS_URL=redis://localhost:6379/0
   JWT_SECRET_KEY=your_jwt_secret
   STRIPE_API_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   GEMINI_API_KEY=your_gemini_api_key
   STRIPE_PRO_PRICE_ID=price_...
   STRIPE_BASIC_PRICE_ID=price_...
   ```

3. **Install dependencies** (in a virtual environment):
   ```sh
   pip install -r requirements.txt
   ```

4. **Run database migrations**:
   ```sh
   python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
   # Or use Alembic if configured
   ```

5. **Start services**:
   - **FastAPI server:**
     _Run this command from the backend directory:_
     ```sh
     uvicorn main:app --reload
     ```
   - **Celery worker:**
     _Run this command from the backend directory:_
     ```sh
     celery -A app.celery_worker.celery_app worker --loglevel=info
     ```
   - **Redis:** Ensure Redis is running on the configured URL.
   - **Stripe CLI (for local webhook testing):**
     _Run these commands from the root directory:_
     - Login to Stripe CLI:
       ```sh
       stripe login
       ```
     - Forward Stripe webhooks to your local server:
       ```sh
       stripe listen --forward-to 127.0.0.1:8000/webhook/stripe
       ```
     - (Optional) Trigger a test event (e.g.,  payment_intent.succeeded):
       ```sh
        stripe trigger payment_intent.succeeded
       ```

---

## Environment Variables Example

A sample environment variable file is provided as `env.example.text` in the `backend/app` directory. This file lists all the required environment variables with example values and comments for each variable.

**How to use:**
1. Copy `env.example.text` to a new file named `.env` in the same directory:
   ```sh
   cp env.example.text .env
   ```
2. Edit the `.env` file and replace the placeholder/example values with your actual secrets and configuration values.
3. The application will automatically load environment variables from this `.env` file when starting up.

**Note:** Never commit your real `.env` file with secrets to version control. Only share `env.example.text` as a reference for other developers.

---

## Architecture Overview

- **FastAPI**: Main web framework for API endpoints.
- **PostgreSQL**: Relational database for users, chatrooms, messages, subscriptions.
- **Redis**: Used for both caching (chatroom lists) and as a Celery broker for background tasks.
- **Celery**: Handles background/async tasks (e.g., Gemini API calls, can be extended for other async jobs).
- **Stripe**: Manages subscription payments and webhooks.
- **Google Gemini API**: Provides AI-powered chat responses.

### Key Modules
- `routers/`: All API endpoints (auth, chatroom, user, subscription)
- `models.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic schemas for request/response validation
- `cache.py`: Redis caching utilities
- `gemini.py`: Gemini API integration
- `stripe_utils.py`: Stripe integration helpers
- `celery_worker.py`: Celery app setup

---

## Queue System Explanation

- **Celery** is used for background processing, with Redis as the broker and backend.
- While Gemini API calls are now synchronous for immediate response, the system is designed to support async/queued processing for scalability (e.g., long-running AI tasks, notifications).
- To add a new async task, define a function with `@celery_app.task` and call it with `.delay()`.
- Celery workers must be running for background tasks to be processed.

---

## Gemini API Integration Overview

- The backend integrates with the [Google Gemini API](https://ai.google.dev/gemini-api/docs/text-generation) for text generation.
- The `/chatroom/{id}/message` endpoint sends user messages to Gemini and returns the AI's response.
- API key is securely loaded from environment variables.
- The integration is designed to be easily swappable for other LLM providers if needed.

---

## Assumptions & Design Decisions

- **Access tokens (JWTs)** are required in the request body for POST/PUT and as query params for GET endpoints.
- **Chatroom list caching** is per-user, with a short TTL (default 10 minutes) to optimize dashboard load times.
- **Stripe webhooks** are validated using the raw request body and the secret provided by Stripe CLI or dashboard.
- **Celery** is included for future scalability, even though Gemini calls are currently synchronous.
- **No ORM `.from_orm()`**: All SQLAlchemy models are converted to dicts before passing to Pydantic, to avoid deprecation and serialization issues.
- **Security**: Only authenticated users can access chatroom, message, and subscription endpoints.

---

## Testing via Postman

1. **Import the Postman collection**:
   - Use the provided `kuvaka_tech_assignment.postman_collection.json` file.
   - In Postman, go to File > Import > select the JSON file.

2. **Set the `{{jwt_token}}` variable**:
   - After verifying OTP, copy the `access_token` from the response and set it as the `jwt_token` variable in Postman.

3. **Test all endpoints**:
   - Requests are organized by folders (Auth, User, Chatroom, Subscription, Stripe Webhook).
   - All protected endpoints require the JWT token as shown in the collection.

---

## Access & Deployment Instructions

- **Local Access**: By default, the API runs at `http://localhost:8000/`.
- **Deployment**:
  - Use a production WSGI server (e.g., Gunicorn with Uvicorn workers) for deployment.
  - Set environment variables securely in your deployment environment.
  - Ensure Redis and PostgreSQL are accessible to the app.
  - Configure Stripe webhook endpoints in the Stripe dashboard to point to your deployed `/webhook/stripe` URL.
- **Environment Variables**: Never commit secrets to version control. Use `.env` files or your cloud provider's secret management.

---

## Contact
For questions or support, contact me @aach.0012345@gmail.com. 
