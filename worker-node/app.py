import os
import time
import psycopg
from fastapi import FastAPI, Request
from prometheus_client import start_http_server, Histogram
from contextlib import asynccontextmanager

# --- Prometheus Metrics ---
# Create a Histogram to track calculation duration
CALCULATION_DURATION = Histogram(
    'worker_calculation_duration_seconds',
    'Time taken to solve a math calculation'
)

# --- FastAPI Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs ON STARTUP
    print("FastAPI startup: Starting Prometheus metrics server on port 8001")
    start_http_server(8001, '0.0.0.0')
    yield
    # This code runs ON SHUTDOWN (if needed)
    print("FastAPI shutdown.")

# --- Database Setup ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")

conn_string = f"host='{DB_HOST}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASS}'"

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    conn = None
    try:
        # Use a new connection for the init
        with psycopg.connect(conn_string) as conn:
            # Use an explicit transaction
            with conn.transaction():
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS calculations (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMPTZ DEFAULT NOW(),
                        equation TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        time_ms REAL
                    )
                """)
        print("Database table 'calculations' initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

# Initialize the database on startup
init_db()

# --- FastAPI Application ---
# Tell FastAPI to use our new lifespan event
app = FastAPI(lifespan=lifespan)

@app.post("/calculate")
async def calculate(request: Request):
    """Solves a math equation from a POST request and saves it to the DB."""
    data = await request.json()
    equation_str = data.get("equation")

    if not equation_str:
        return {"error": "No equation provided"}, 400

    start_time = time.perf_counter()

    try:
        # Safely evaluate the math expression
        answer = eval(equation_str, {"__builtins__": {}}, {})
    except Exception as e:
        answer = f"Error: {e}"

    end_time = time.perf_counter()
    time_taken_ms = (end_time - start_time) * 1000

    # Observe the duration for Prometheus
    CALCULATION_DURATION.observe((end_time - start_time))

    # Save to database
    try:
        # Use a new connection for the insert
        with psycopg.connect(conn_string) as conn:
            # Use an explicit transaction
            with conn.transaction():
                conn.execute(
                    "INSERT INTO calculations (equation, answer, time_ms) VALUES (%s, %s, %s)",
                    (equation_str, str(answer), time_taken_ms)
                )

        print(f"Solved: {equation_str} = {answer} (in {time_taken_ms:.2f} ms)")
        return {"answer": str(answer), "time_ms": time_taken_ms}

    except Exception as e:
        print(f"Error saving to database: {e}")
        return {"error": f"Error saving to database: {e}"}, 500

@app.get("/healthz")
def health_check():
    # Health check for the initContainer
    return {"status": "ok"}
