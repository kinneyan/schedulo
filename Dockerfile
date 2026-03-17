# Stage 1: Build React frontend
FROM node:22.14-slim AS build
WORKDIR /app
COPY client/package*.json ./
RUN npm install
COPY client/ .
ENV VITE_API_URL=""
RUN npm run build && test -f dist/index.html

# Stage 2: Python runtime
FROM python:3.12.9-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /server
COPY server/ /server/
RUN pip install --no-cache-dir .
COPY --from=build /app/dist /server/server/static_build
RUN python manage.py collectstatic --noinput && test -f /server/server/static_build/index.html
RUN adduser --disabled-password --no-create-home appuser
USER appuser
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=server.settings.prod
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} server.wsgi:application"]
