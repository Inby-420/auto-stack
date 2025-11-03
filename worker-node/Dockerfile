# --- STAGE 1: The "Builder" ---
# We use a full Python image that has all the build tools
FROM python:3.10-alpine AS builder

# Install the build-time dependencies
RUN apk add --no-cache postgresql-dev build-base

# Set up a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy requirements and install them into the virtual env
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: The "Final" Image ---
# We start from a fresh, clean, tiny Python image
FROM python:3.10-alpine

# Install *only* the one library needed to *run* the app
RUN apk add --no-cache libpq

# Set the working directory
WORKDIR /app

# Copy the *compiled* virtual environment from the "builder" stage
COPY --from=builder /venv /venv

# Copy your application code
COPY app.py .

# Set the path to use the Python from the virtual environment
ENV PATH="/venv/bin:$PATH"

# Expose the correct port
EXPOSE 8525
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8525"]

