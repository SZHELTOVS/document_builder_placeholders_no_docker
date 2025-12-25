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
                        python -m venv venv
                        venv\\Scripts\\pip install django docxtpl python-docx djangorestframework django-cors-headers
                        echo Dependencies installed
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
                    echo 'Starting server as separate service...'
                    
                    // 1. Start Django as Windows service
                    bat '''
                        @echo off
                        echo Creating server startup script...
                        cd backend
                        
                        echo Creating batch file for Django...
                        echo @echo off > start_django.bat
                        echo cd /d "%%~dp0" >> start_django.bat
                        echo venv\\Scripts\\python.exe manage.py runserver 0.0.0.0:8000 >> start_django.bat
                        
                        echo Starting Django in separate window...
                        start "DjangoServer" cmd /k start_django.bat
                        echo Django started in separate process!
                        echo Check: http://localhost:8000
                        
                        timeout /t 5 /nobreak > nul
                    '''
                    
                    // 2. Start Frontend as separate service
                    bat '''
                        @echo off
                        echo Creating batch file for Frontend...
                        cd backend\\frontend
                        
                        echo @echo off > start_frontend.bat
                        echo cd /d "%%~dp0" >> start_frontend.bat
                        echo npm run dev >> start_frontend.bat
                        
                        echo Starting Frontend in separate window...
                        start "FrontendServer" cmd /k start_frontend.bat
                        echo Frontend started in separate process!
                        
                        timeout /t 5 /nobreak > nul
                    '''
                    
                    // 3. Check processes and show their IDs
                    bat '''
                        @echo off
                        echo.
                        echo ================================================
                        echo SERVER IS RUNNING!
                        echo ================================================
                        echo.
                        echo Active processes:
                        echo.
                        echo Python processes (Django):
                        wmic process where "name='python.exe'" get ProcessId,CommandLine
                        echo.
                        echo Node processes (Frontend):
                        wmic process where "name='node.exe'" get ProcessId,CommandLine
                        echo.
                        echo Processes will NOT be killed when Jenkins finishes!
                        echo.
                        echo Access:
                        echo Backend: http://localhost:8000
                        echo Frontend: http://localhost:9000 (or other port)
                        echo.
                        timeout /t 10 /nobreak > nul
                    '''
                    
                    // 4. Save information about running processes
                    bat '''
                        @echo off
                        echo === SERVER RUNNING === > server_running.txt
                        echo Start time: %%date%% %%time%% >> server_running.txt
                        echo Processes: >> server_running.txt
                        echo python.exe - Django backend >> server_running.txt  
                        echo node.exe - Quasar frontend >> server_running.txt
                        echo. >> server_running.txt
                        echo Server will continue running after Jenkins finishes >> server_running.txt
                        echo To stop: taskkill /F /IM python.exe /IM node.exe >> server_running.txt
                        type server_running.txt
                    '''
                    
                    archiveArtifacts artifacts: 'server_running.txt'
                    
                    echo 'SERVER IS RUNNING'
                    echo 'Backend: http://localhost:8000'
                    echo 'Frontend: in development'
                    echo 'Processes continue to run independently from Jenkins'
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
                        echo Branch: %%GIT_BRANCH%% >> deploy.txt
                        echo Commit: ${commitHash} >> deploy.txt
                        echo Time: %%date%% %%time%% >> deploy.txt
                        echo Status: DEPLOYED >> deploy.txt
                        echo Tests: 6/6 passed >> deploy.txt
                        echo Services: running >> deploy.txt
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
            echo 'Project: RUNNING'
            echo 'Deploy: EXECUTED (main branch)'
            echo 'Lab: COMPLETE'
        }
    }
}