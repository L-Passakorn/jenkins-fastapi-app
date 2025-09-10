pipeline {
    agent any // This uses the main Jenkins agent for all general tasks
    
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
                            echo "=== Trying Docker approach ==="
                            docker run --rm -v "$(pwd)":/usr/src -w /usr/src sonarsource/sonar-scanner-cli:latest \
                                -Dsonar.projectKey=6510110356_jenkins-fastapi \
                                -Dsonar.sources=app,tests \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.host.url=http://host.docker.internal:9000 \
                                -Dsonar.login=${SCANNER_TOKEN}
                            '''
                        } catch (Exception e) {
                            echo "Docker approach failed: ${e.getMessage()}"
                            echo "Trying direct SonarQube scanner approach..."
                            
                            // Fallback to using sonar-project.properties file only
                            sh '''
                            echo "=== Using sonar-project.properties configuration ==="
                            cat sonar-project.properties
                            
                            # Create a temporary properties file with working configuration
                            cat > sonar-temp.properties << EOF
sonar.projectKey=6510110356_jenkins-fastapi
sonar.projectName=6510110356_jenkins-fastapi
sonar.projectVersion=1.0
sonar.sources=app
sonar.language=py
sonar.sourceEncoding=UTF-8
sonar.python.coverage.reportPaths=coverage.xml
sonar.host.url=http://localhost:9000
sonar.login=${SCANNER_TOKEN}
EOF
                            
                            # Use wget to download and run SonarQube scanner
                            if ! command -v sonar-scanner &> /dev/null; then
                                echo "Downloading SonarQube scanner..."
                                wget -O sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
                                unzip -q sonar-scanner.zip
                                export PATH=$PATH:$(pwd)/sonar-scanner-4.8.0.2856-linux/bin
                            fi
                            
                            sonar-scanner -Dproject.settings=sonar-temp.properties
                            '''
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            agent {
                docker {
                    image 'docker:19.03.13'
                    args "-w /workspace -v \${pwd()}:/workspace -v /var/run/docker.sock:/var/run/docker.sock"
                }
            }
            steps {
                sh 'docker build -t fastapi-app:latest .'
            }
        }

        stage('Deploy Container') {
            agent {
                docker {
                    image 'docker:19.03.13'
                    args "-w /workspace -v \${pwd()}:/workspace -v /var/run/docker.sock:/var/run/docker.sock"
                }
            }
            steps {
                sh '''
                docker stop fastapi_app || true
                docker rm fastapi_app || true
                docker run -d -p 8000:8000 --name fastapi_app fastapi-app:latest
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
