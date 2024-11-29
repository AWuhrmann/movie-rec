# Movie recommendations for ADA@EPFL

## Project Structure
- `frontend/`: Svelte application
- `backend/`: Python FastAPI backend

## Development

### Frontend
```bash
cd frontend
npm install
npm run dev -- --open
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```