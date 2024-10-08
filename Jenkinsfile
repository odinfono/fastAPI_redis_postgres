pipeline {
    agent any

    environment {
        DATABASE_URL = 'postgresql://postgres:password@localhost/dbname'
        REDIS_URL = 'redis://localhost:6379/0'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs() 
            }
        }

        stage('Clone repository') {
            steps {
                git branch: 'main', url: 'https://github.com/odinfono/fastAPI_redis_postgres.git'
            }
        }
        
        stage('Set up environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest httpx aiosqlite pytest-asyncio
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '. venv/bin/activate && pytest'
            }
        }

        stage('Run Application') {
            steps {
                sh '. venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000'
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
