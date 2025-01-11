# Use the official Python image
FROM python:3.10.8

# Set environment variables
ENV FLASK_ENV=development
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=1

# Set the working directory in the container
WORKDIR /project

# Copy requirements and install dependencies
COPY requirements-docker.txt .
RUN apt-get update && apt-get install -y wget tar unzip && \
    mkdir -p /app/scripts && \
    chmod -R 755 /app/scripts && \
    pip install --upgrade pip && pip install --timeout 120 --no-cache-dir -r requirements-docker.txt &&\
    pip install watchdog

# Copy the project files
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]

