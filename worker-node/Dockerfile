# --- STAGE 1: The Builder ---
# Use a full-featured image to build our dependencies
FROM python:3.10-alpine AS builder

# Install build-time dependencies for compiling psycopg
RUN apk add --no-cache postgresql-dev build-base

# Create a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: The Final, Lean Image ---
# Start from a clean, lightweight image
FROM python:3.10-alpine

RUN apk add --no-cache libpq

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /venv /venv

# Copy the application code
COPY app.py .

# Set the PATH to use the venv
ENV PATH="/venv/bin:$PATH"

# Expose the correct ports
EXPOSE 8525
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8525"]
