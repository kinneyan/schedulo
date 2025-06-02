# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /server

# Install Python dependencies
COPY requirements.txt /server/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY . /server/

# Expose the port the application will run on
EXPOSE 8000

# Default command for the container
CMD ["sh", "-c", "python manage.py migrate && \
  if [ \"$DJANGO_ENV\" = \"production\" ]; then \
  gunicorn --bind 0.0.0.0:8000 --workers 3 server.wsgi:application; \
  else \
  python manage.py runserver 0.0.0.0:8000; \
  fi"]
