# Use a lightweight, efficient base image
FROM python:3.10-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the application code
COPY app.py .

# Command to run the application
CMD ["python", "app.py"]
