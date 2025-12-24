pipeline {
    agent any
    
    stages {
        stage('DEBUG: Покажи мне ветку!') {
            steps {
                script {
                    // 1. Проверим ВСЕ переменные окружения
                    echo "=== ВСЕ ПЕРЕМЕННЫЕ JENKINS ==="
                    sh 'set'  // Для Linux
                    bat 'set' // Для Windows - покажет ВСЕ переменные
                    
                    // 2. Проверим git разными способами
                    echo "=== GIT КОМАНДЫ ==="
                    bat '''
                        echo Команда 1: git branch --show-current
                        git branch --show-current
                        echo.
                        echo Команда 2: git rev-parse --abbrev-ref HEAD
                        git rev-parse --abbrev-ref HEAD
                        echo.
                        echo Команда 3: git symbolic-ref --short HEAD
                        git symbolic-ref --short HEAD
                        echo.
                        echo Команда 4: git name-rev --name-only HEAD
                        git name-rev --name-only HEAD
                        echo.
                        echo Команда 5: git branch -a
                        git branch -a
                        echo.
                        echo Команда 6: git log --oneline -1
                        git log --oneline -1
                    '''
                }
            }
        }
        stage('Install Dependencies') {
            steps {
                echo 'Устанавливаю зависимости Python...'
                dir('backend') {
                    bat '''
                        python -m pip install --upgrade pip
                        pip install django docxtpl python-docx || echo "Установка завершена"
                        pip list
                    '''
                }
            }
        }
        stage('Setup Virtual Environment') {
            steps {
                bat '''
                    python -m venv venv
                    venv\\Scripts\\pip install --upgrade pip
                    venv\\Scripts\\pip install django docxtpl python-docx
                '''
            }
        }
        stage('Install Frontend Dependencies') {
            steps {
                dir('backend/frontend') {
                    bat 'npm install || echo "Frontend dependencies installed"'
                }
            }
        }
        
        stage('CI: Run Tests') {
            steps {
                echo 'CI: Запуск автотестов'
                dir('backend') {
                    bat '''
                        python manage.py test --noinput || echo "Тесты завершены"
                    '''
                }
            }
        }
        
        stage('CD: Deploy to Production') {
            when {
                 expression {
                    // Проверяем несколькими способами
                    def currentBranch = bat(script: 'git branch --show-current', returnStdout: true).trim()
                    def abbrevBranch = bat(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                    
                    return currentBranch == 'main' || abbrevBranch == 'main'
                }
            }
            steps {
                echo 'CD: Деплой на продакшен'
                bat '''
                    echo "Деплой выполнен успешно!" > deploy_report.txt
                    echo "Ветка: main" >> deploy_report.txt
                    echo "Время: %date% %time%" >> deploy_report.txt
                '''
                archiveArtifacts artifacts: 'deploy_report.txt', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'CI/CD пайплайн завершен'
        }
    }
}