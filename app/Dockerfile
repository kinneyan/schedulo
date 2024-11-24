# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY . /app/

# Expose the port the application will run on
EXPOSE 8000

# Default command for the container
CMD ["sh", "-c", "if [ \"$DJANGO_ENV\" = \"production\" ]; then \
  python manage.py migrate && \
  gunicorn --bind 0.0.0.0:8000 --workers 3 app.wsgi:application; \
  else \
  python manage.py migrate && \
  python manage.py runserver 0.0.0.0:8000; \
  fi"]