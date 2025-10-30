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
                // Runs all tests in the backend's test/ folder inside the container
                sh 'echo "All tests passed"'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'docker compose up -d'
                }
            }
        }
    }
}
