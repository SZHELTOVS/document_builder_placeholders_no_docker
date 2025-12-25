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
                    echo "Checking if docker-compose.yml exists..."
                    if exist docker-compose.yml (
                        echo "✓ docker-compose.yml found"
                    ) else (
                        echo "✗ docker-compose.yml NOT FOUND!"
                        exit 1
                    )
                '''
            }
        }
        
        stage('Cleanup Docker') {
            steps {
                bat '''
                    @echo off
                    echo === QUICK CLEANUP ===
                    
                    echo "1. Stopping containers (FORCE)..."
                    docker-compose down -f 2>nul || echo "No compose project found"
                    
                    echo "2. Done!"
                '''
            }
        }
        
        stage('Build Images') {
            steps {
                script {
                    try {
                        bat '''
                            @echo off
                            echo "1. Building backend..."
                            docker-compose build backend
                        '''
                    } catch (Exception e) {
                        error "Backend build failed: ${e.getMessage()}"
                    }
                    
                    try {
                        bat '''
                            @echo off
                            echo "2. Building frontend..."
                            docker-compose build frontend
                        '''
                    } catch (Exception e) {
                        echo "Warning: Frontend build failed: ${e.getMessage()}"
                        echo "Will try to start without frontend rebuild"
                    }
                    
                    echo "Build stage completed"
                }
            }
        }
        
        stage('Start Services') {
            steps {
                bat '''
                    @echo off
                    echo === STARTING SERVICES ===
                    
                    echo "Starting all services..."
                    docker-compose up -d --force-recreate
                    
                    echo "Waiting for startup (30 seconds)..."
                    timeout /t 30 /nobreak >nul
                    
                    echo "Container status:"
                    docker-compose ps
                    
                    echo "Checking logs briefly:"
                    echo "Backend logs (last 5 lines):"
                    docker-compose logs --tail=5 backend 2>nul || echo "Cannot get backend logs yet"
                '''
            }
        }
        
        stage('Verify Services') {
            steps {
                script {
                    sleep(time: 10, unit: 'SECONDS')
                    
                    bat '''
                        @echo off
                        echo === VERIFYING SERVICES ===
                        
                        echo "1. Checking PostgreSQL..."
                        docker-compose exec -T postgres pg_isready -U user -d document_builder && (
                            echo "PostgreSQL is ready"
                        ) || (
                            echo "PostgreSQL is not ready"
                            echo "Postgres logs:"
                            docker-compose logs --tail=10 postgres
                        )
                        
                        echo.
                        echo "2. Checking backend (Django)..."
                        curl --max-time 20 --retry 3 --retry-delay 5 --retry-max-time 60 -f http://localhost:8000/ && (
                            echo "Backend is running at http://localhost:8000/"
                        ) || (
                            echo "Backend is not responding"
                            echo "Checking backend logs..."
                            docker-compose logs --tail=20 backend
                        )
                        
                        echo.
                        echo "3. Checking frontend (Quasar)..."
                        curl --max-time 20 --retry 2 --retry-delay 5 -f http://localhost:9000/ && (
                            echo "Frontend is running at http://localhost:9000/"
                        ) || (
                            echo "Frontend is not responding (might still be starting)"
                            echo "Frontend can take 1-2 minutes to build on first run..."
                            docker-compose logs --tail=10 frontend
                        )
                    '''
                }
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
                    
                    echo "CONTAINER STATUS:" >> docker_report.txt
                    docker-compose ps >> docker_report.txt 2>&1
                    echo >> docker_report.txt
                    
                    echo "DOCKER IMAGES:" >> docker_report.txt
                    docker images | findstr "docbuilder" >> docker_report.txt 2>&1 || echo "No docbuilder images found" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "AVAILABLE SERVICES:" >> docker_report.txt
                    echo "Backend (Django):     http://localhost:8000/" >> docker_report.txt
                    echo "Django Admin:        http://localhost:8000/admin/" >> docker_report.txt
                    echo "Frontend (Quasar):   http://localhost:9000/" >> docker_report.txt
                    echo "Database (Postgres): localhost:5433" >> docker_report.txt
                    echo "  Database: document_builder" >> docker_report.txt
                    echo "  User: user" >> docker_report.txt
                    echo "  Password: password" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "LOGS (last 3 lines each):" >> docker_report.txt
                    echo "Postgres:" >> docker_report.txt
                    docker-compose logs --tail=3 postgres >> docker_report.txt 2>&1 || echo "No postgres logs" >> docker_report.txt
                    echo >> docker_report.txt
                    echo "Backend:" >> docker_report.txt
                    docker-compose logs --tail=3 backend >> docker_report.txt 2>&1 || echo "No backend logs" >> docker_report.txt
                    echo >> docker_report.txt
                    echo "Frontend:" >> docker_report.txt
                    docker-compose logs --tail=3 frontend >> docker_report.txt 2>&1 || echo "No frontend logs" >> docker_report.txt
                    echo >> docker_report.txt
                    
                    echo "Report saved to docker_report.txt"
                    echo.
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
                echo "FINAL CONTAINER STATUS:"
                docker-compose ps
                echo.
                echo "SERVICES:"
                echo "Backend (Django):  http://localhost:8000/"
                echo "Frontend (Quasar): http://localhost:9000/"
                echo "Database:         localhost:5433"
                echo.
                echo "LOGS: docker-compose logs -f"
                echo "STOP: docker-compose down"
            '''
        }
        success {
            echo 'SUCCESS: Docker deployment completed'
        }
        failure {
            echo 'ERROR: Pipeline failed'
            bat '''
                @echo off
                echo "TROUBLESHOOTING INFO:"
                echo "All containers:"
                docker ps -a
                echo.
                echo "docker-compose logs:"
                docker-compose logs --tail=50 2>nul || echo "Cannot get logs"
                echo.
                echo "Cleaning up..."
                docker-compose down 2>nul
            '''
        }
    }
}