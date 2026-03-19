# Key Module Design

## 1. Data Layer
- MySQL table: `incidents`
- ORM model: `backend/app/models/incident.py`
- Supports both CSV import and generated sample data script.

## 2. Service Layer
- `analytics_service.py` encapsulates reusable stats logic.
- Outputs frontend-friendly list structures for ECharts.

## 3. API Layer
- `routes_incidents.py`: CRUD subset + CSV upload.
- `routes_analytics.py`: overview, distribution, trend, heat points.
- `routes_nl.py`: natural language query with optional LLM call.

## 4. Frontend Layer
- Vue3 + Router multi-page dashboard.
- Reusable chart component `EChartPanel.vue`.
- Axios client for backend integration.

## 5. Expansion Plan
- Add auth and RBAC roles.
- Add district-level spatial aggregation and map overlay.
- Add forecast model for high-frequency incidents.
