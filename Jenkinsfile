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
                // Run sonar-scanner inside the official SonarScanner Docker image.
                // This avoids needing the SonarQube Jenkins plugin or a configured Sonar installation.
                withCredentials([string(credentialsId: 'sonarqube_token', variable: 'SCANNER_TOKEN')]) {
                    sh '''
                    echo "=== DEBUG: Checking workspace contents ==="
                    ls -la
                    echo "=== DEBUG: Checking if tests directory exists ==="
                    ls -la tests/ || echo "tests directory not found"
                    echo "=== DEBUG: Checking if coverage.xml exists ==="
                    ls -la coverage.xml || echo "coverage.xml not found"
                    
                    echo "Running SonarScanner in Docker..."
                    docker run --rm -v "${WORKSPACE}":/usr/src -w /usr/src sonarsource/sonar-scanner-cli:latest \
                        -Dsonar.host.url=http://host.docker.internal:9000 \
                        -Dsonar.login=${SCANNER_TOKEN}
                    '''
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
