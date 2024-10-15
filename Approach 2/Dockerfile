# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the API port
EXPOSE 8080

# Command to run the FastAPI server with a delay
CMD ["sh", "-c", "sleep 30 && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
