
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
			echo "Checking existing deployment from Jenkins..."

			sh """
			    echo "Container name: $CONTAINER_NAME"
			    echo "Docker containers matching the name:"
			    docker ps -a --filter "name=$CONTAINER_NAME"

			    echo "Inspecting previous deployment:"
			    docker inspect "$CONTAINER_NAME" --format='{{.Config.Image}}'
			"""
                    // Identify the currently running image
                    
                    //def previousImage = sh(
    			//script: 'docker inspect "$CONTAINER_NAME" --format="{{.Config.Image}}" 2>/dev/null || true',
    				//returnStdout: true
			//).trim()

			//echo "Previous image captured: ${previousImage ?: 'None'}"
			
			
			def previousImage = sh(
			    script: 'docker inspect "$CONTAINER_NAME" --format "{{.Config.Image}}"',
			    returnStdout: true
			).trim()

			echo "DEBUG: Captured previous image = [${previousImage}]"

			if (!previousImage) {
			    error("Could not capture the previous Docker image")
			}

                    // Deploy new image and perform health check

                    def deployStatus = sh(
                        script: '''
                            set -e

                            docker rm -f "$CONTAINER_NAME" \
                                >/dev/null 2>&1 || true

                            docker run -d \
                                --name "$CONTAINER_NAME" \
                                -p "$APP_PORT:5000" \
                                "$IMAGE_NAME:$BUILD_NUMBER" sh -c 'sleep 300'

                            for i in $(seq 1 15); do

                                if docker exec "$CONTAINER_NAME" python -c \
                                "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3).read().decode())"
                                then
                                    echo "New deployment is healthy!"
                                    exit 0
                                fi

                                echo "Waiting for application..."
                                sleep 2
                            done

                            docker logs "$CONTAINER_NAME" || true

                            exit 1
                        ''',
                        returnStatus: true
                    )

                    // Rollback if deployment or health check fails

                    if (deployStatus != 0) {

                        echo "NEW DEPLOYMENT FAILED!"

                        if (previousImage) {

                            echo "Starting automatic rollback to ${previousImage}"

                            def rollbackStatus

				withEnv(["PREVIOUS_IMAGE=${previousImage}"]) {
				    rollbackStatus = sh(
					script: '''
					    set -e

					    docker rm -f "$CONTAINER_NAME" \
						>/dev/null 2>&1 || true

					    docker run -d \
						--name "$CONTAINER_NAME" \
						-p "$APP_PORT:5000" \
						"$PREVIOUS_IMAGE"

					    for i in $(seq 1 15); do

						if docker exec "$CONTAINER_NAME" python -c \
						"import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3).read().decode())"
						then
						    echo "Rollback successful!"
						    exit 0
						fi

						echo "Waiting for previous version..."
						sleep 2
					    done

					    docker logs "$CONTAINER_NAME" || true
					    exit 1
					''',
					returnStatus: true
				    )
				}

                            if (rollbackStatus != 0) {
                                error("CRITICAL: Deployment and rollback both failed!")
                            }

                            echo "Previous working version restored successfully!"

                        } else {

                            echo "No previous deployment available for rollback."

                            sh '''
                                docker rm -f "$CONTAINER_NAME" \
                                    >/dev/null 2>&1 || true
                            '''
                        }

                        error("New deployment failed. Rollback attempted.")
                    }
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
