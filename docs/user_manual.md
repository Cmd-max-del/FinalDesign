# User Manual

## 1. Start Backend
1. Create Python virtual environment and activate it.
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Copy env file:
   - `copy backend\\.env.example backend\\.env`
4. Initialize MySQL schema using `data/sql/init_mysql.sql`.
5. Start backend:
   - `uvicorn app.main:app --reload --app-dir backend`

## 2. Prepare Data
- Option A: upload CSV via `/api/v1/incidents/upload-csv`.
- Option B: run sample script:
  - `python backend/scripts/seed_sample_data.py`

## 3. Start Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
4. Open browser at `http://127.0.0.1:5173`

## 4. Demonstration Suggestion
- Show dashboard overview.
- Show type and trend pages.
- Ask natural language question in assistant page.
- Explain dispatch optimization based on discovered patterns.
