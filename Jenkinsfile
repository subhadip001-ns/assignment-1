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
                // Runs pytest in the backend service's test directory
                sh 'docker compose run --rm backend uv run python -m pytest test/test_courses.py -v'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    if (!fileExists('.env')) {
                        sh 'touch .env'
                    }
                    sh 'echo "POSTGRES_PASSWORD=postgrespass" >> .env'
                    sh 'echo "POSTGRES_DB=student_course_enrollment_db" >> .env'
                    sh 'echo "DATABASE_URL=postgresql://postgres:postgrespass@localhost:5432/student_course_enrollment_db" >> .env'
                    sh 'docker compose up -d'
                }
            }
        }
    }
}
