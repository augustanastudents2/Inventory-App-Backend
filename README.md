# ASA Inventory App Backend

FastAPI backend for the ASA Inventory Management System, using Supabase as the database.

## Setup

1.  **Clone the repository**
2.  **Install dependencies**: `pip install -r requirements.txt`
3.  **Environment Variables**: Create a `.env` file with:
    ```
    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_anon_key
    SUPABASE_SERVICE_KEY=your_supabase_service_role_key
    ```
4.  **Database**: Run the SQL in `database/database_schema.sql` in your Supabase SQL Editor.
5.  **Run**: `uvicorn main:app --reload`

## Deployment

This backend is ready for deployment on **Render**.
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
