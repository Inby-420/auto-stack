# Use a lightweight, efficient base image
FROM python:3.10-alpine

# Install build dependencies
RUN apk add --no-cache postgresql-dev build-base

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Expose port 8525 (everyone uses 8080 xD)
EXPOSE 8525

# Command to run the application using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8525"]
