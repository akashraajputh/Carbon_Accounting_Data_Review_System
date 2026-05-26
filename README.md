# Carbon Accounting Data Review Prototype

This repository contains a Django REST backend and a React frontend for ingesting realistic enterprise data from SAP, utility electricity bills, and corporate travel exports.

## Setup

### Backend

1. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```
2. Apply migrations:
   ```powershell
   cd backend
   python manage.py migrate
   python manage.py loaddata initial_tenants.json  # optional if data fixture exists
   ```
3. Create a superuser if needed:
   ```powershell
   python manage.py createsuperuser
   ```
4. Run the backend:
   ```powershell
   python manage.py runserver
   ```

### Frontend

1. Install dependencies:
   ```powershell
   cd frontend
   npm install
   ```
2. Start the UI:
   ```powershell
   npm run dev
   ```

### Usage

- Upload CSV files under `samples/` using the React UI.
- Review `pending` records, approve or reject rows, and inspect flagged issues.

## Deployment

### Render (backend)

1. Create a new Render web service.
2. Set the repo root to this repository and the build command to:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Set the start command to:


   ```bash
   bash start-backend.sh
   ```
   This script runs Django migrations before launching Gunicorn.
4. Add environment variables:
   - `DJANGO_SECRET_KEY`: a secure secret value
   - `DEBUG`: `0`
   - `VITE_API_BASE`: not required for backend

### Vercel (frontend)

1. Deploy the `frontend` directory as a separate Vercel project.
2. Ensure Vercel uses `npm install` and `npm run build` in the `frontend` folder.
3. Add an environment variable in Vercel:
   - `VITE_API_BASE`: `https://carbon-accounting-data-review-system-9.onrender.com/api`

### Notes

- The frontend reads `VITE_API_BASE` at build time. Set it to your Render backend API URL.
- `backend/requirements.txt` now includes `gunicorn` so the backend can run in production on Render.

## Notes

- The backend accepts CSV uploads for `sap`, `utility`, and `travel` sources.
- The model keeps raw source payload, normalized quantities, scope type, and approval state.
- Documentation files include `MODEL.md`, `DECISIONS.md`, `TRADEOFFS.md`, and `SOURCES.md`.

