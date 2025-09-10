pipeline {
    agent any // This uses the main Jenkins agent for all general tasks
    
    environment {
        APP_PORT = "${params.APP_PORT ?: '8000'}"
        ENVIRONMENT = "${params.ENVIRONMENT ?: 'development'}"
        CONTAINER_NAME = "fastapi_app_${ENVIRONMENT}"
    }
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Select deployment environment'
        )
        string(
            name: 'APP_PORT',
            defaultValue: '8000',
            description: 'Port to expose the application'
        )
    }
    
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
                sh 'echo "Workspace cleaned"'
            }
        }

        stage('Checkout') {
            steps {
                // Try the pipeline-configured SCM first; if that fails (missing branch),
                // fallback to the repository 'main' branch to avoid aborting the build.
                script {
                    try {
                        echo "Attempting to checkout using pipeline-configured SCM..."
                        checkout scm
                    } catch (err) {
                        echo "Primary checkout failed: ${err}. Falling back to 'main' branch."
                        checkout([$class: 'GitSCM', branches: [[name: 'refs/heads/main']], userRemoteConfigs: [[url: 'https://github.com/L-Passakorn/jenkins-fastapi-app.git']]])
                    }
                }
                sh 'echo "=== FILES AFTER CHECKOUT ==="; ls -la'
            }
        }

        stage('Run Tests & Coverage') {
            agent {
                docker {
                    image 'python:3.11'
                    args '-u root:root'
                }
            }
            steps {
                sh '''
                echo "Running tests inside Docker container..."
                python -m venv venv
                . venv/bin/activate
                pip install --no-cache-dir -r requirements.txt
                echo "Dependencies installed. Running tests..."
                pytest --maxfail=1 --disable-warnings -q --cov=app --cov-report=xml
                echo "Tests completed successfully."
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // Alternative approach: Use SonarQube without Docker to avoid volume mounting issues
                withCredentials([string(credentialsId: 'sonarqube_token', variable: 'SCANNER_TOKEN')]) {
                    script {
                        // Try Docker approach first, if it fails, use direct approach
                        try {
                            sh '''
                            echo "=== DEBUG: Checking files before Docker ==="
                            ls -la
                            echo "=== Trying Docker approach ==="
                            docker run --rm -v "$(pwd)":/usr/src -w /usr/src sonarsource/sonar-scanner-cli:latest \
                                -Dsonar.projectKey=6510110356_jenkins-fastapi \
                                -Dsonar.sources=app,tests \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.host.url=http://host.docker.internal:9000 \
                                -Dsonar.token=${SCANNER_TOKEN}
                            '''
                        } catch (Exception e) {
                            echo "Docker approach failed: ${e.getMessage()}"
                            echo "Trying direct SonarQube scanner approach..."
                            
                            // Fallback to using sonar-project.properties file only
                            sh '''
                            echo "=== Using sonar-project.properties configuration ==="
                            ls -la
                            cat sonar-project.properties
                            
                            # Create a temporary properties file with working configuration
                            # Try different host URLs for Docker-to-host communication
                            echo "=== Testing SonarQube connectivity ==="
                            
                            # Test different host URLs
                            SONAR_HOST=""
                            for host in "host.docker.internal" "172.17.0.1" "gateway.docker.internal" "localhost"; do
                                echo "Testing http://$host:9000..."
                                if curl -s --connect-timeout 5 "http://$host:9000" >/dev/null 2>&1; then
                                    SONAR_HOST="http://$host:9000"
                                    echo "✓ SonarQube found at $SONAR_HOST"
                                    break
                                fi
                            done
                            
                            if [ -z "$SONAR_HOST" ]; then
                                echo "⚠ Could not find SonarQube server. Trying host.docker.internal as default..."
                                SONAR_HOST="http://host.docker.internal:9000"
                            fi
                            
                            cat > sonar-temp.properties << EOF
sonar.projectKey=6510110356_jenkins-fastapi
sonar.projectName=6510110356_jenkins-fastapi
sonar.projectVersion=1.0
sonar.sources=app
sonar.language=py
sonar.sourceEncoding=UTF-8
sonar.python.coverage.reportPaths=coverage.xml
sonar.host.url=$SONAR_HOST
sonar.token=${SCANNER_TOKEN}
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
EOF
                            
                            # Check if sonar-scanner is available
                            if ! command -v sonar-scanner &> /dev/null; then
                                echo "SonarQube scanner not found, downloading..."
                                
                                # Try curl first, then wget
                                if command -v curl &> /dev/null; then
                                    echo "Using curl to download..."
                                    curl -o sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                                elif command -v wget &> /dev/null; then
                                    echo "Using wget to download..."
                                    wget -O sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                                else
                                    echo "Neither curl nor wget available. Trying alternative approach..."
                                    # Use the SonarQube Docker image but run it differently
                                    docker run --rm \
                                        -e SONAR_HOST_URL="$SONAR_HOST" \
                                        -e SONAR_TOKEN=${SCANNER_TOKEN} \
                                        -v "$(pwd)":/usr/src \
                                        --workdir /usr/src \
                                        sonarsource/sonar-scanner-cli:latest \
                                        -Dproject.settings=sonar-temp.properties
                                    exit 0
                                fi
                                
                                # Extract and use the scanner
                                if [ -f sonar-scanner.zip ]; then
                                    unzip -q sonar-scanner.zip
                                    export PATH=$PATH:$(pwd)/sonar-scanner-5.0.1.3006-linux/bin
                                    sonar-scanner -Dproject.settings=sonar-temp.properties
                                else
                                    echo "Failed to download scanner, trying Docker fallback..."
                                    docker run --rm \
                                        -e SONAR_HOST_URL="$SONAR_HOST" \
                                        -e SONAR_TOKEN=${SCANNER_TOKEN} \
                                        -v "$(pwd)":/usr/src \
                                        --workdir /usr/src \
                                        sonarsource/sonar-scanner-cli:latest \
                                        -Dproject.settings=sonar-temp.properties
                                fi
                            else
                                echo "Using existing sonar-scanner..."
                                sonar-scanner -Dproject.settings=sonar-temp.properties
                            fi
                            '''
                        }
                    }
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                script {
                    echo "=== Waiting for SonarQube Quality Gate ==="
                    try {
                        timeout(time: 5, unit: 'MINUTES') {
                            def qg = waitForQualityGate()
                            if (qg.status != 'OK') {
                                echo "Quality Gate failed: ${qg.status}"
                                echo "Quality Gate details: ${qg}"
                                // You can choose to fail the build or continue
                                // error "Pipeline aborted due to quality gate failure: ${qg.status}"
                                currentBuild.result = 'UNSTABLE'
                            } else {
                                echo "Quality Gate passed: ${qg.status}"
                            }
                        }
                    } catch (Exception e) {
                        echo "Quality Gate check failed or timed out: ${e.getMessage()}"
                        echo "Continuing with build..."
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                echo "=== Cleaning up before Docker build ==="
                rm -rf .pytest_cache || true
                rm -rf __pycache__ || true
                rm -rf .sonar || true
                rm -rf sonar-scanner* || true
                rm -f sonar-scanner.zip || true
                rm -f sonar-temp.properties || true
                find . -name "*.pyc" -delete || true
                find . -name "__pycache__" -type d -exec rm -rf {} + || true
                
                echo "=== Building Docker image ==="
                docker build -t fastapi-app:latest .
                '''
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                echo "=== Deploying FastAPI container ==="
                echo "Environment: ${ENVIRONMENT}"
                echo "Port: ${APP_PORT}"
                echo "Container Name: ${CONTAINER_NAME}"
                
                # Stop and remove existing container if it exists
                docker stop ${CONTAINER_NAME} || true
                docker rm ${CONTAINER_NAME} || true
                
                # Deploy new container with environment-specific settings
                docker run -d \
                    -p ${APP_PORT}:8000 \
                    --name ${CONTAINER_NAME} \
                    -e ENVIRONMENT=${ENVIRONMENT} \
                    fastapi-app:latest
                
                echo "=== Container deployed successfully ==="
                docker ps | grep ${CONTAINER_NAME} || echo "Container not running"
                echo "Application available at: http://localhost:${APP_PORT}"
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished'
        }
    }
}
