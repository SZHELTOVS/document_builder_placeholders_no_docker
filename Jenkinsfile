pipeline {
    agent any
    
    stages {
        stage('Run Docker') {
            steps {
                bat '''
                    @echo off
                    docker-compose down
                    docker-compose up --build -d
                    timeout /t 30
                    docker-compose ps
                '''
            }
        }
    }
}