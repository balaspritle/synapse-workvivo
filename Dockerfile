# Use an official lightweight Python image
FROM --platform=linux/amd64 python:3.11.1-slim

# Set the working directory
WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the FastAPI default port
EXPOSE 8080

# Run FastAPI using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]