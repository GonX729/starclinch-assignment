# Notification Management System

A full-stack admin panel for managing transactional notifications across **WhatsApp**, **Email**, and **Web Push** — triggered automatically on user login and logout events.

---

## Features

- **Admin notification management** — create, edit, enable, and disable notification templates from a clean web UI
- **Login trigger** — fires all configured notification channels when a user logs in
- **Logout trigger** — fires all configured notification channels when a user logs out
- **WhatsApp notifications** — sends messages via WhatsApp Cloud API (Meta sandbox)
- **Email notifications** — sends transactional emails via Postmark
- **Web Push notifications** — sends browser push notifications via OneSignal
- **Template editor** — channel-aware editor with subject/title/body fields and live variable chips
- **Enable / disable** — toggle individual channel templates without deleting them
- **Test notifications** — send a real test notification directly from the editor modal

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14 (App Router), Tailwind CSS, TypeScript |
| **Backend** | Python, Django 4+, Django REST Framework |
| **Database** | PostgreSQL (SQLite for local development) |
| **Auth** | JWT via `djangorestframework-simplejwt` |
| **WhatsApp** | WhatsApp Cloud API (Meta for Developers — sandbox) |
| **Email** | Resend (free developer tier) |
| **Web Push** | OneSignal (browser push only) |
| **Backend Deploy** | Render |
| **Frontend Deploy** | Vercel |

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

---

### Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env         # then fill in your sandbox credentials

# Apply migrations
python manage.py migrate

# Seed the default triggers (LOGIN, LOGOUT)
python manage.py seed_triggers

# Create an admin account
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Backend runs at: `http://localhost:8000`
Django admin: `http://localhost:8000/admin/`

---

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local   # then set NEXT_PUBLIC_API_URL

# Start the development server
npm run dev
```

Frontend runs at: `http://localhost:3000` (redirects to `/admin/notifications`)

---

### Database Setup

**Local (SQLite — default, no config needed):**  
SQLite is used automatically during local development. No setup required.

**Production (PostgreSQL on Render):**  
Provision a PostgreSQL database on Render and set the `DATABASE_URL` environment variable (see Environment Variables below).

---

## Environment Variables

### Backend — `backend/.env`

```env
# Django
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (leave blank to use SQLite locally)
DATABASE_URL=

# CORS — comma-separated frontend origins
CORS_ALLOWED_ORIGINS=http://localhost:3000

# WhatsApp Cloud API (Meta sandbox)
WHATSAPP_ACCESS_TOKEN=
PHONE_NUMBER_ID=

# Email (Resend)
RESEND_API_KEY=
DEFAULT_FROM_EMAIL=

# Web Push (OneSignal)
ONESIGNAL_APP_ID=
ONESIGNAL_REST_API_KEY=
```

### Frontend — `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

> **Never commit real secrets.** Both `.env` and `.env.local` are listed in `.gitignore`.

---

## Admin Login

**During local development:**

```bash
cd backend
python manage.py createsuperuser
# Follow the prompts to set username, email, and password
```

Then open `http://localhost:3000/login` and sign in with those credentials.

**For the pre-created dev account** (after running `seed_triggers`):

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

> Change this password before any deployment.

To receive WhatsApp and Email notifications, set the admin user's **phone** and **email** fields via the Django admin panel at `http://localhost:8000/admin/`.

---

## Triggers

Triggers are event keys stored in the database that map to notification templates. Two are seeded by default:

| Trigger | Event Key | When it fires |
|---|---|---|
| **Login** | `LOGIN` | A user successfully authenticates via `POST /api/auth/login/` |
| **Logout** | `LOGOUT` | A user calls `POST /api/auth/logout/` |

When a trigger fires, the system:
1. Looks up all **enabled** templates for that trigger
2. Renders each template body with user variables (`{{name}}`, `{{email}}`, `{{phone}}`)
3. Dispatches each channel **independently** — one failure does not block the others
4. Logs success or failure for every dispatch

Additional triggers can be added from the Django admin or by creating a new `Trigger` record via the API.

---

## Deployment

### Backend — Render

1. Create a new **Web Service** on [render.com](https://render.com) pointing to the `backend/` directory.
2. Set **Build command:**
   ```
   pip install -r requirements.txt && python manage.py migrate && python manage.py seed_triggers
   ```
3. Set **Start command:**
   ```
   gunicorn config.wsgi:application
   ```
4. Add a **PostgreSQL** database from the Render dashboard.
5. Set all environment variables from the Backend `.env` section above.
6. Set `DEBUG=False` and add the Render domain to `ALLOWED_HOSTS`.

### Frontend — Vercel

1. Import the repository on [vercel.com](https://vercel.com).
2. Set **Root directory** to `frontend/`.
3. Add the environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://<your-render-backend>.onrender.com/api
   ```
4. Deploy — Vercel auto-detects Next.js and builds it.

---

## Testing

### Setup sandbox credentials

Before testing real notifications, add your sandbox credentials to `backend/.env`:

| Channel | Credential source |
|---|---|
| WhatsApp | [Meta for Developers](https://developers.facebook.com) → create app → WhatsApp product → API Setup. Add your phone to the test recipient list. Token expires — regenerate when tests fail. |
| Email | [Resend](https://resend.com) → create an API key. Verify your sender domain/email address. |
| Web Push | [OneSignal](https://onesignal.com) → create a Web app → copy App ID and REST API Key. |

### Test all three channels

**Step 1 — Log in as admin**
```
http://localhost:3000/login
```

**Step 2 — Create templates**

In the Notification Settings table, click **Configure** for each cell:
- Login / WhatsApp → `Hello {{name}}, you logged in.`
- Login / Email → subject: `Login alert`, body: `Hi {{name}}, you just logged in.`
- Login / Web Push → title: `Login detected`, body: `Welcome back, {{name}}!`

**Step 3 — Test via editor**

Open any configured template → click **▶ Send test** → check the relevant inbox/device.

**Step 4 — Trigger via real login**

Log out, then log back in. The backend will fire all three channels automatically.
Check the Django server terminal for dispatch logs:
```
INFO ... Dispatching 'LOGIN' → WHATSAPP for user 'admin'
INFO ... Dispatching 'LOGIN' → EMAIL for user 'admin'
INFO ... Dispatching 'LOGIN' → WEB_PUSH for user 'admin'
```

**Step 5 — Test disable behaviour**

Open the WhatsApp template editor → toggle **Channel status** to OFF → Save.
Log out and log in again. Verify that only Email and Web Push fire (WhatsApp log line absent).
