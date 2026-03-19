# API Documentation

## Base URL
- `http://127.0.0.1:8000/api/v1`

## Incident APIs
- `POST /incidents`
  - Create a single incident record.
- `GET /incidents?skip=0&limit=100`
  - Paginated incident list.
- `POST /incidents/upload-csv`
  - Upload CSV file with required columns:
  - `incident_type, dispatch_time, address, longitude, latitude, handling_duration_min, police_unit_count, status`

## Analytics APIs
- `GET /analytics/overview`
- `GET /analytics/type-distribution?top_n=10`
- `GET /analytics/hour-distribution`
- `GET /analytics/daily-trend`
- `GET /analytics/heat-points?max_points=2000`

## Natural Language API
- `GET /nl/status`
  - Returns whether external LLM is enabled and current model name.
- `POST /nl/query`
  - Request body:
  - `{ "question": "What is the recent incident overview?" }`
  - Response body:
  - `{ "answer": "...", "generated_sql": null, "source": "llm|rule-based" }`

## Collaboration APIs
- `POST /collaboration/assignments`
  - Create an assignment for an officer.
  - If a time overlap conflict exists for the same officer, returns `accepted=false` and conflict list.
- `GET /collaboration/assignments`
  - Returns latest assignment records for multi-user operation demonstration.
