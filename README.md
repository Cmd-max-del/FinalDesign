# Police Incident Visual Analytics System

This project is a graduation-design-ready prototype for multi-dimensional police incident analytics.

## Tech Stack
- Backend: FastAPI, SQLAlchemy, MySQL
- Frontend: Vue3, Vite, ECharts, Axios
- Data: CSV + MySQL
- AI extension: LLM API (optional)

## Project Structure
- `backend/`: API service and analytics logic
- `frontend/`: visualization dashboard
- `data/sql/`: MySQL initialization scripts
- `data/sample/`: sample incident CSV
- `docs/`: API doc, module design, user manual
- `notebooks/`: data analysis notebook

## Quick Start
1. Prepare MySQL and execute `data/sql/init_mysql.sql`.
2. Backend setup:
   - `pip install -r backend/requirements.txt`
   - `copy backend\\.env.example backend\\.env`
   - `uvicorn app.main:app --reload --app-dir backend`
3. Frontend setup:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

## LLM Integration (Optional)
1. Configure `backend/.env`:
   - `OPENAI_API_KEY=<your_api_key>`
   - `OPENAI_BASE_URL=https://api.openai.com/v1` (or your OpenAI-compatible endpoint)
   - `OPENAI_MODEL=gpt-4o-mini`
2. Restart backend after changing `.env`.
3. Verify status:
   - API: `GET /api/v1/nl/status`
   - Frontend Assistant page shows `LLM 已启用` or `LLM 未启用`.
4. Query API:
   - `POST /api/v1/nl/query`
   - Response field `source` equals `llm` or `rule-based`.

## Core Features
- Incident data import and management
- Type/time/trend/spatial analytics APIs
- Dashboard with ECharts visualizations
- Natural language analytics query entry
- Multi-user dispatch collaboration and conflict detection demo

## Suggested Thesis Chapters
- Requirement Analysis and System Feasibility
- Architecture and Key Module Design
- Data Cleaning and Analytics Methodology
- Frontend Visualization and Interaction Design
- System Testing and Performance Evaluation
- Conclusion and Future Work
