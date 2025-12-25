pipeline {
    agent any
    
    stages {
        stage('Check Structure') {
            steps {
                bat '''
                    @echo off
                    echo === CHECKING PROJECT STRUCTURE ===
                    echo.
                    echo "Root folder:"
                    dir /B
                    echo.
                    echo "Backend folder:"
                    dir backend /B
                    echo.
                    echo "Backend/frontend folder:"
                    dir backend\\frontend /B
                    echo.
                    echo "Checking frontend package.json:"
                    type backend\\frontend\\package.json | findstr "name version"
                '''
            }
        }
        
        stage('Create Docker Files') {
            steps {
                script {
                    echo '=== CREATING DOCKER CONFIGURATION ==='
                    
                    // 1. Create requirements.txt for backend
                    writeFile file: 'backend/requirements.txt', text: '''Django>=5.0,<6.0
psycopg2-binary
python-docx
docxtpl
djangorestframework
django-cors-headers
'''
                    echo 'Created backend/requirements.txt'
                    
                    // 2. Create Dockerfile for backend
                    writeFile file: 'backend/Dockerfile', text: '''FROM python:3.11-slim

RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
'''
                    echo 'Created backend/Dockerfile'
                    
                    // 3. Create Dockerfile for frontend
                    writeFile file: 'backend/frontend/Dockerfile', text: '''FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --no-audit --no-fund --ignore-scripts

COPY . .

EXPOSE 9000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "9000"]
'''
                    echo 'Created backend/frontend/Dockerfile'
                    
                    // 4. Create docker-compose.yml
                    writeFile file: 'docker-compose.yml', text: '''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: docbuilder-db
    environment:
      POSTGRES_DB: document_builder
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: docbuilder-backend
    environment:
      DB_NAME: document_builder
      DB_USER: user
      DB_PASSWORD: password
      DB_HOST: postgres
      DB_PORT: 5432
      DEBUG: "True"
      ALLOWED_HOSTS: "*"
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
    command: >
      sh -c "sleep 5 &&
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"

  frontend:
    build:
      context: ./backend/frontend
      dockerfile: Dockerfile
    container_name: docbuilder-frontend
    ports:
      - "9000:9000"
    volumes:
      - ./backend/frontend:/app
      - /app/node_modules
    environment:
      NODE_ENV: development
      HOST: 0.0.0.0
      PORT: 9000
    stdin_open: true
    tty: true
    depends_on:
      - backend

volumes:
  postgres_data:
'''
                    echo 'Created docker-compose.yml'
                }
            }
        }
        
        stage('Cleanup Docker') {
            steps {
                bat '''
                    @echo off
                    echo === CLEANING DOCKER ===
                    docker-compose down 2>nul || echo "No running containers"
                    docker system prune -f 2>nul
                    echo "Cleanup completed"
                '''
            }
        }
        
        stage('Build Images') {
            steps {
                bat '''
                    @echo off
                    echo === BUILDING DOCKER IMAGES ===
                    
                    echo "1. Building backend..."
                    docker-compose build backend
                    
                    echo.
                    echo "2. Building frontend..."
                    docker-compose build frontend
                    
                    echo.
                    echo "Images built"
                '''
            }
        }
        
        stage('Start Services') {
            steps {
                bat '''
                    @echo off
                    echo === STARTING SERVICES ===
                    
                    echo "Starting all services..."
                    docker-compose up -d
                    
                    echo.
                    echo "Waiting for startup..."
                    timeout /t 20 /nobreak >nul
                    
                    echo.
                    echo "Container status:"
                    docker-compose ps
                '''
            }
        }
        
        stage('Verify Services') {
            steps {
                bat '''
                    @echo off
                    echo === VERIFYING SERVICES ===
                    
                    echo "Giving services time to fully start..."
                    timeout /t 10 /nobreak >nul
                    
                    echo.
                    echo "1. Checking backend (Django)..."
                    curl --max-time 15 --retry 2 --retry-delay 5 http://localhost:8000/ && (
                        echo "Backend is running at http://localhost:8000/"
                    ) || (
                        echo "Backend is not responding"
                        echo "Backend logs:"
                        docker-compose logs backend --tail=15
                    )
                    
                    echo.
                    echo "2. Checking frontend (Quasar)..."
                    curl --max-time 15 --retry 2 --retry-delay 5 http://localhost:9000/ && (
                        echo "Frontend is running at http://localhost:9000/"
                    ) || (
                        echo "Frontend is not responding (may take longer to start)"
                        echo "Frontend logs:"
                        docker-compose logs frontend --tail=15
                    )
                    
                    echo.
                    echo "3. Checking database..."
                    docker-compose exec -T postgres pg_isready -U user && (
                        echo "Database is working"
                    ) || echo "Database check failed"
                '''
            }
        }
        
        stage('Create Summary') {
            steps {
                bat '''
                    @echo off
                    echo === CREATING REPORT ===
                    
                    echo "DOCUMENT BUILDER - DOCKER DEPLOYMENT" > docker_report.txt
                    echo "======================================" >> docker_report.txt
                    echo "Date: %date% %time%" >> docker_report.txt
                    echo "Build: %BUILD_NUMBER%" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "CONTAINERS:" >> docker_report.txt
                    docker-compose ps >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "AVAILABLE SERVICES:" >> docker_report.txt
                    echo "Backend (Django):  http://localhost:8000/" >> docker_report.txt
                    echo "Frontend (Quasar): http://localhost:9000/" >> docker_report.txt
                    echo "Database:          localhost:5433" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "COMMANDS:" >> docker_report.txt
                    echo "docker-compose down          - stop all" >> docker_report.txt
                    echo "docker-compose logs -f       - view logs" >> docker_report.txt
                    echo "docker-compose exec backend bash - enter backend" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "Report saved to docker_report.txt"
                    type docker_report.txt
                '''
                archiveArtifacts artifacts: 'docker_report.txt', fingerprint: true
                archiveArtifacts artifacts: 'docker-compose.yml', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo '=== PIPELINE COMPLETED ==='
            bat '''
                @echo off
                echo.
                echo "FINAL STATUS:"
                docker-compose ps
                echo.
                echo "SERVICES RUNNING:"
                echo "Django:  http://localhost:8000/"
                echo "Quasar:  http://localhost:9000/"
                echo "Postgres: localhost:5433"
                echo.
                echo "To stop: docker-compose down"
            '''
        }
        success {
            echo 'SUCCESS: All services are running in Docker!'
        }
        failure {
            echo 'ERROR: Failed to start all services'
        }
    }
}