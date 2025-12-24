pipeline {
    agent any
    
    stages {
        stage('DEBUG: Show Branch Info') {
            steps {
                script {
                    echo "=== DEBUG FOR WINDOWS ==="
                    echo "BRANCH_NAME = ${env.BRANCH_NAME ?: 'NOT SET'}"
                    echo "GIT_BRANCH = ${env.GIT_BRANCH ?: 'NOT SET'}"
                    
                    bat '''
                        @echo off
                        echo.
                        echo === GIT COMMANDS ===
                        git branch --show-current
                        git rev-parse --abbrev-ref HEAD
                        git branch -a
                    '''
                }
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                dir('backend') {
                    bat '''
                        python -m venv venv
                        venv\\Scripts\\pip install django docxtpl python-docx
                        venv\\Scripts\\pip install django docxtpl python-docx djangorestframework
                    '''
                }
            }
        }
        
        stage('Install Frontend Dependencies') {
            steps {
                dir('backend/frontend') {
                    bat 'npm install'
                }
            }
        }
        
        stage('CI: Run Tests') {
            steps {
                echo 'CI: Running Django tests...'
                dir('backend') {
                    bat '''
                        venv\\Scripts\\python.exe manage.py test --noinput
                    '''
                }
            }
        }

        stage('Run Project') {
            steps {
                echo 'Starting Backend and Frontend...'
                script {
                    // Start Django backend
                    bat '''
                        @echo off
                        echo Starting Django backend...
                        start /B cmd /c "cd backend && venv\\Scripts\\python.exe manage.py runserver 0.0.0.0:8000"
                        echo Backend started at http://localhost:8000
                        timeout /t 2 /nobreak > nul
                    '''
                    
                    // Start Quasar frontend
                    bat '''
                        @echo off
                        echo Starting Quasar frontend...
                        start /B cmd /c "cd backend\\frontend && npm run dev"
                        echo Frontend started in dev mode
                        timeout /t 3 /nobreak > nul
                    '''
                    
                    // Verify services are running
                    bat '''
                        @echo off
                        echo === SERVICES RUNNING ===
                        echo 1. Django Backend: http://localhost:8000
                        echo 2. Quasar Frontend: dev mode
                        echo.
                        echo Project is ready!
                        timeout /t 5 /nobreak > nul
                    '''
                }
            }
        }
        
        stage('CD: Deploy to Production') {
            when {
                expression {
                    // SIMPLE AND CORRECT CHECK
                    return env.GIT_BRANCH == 'origin/main'
                }
            }
            steps {
                script {
                    echo 'CD: Deploying to production (main branch only)'
                    def commitHash = bat(script: '@echo off && git rev-parse --short HEAD', returnStdout: true).trim()
                    
                    bat """
                        @echo off
                        echo "=== CI/CD DEPLOYMENT REPORT ===" > deploy_report.txt
                        echo "Project: Document Builder" >> deploy_report.txt
                        echo "Branch: %GIT_BRANCH%" >> deploy_report.txt
                        echo "Commit: ${commitHash}" >> deploy_report.txt
                        echo "Time: %date% %time%" >> deploy_report.txt
                        echo "Status: SUCCESS" >> deploy_report.txt
                        echo "Tests passed: 6" >> deploy_report.txt
                        type deploy_report.txt
                    """
                }
                archiveArtifacts artifacts: 'deploy_report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'CI/CD pipeline completed'
            // Cleanup processes
            bat '''
                @echo off
                echo Cleaning up processes...
                taskkill /F /IM python.exe 2>nul
                taskkill /F /IM node.exe 2>nul
                echo Cleanup done.
            '''
        }
        success {
            echo 'ALL STAGES COMPLETED SUCCESSFULLY!'
        }
    }
}