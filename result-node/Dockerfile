# Use a lightweight, efficient base image
FROM python:3.10-alpine

# Install build dependencies
RUN apk add --no-cache postgresql-dev build-base

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code AND the templates directory
COPY app.py .
COPY templates ./templates/

# Expose port 8080
EXPOSE 8080

# Command to run the application using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
