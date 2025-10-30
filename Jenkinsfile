pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker compose build'
            }
        }
        stage('Test') {
            steps {
                // sh 'cd backend && cd test && uv run python -m pytest test_courses.py -v'
                echo 'Test stage skipped'
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker compose up -d'
            }
        }
    }
}
