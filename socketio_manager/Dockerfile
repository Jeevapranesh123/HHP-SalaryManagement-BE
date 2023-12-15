# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/backend

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY app app
COPY socketio_manager socketio_manager
COPY .env .

# Expose the port the app runs on
EXPOSE 80

# Run the application
CMD ["uvicorn", "socketio_manager.main:SocketServer", "--host", "0.0.0.0", "--port", "80"]
