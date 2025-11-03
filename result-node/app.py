import os
import psycopg
import psycopg.rows
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Database Setup ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgresdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")

conn_string = f"host='{DB_HOST}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASS}'"

# --- FastAPI Application ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_results(request: Request):
    conn = None
    try:
        conn = psycopg.connect(conn_string)
        
        # Force the isolation level
        conn.isolation_level = psycopg.IsolationLevel.READ_COMMITTED
        
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute("SELECT timestamp, equation, answer, time_ms FROM calculations ORDER BY id DESC LIMIT 50")
            results = cur.fetchall()

        # --- THIS IS THE NEW DEBUGGING LINE ---
        print(f"Data found: {results}")
        # --- END OF DEBUGGING LINE ---

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "results": results, "error": None}
        )
    except Exception as e:
        error_message = f"Error fetching data: {e}"
        print(error_message)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "results": [], "error": error_message}
        )
    finally:
        if conn:
            conn.close()

@app.get("/healthz")
def health_check():
    # Health check for the initContainer
    return {"status": "ok"}


