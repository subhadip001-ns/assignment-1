pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'day-4', url: 'https://github.com/subhadip001-ns/assignment-1.git'
            }
        }
        stage('Build') {
            steps {
                sh 'docker compose build'
            }
        }
        stage('Test') {
            steps {
                sh 'cd backend && cd test && uv run python -m pytest test_courses.py -v'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker compose up -d'
            }
        }
    }
}
