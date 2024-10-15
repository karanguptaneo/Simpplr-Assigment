# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Add a bash script to run elasticsearch_setup.py with retries
RUN echo '#!/bin/bash\n' \
    'attempt=0\n' \
    'until [ $attempt -ge 5 ]\n' \
    'do\n' \
    '   python apps/elasticsearch_setup.py && break\n' \
    '   attempt=$((attempt+1))\n' \
    '   echo "Retrying in 4 seconds... ($attempt/5)"\n' \
    '   sleep 4\n' \
    'done\n' > /usr/src/app/run_elasticsearch_setup.sh

# Make the bash script executable
RUN chmod +x /usr/src/app/run_elasticsearch_setup.sh

# Expose the API port
EXPOSE 8000

# Command to run the setup script and then start the FastAPI server
CMD ["/bin/bash", "-c", "/usr/src/app/run_elasticsearch_setup.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
