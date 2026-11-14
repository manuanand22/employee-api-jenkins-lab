pipeline {
    agent any

    environment {
        IMAGE_NAME = 'employee-api'
        CONTAINER_NAME = 'employee-api-ci'
        APP_PORT = '5001'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    .venv/bin/pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    python3 - <<'PY'
import time
import urllib.request

url = "http://localhost:5001/health"

for attempt in range(15):
    try:
        response = urllib.request.urlopen(url, timeout=3)
        print("Health check response:", response.read().decode())
        print("Application deployed successfully!")
        break
    except Exception as error:
        print(f"Attempt {attempt + 1}: {error}")
        time.sleep(2)
else:
    raise SystemExit("Application health check failed")
PY
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check the stage logs.'
        }
    }
}
