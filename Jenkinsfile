pipeline {
    agent any

    environment {
        DATABASE_URL = 'postgresql://postgres:password@localhost/dbname'
        REDIS_URL = 'redis://localhost:6379/0'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()  // This will clean the workspace before the build starts
            }
        }

        stage('Clone repository') {
            steps {
                git branch: 'main', url: 'https://github.com/odinfono/fastAPI_redis_postgres.git'
            }
        }
        
        stage('Set up environment') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run tests') {
            steps {
                sh '. venv/bin/activate && pytest'
            }
        }

        stage('Run Application') {
            steps {
                sh '. venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
