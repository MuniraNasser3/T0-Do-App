# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy all the project files to the container
COPY . .

RUN apt-get update && apt-get install -y netcat-openbsd


# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8000

COPY wait-for-postgres.sh .
CMD ["./wait-for-postgres.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


