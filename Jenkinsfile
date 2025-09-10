pipeline {
    agent any

    stages {
        stage('Setup Python & Install Dependencies') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    args '-u root:root'
                }
            }
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                pip install pytest pytest-cov
                '''
            }
        }

        stage('Run Tests & Generate Coverage') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    args '-u root:root'
                }
            }
            steps {
                sh '''
                . venv/bin/activate
                pytest --maxfail=1 --disable-warnings -q --cov=app --cov-report=xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('sonar-scanner') {
                        withCredentials([string(credentialsId: 'sonar-token', variable: 'SCANNER_TOKEN')]) {
                            sh '''
                            echo "SUCCESS: SCANNER_TOKEN is set."
                            export SONAR_TOKEN="${SCANNER_TOKEN}"
                            
                            # Use the SonarQube scanner tool configured in Jenkins
                            sonar-scanner \
                                -Dsonar.host.url="${SONAR_HOST_URL}" \
                                -Dsonar.projectKey=6510110356_jenkins-fastapi \
                                -Dsonar.sources=app \
                                -Dsonar.tests=tests \
                                -Dsonar.python.coverage.reportPaths=coverage.xml
                            '''
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t fastapi-app:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh 'docker run -d -p 8000:8000 fastapi-app:latest'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished'
        }
    }
}
