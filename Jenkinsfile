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
            for i in $(seq 1 15); do
                if docker exec ${CONTAINER_NAME} python -c \
                "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3).read().decode())"
                then
                    echo "Application health check successful!"
                    exit 0
                fi

                echo "Waiting for application..."
                sleep 2
            done

            docker logs ${CONTAINER_NAME}
            exit 1
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
