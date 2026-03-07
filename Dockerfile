# Stage 1: Build React frontend
FROM node:22 AS build
WORKDIR /app
COPY client/package*.json ./
RUN npm install
COPY client/ .
ENV VITE_API_URL=""
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /server
COPY server/requirements.txt /server/
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ /server/
COPY --from=build /app/dist /server/static_build
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 3 server.wsgi:application"]
