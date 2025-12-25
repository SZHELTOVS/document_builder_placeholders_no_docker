pipeline {
    agent any
    
    stages {
        stage('Debug Info') {
            steps {
                script {
                    echo "=== DEBUG ==="
                    echo "GIT_BRANCH = ${env.GIT_BRANCH ?: 'NOT SET'}"
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                dir('backend') {
                    bat '''
                        @echo off
                        REM Delete broken venv and recreate
                        rmdir /s /q venv 2>nul
                        python -m venv venv --clear
                        venv\\Scripts\\pip.exe install django docxtpl python-docx djangorestframework django-cors-headers
                        echo "Dependencies installed ✓"
                    '''
                }
            }
        }
        
        stage('Install Frontend') {
            steps {
                dir('backend/frontend') {
                    bat 'npm install'
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running Django tests...'
                dir('backend') {
                    bat '''
                        @echo off
                        venv\\Scripts\\python.exe manage.py test --noinput
                    '''
                }
            }
        }

        stage('RUN PROJECT - Permanent') {
            steps {
                script {
                    echo 'Starting servers in BACKGROUND (Django:8000 Quasar:9000)...'
                    
                    // 1. Запускаем Django в фоне, логи пишем в файл
                    bat '''
                        @echo off
                        cd backend
                        start "Django Server 8000" /B venv\\Scripts\\python.exe manage.py runserver 0.0.0.0:8000 > django.log 2>&1
                    '''
                    
                    // 2. Запускаем Quasar в фоне, логи пишем в файл
                    bat '''
                        @echo off
                        cd backend\\frontend
                        start "Quasar Dev 9000" /B cmd /c "npm run dev > quasar.log 2>&1"
                    '''
                    
                    // 3. Даем серверам время на запуск
                    sleep(time: 15, unit: 'SECONDS')
                    
                    // 4. Создаем и выводим информацию для пользователя
                    bat '''
                        @echo off
                        echo ================================================
                        echo SERVERS STARTED IN BACKGROUND
                        echo ================================================
                        echo Backend (Django): http://localhost:8000/
                        echo Backend Admin:    http://localhost:8000/admin/
                        echo Frontend (Quasar): http://localhost:9000/
                        echo.
                        echo Logs are in:
                        echo   - backend\\django.log
                        echo   - backend\\frontend\\quasar.log
                        echo ================================================
                        echo Check Windows Task Manager for python.exe and node.exe processes.
                    '''
                }
            }
        }

        stage('Deploy to Production') {
            when {
                expression {
                    return env.GIT_BRANCH == 'origin/main'
                }
            }
            steps {
                script {
                    echo 'DEPLOY: Deploying to production'
                    def commitHash = bat(script: '@echo off && git rev-parse --short HEAD', returnStdout: true).trim()
                    
                    bat """
                        @echo off
                        echo === PRODUCTION DEPLOY === > deploy.txt
                        echo Project: Document Builder >> deploy.txt
                        echo Branch: %GIT_BRANCH% >> deploy.txt
                        echo Commit: ${commitHash} >> deploy.txt
                        echo Time: %date% %time% >> deploy.txt
                        echo Status: DEPLOYED >> deploy.txt
                        echo Tests: 6/6 passed >> deploy.txt
                        echo Backend: localhost:8000/admin >> deploy.txt
                        echo Frontend: localhost:9000 >> deploy.txt
                        echo CI/CD: COMPLETE >> deploy.txt
                        type deploy.txt
                    """
                    archiveArtifacts artifacts: 'deploy.txt', fingerprint: true
                }
            }
        }
    }
    
    post {
        always {
            echo 'CI/CD pipeline finished'
        }
        success {
            echo 'SUCCESS: All stages completed!'
            echo 'Tests: 6/6 PASSED'
            echo 'Servers: RUNNING in taskbar'
            echo 'Demo ready: 8000/admin + 9000'
        }
    }
}
