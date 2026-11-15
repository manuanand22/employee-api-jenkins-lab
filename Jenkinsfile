
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

        stage('Test Jenkins Credentials') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-demo-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        if [ -n "$DOCKER_USER" ] && [ -n "$DOCKER_PASS" ]; then
                            echo "Jenkins credentials retrieved successfully!"
                        else
                            exit 1
                        fi
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            -u "$DOCKERHUB_USER" \
                            --password-stdin

                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} \
                            "$DOCKERHUB_USER/employee-api:${BUILD_NUMBER}"

                        docker push "$DOCKERHUB_USER/employee-api:${BUILD_NUMBER}"

                        docker logout
                    '''
                }
            }
        }

      stage('Deploy and Verify') {
    steps {
        script {
            echo "Checking existing deployment..."

            def previousImage = sh(
                script: 'docker inspect "$CONTAINER_NAME" --format "{{.Config.Image}}"',
                returnStdout: true
            ).trim()

            echo "Previous image captured: ${previousImage}"

            def deployStatus = sh(
                script: """
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    echo "Waiting for application health check..."

                    for i in \$(seq 1 15); do
                        if docker exec ${CONTAINER_NAME} python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)" 2>/dev/null; then
                            echo "Deployment successful!"
                            exit 0
                        fi

                        echo "Health check attempt \$i failed"
                        sleep 2
                    done

                    echo "Deployment health check failed"
                    exit 1
                """,
                returnStatus: true
            )

            if (deployStatus != 0) {
                echo "Deployment failed. Starting rollback..."

                sh """
                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        ${previousImage}
                """

                def rollbackStatus = sh(
                    script: """
                        for i in \$(seq 1 15); do
                            if docker exec ${CONTAINER_NAME} python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)" 2>/dev/null; then
                                echo "Rollback successful! Previous version is healthy."
                                exit 0
                            fi

                            echo "Rollback health check attempt \$i failed"
                            sleep 2
                        done

                        echo "Rollback health check failed!"
                        exit 1
                    """,
                    returnStatus: true
                )

                if (rollbackStatus != 0) {
                    error("Deployment failed and rollback was unsuccessful!")
                }

                error("Deployment failed, but rollback completed successfully. Previous version restored: ${previousImage}")
            }

            echo "Deployment completed successfully!"
        }
    }
}

        stage('Publish Latest Tag') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            -u "$DOCKERHUB_USER" \
                            --password-stdin

                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} \
                            "$DOCKERHUB_USER/employee-api:latest"

                        docker push "$DOCKERHUB_USER/employee-api:latest"

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check deployment and rollback logs.'
        }
    }
}
