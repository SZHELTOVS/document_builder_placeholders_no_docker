pipeline {
    agent any
    
    stages {
        stage('Check Structure') {
            steps {
                bat '''
                    @echo off
                    echo === ПРОВЕРКА СТРУКТУРЫ ===
                    echo.
                    echo "Корневая папка:"
                    dir /B
                    echo.
                    echo "Папка backend:"
                    dir backend /B
                    echo.
                    echo "Папка backend/frontend:"
                    dir backend\\frontend /B
                    echo.
                    echo "Проверяю package.json фронтенда:"
                    type backend\\frontend\\package.json | findstr "name version"
                '''
            }
        }
        
        stage('Create Docker Files') {
            steps {
                script {
                    echo '=== СОЗДАЮ DOCKER КОНФИГУРАЦИЮ ==='
                    
                    // 1. Создаем requirements.txt для бэкенда
                    writeFile file: 'backend/requirements.txt', text: '''Django>=5.0,<6.0
psycopg2-binary
python-docx
docxtpl
djangorestframework
django-cors-headers
'''
                    echo '✓ Создан backend/requirements.txt'
                    
                    // 2. Создаем Dockerfile для бэкенда
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
                    echo '✓ Создан backend/Dockerfile'
                    
                    // 3. Создаем Dockerfile для фронтенда
                    writeFile file: 'backend/frontend/Dockerfile', text: '''FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --no-audit --no-fund --ignore-scripts

COPY . .

EXPOSE 9000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "9000"]
'''
                    echo '✓ Создан backend/frontend/Dockerfile'
                    
                    // 4. Создаем docker-compose.yml
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
                    echo '✓ Создан docker-compose.yml'
                }
            }
        }
        
        stage('Cleanup Docker') {
            steps {
                bat '''
                    @echo off
                    echo === ОЧИСТКА DOCKER ===
                    docker-compose down 2>nul || echo "Нет запущенных контейнеров"
                    docker system prune -f 2>nul
                    echo "✓ Очистка завершена"
                '''
            }
        }
        
        stage('Build Images') {
            steps {
                bat '''
                    @echo off
                    echo === СОБИРАЮ DOCKER ОБРАЗЫ ===
                    
                    echo "1. Собираю бэкенд..."
                    docker-compose build backend
                    
                    echo.
                    echo "2. Собираю фронтенд..."
                    docker-compose build frontend
                    
                    echo.
                    echo "✓ Образы собраны"
                '''
            }
        }
        
        stage('Start Services') {
            steps {
                bat '''
                    @echo off
                    echo === ЗАПУСКАЮ СЕРВИСЫ ===
                    
                    echo "Запускаю все сервисы..."
                    docker-compose up -d
                    
                    echo.
                    echo "Жду запуска..."
                    timeout /t 20 /nobreak >nul
                    
                    echo.
                    echo "Статус контейнеров:"
                    docker-compose ps
                '''
            }
        }
        
        stage('Verify Services') {
            steps {
                bat '''
                    @echo off
                    echo === ПРОВЕРКА СЕРВИСОВ ===
                    
                    echo "Даю сервисам время на полный запуск..."
                    timeout /t 10 /nobreak >nul
                    
                    echo.
                    echo "1. Проверяю бэкенд (Django)..."
                    curl --max-time 15 --retry 2 --retry-delay 5 http://localhost:8000/ && (
                        echo "✓ Бэкенд работает на http://localhost:8000/"
                    ) || (
                        echo "✗ Бэкенд не отвечает"
                        echo "Логи бэкенда:"
                        docker-compose logs backend --tail=15
                    )
                    
                    echo.
                    echo "2. Проверяю фронтенд (Quasar)..."
                    curl --max-time 15 --retry 2 --retry-delay 5 http://localhost:9000/ && (
                        echo "✓ Фронтенд работает на http://localhost:9000/"
                    ) || (
                        echo "✗ Фронтенд не отвечает (может дольше запускаться)"
                        echo "Логи фронтенда:"
                        docker-compose logs frontend --tail=15
                    )
                    
                    echo.
                    echo "3. Проверяю базу данных..."
                    docker-compose exec -T postgres pg_isready -U user && (
                        echo "✓ База данных работает"
                    ) || echo "⚠ База данных проверка не удалась"
                '''
            }
        }
        
        stage('Create Summary') {
            steps {
                bat '''
                    @echo off
                    echo === СОЗДАЮ ОТЧЕТ ===
                    
                    echo "DOCUMENT BUILDER - DOCKER DEPLOYMENT" > docker_report.txt
                    echo "======================================" >> docker_report.txt
                    echo "Дата: %date% %time%" >> docker_report.txt
                    echo "Сборка: %BUILD_NUMBER%" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "КОНТЕЙНЕРЫ:" >> docker_report.txt
                    docker-compose ps >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "ДОСТУПНЫЕ СЕРВИСЫ:" >> docker_report.txt
                    echo "• Бэкенд (Django):  http://localhost:8000/" >> docker_report.txt
                    echo "• Фронтенд (Quasar): http://localhost:9000/" >> docker_report.txt
                    echo "• База данных:      localhost:5433" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "КОМАНДЫ:" >> docker_report.txt
                    echo "docker-compose down          - остановить все" >> docker_report.txt
                    echo "docker-compose logs -f       - смотреть логи" >> docker_report.txt
                    echo "docker-compose exec backend bash - войти в бэкенд" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "Отчет сохранен в docker_report.txt"
                    type docker_report.txt
                '''
                archiveArtifacts artifacts: 'docker_report.txt', fingerprint: true
                archiveArtifacts artifacts: 'docker-compose.yml', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo '=== ПАЙПЛАЙН ЗАВЕРШЕН ==='
            bat '''
                @echo off
                echo.
                echo "ИТОГОВЫЙ СТАТУС:"
                docker-compose ps
                echo.
                echo "СЕРВИСЫ ЗАПУЩЕНЫ:"
                echo "• Django:  http://localhost:8000/"
                echo "• Quasar:  http://localhost:9000/"
                echo "• Postgres: localhost:5433"
                echo.
                echo "Для остановки: docker-compose down"
            '''
        }
        success {
            echo '✅ УСПЕХ: Все сервисы запущены в Docker!'
        }
        failure {
            echo '❌ ОШИБКА: Не удалось запустить все сервисы'
        }
    }
}