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
                        withCredentials([string(credentialsId: 'sonarqube_token', variable: 'SCANNER_TOKEN')]) {
                            sh """
                            echo "SUCCESS: SCANNER_TOKEN is set."

                            # Use SonarQube scanner Docker image
                            docker run --rm \\
                                -e SONAR_HOST_URL=\"${SONAR_HOST_URL}\" \\
                                -e SONAR_LOGIN=\"${SCANNER_TOKEN}\" \\
                                -v \"\$(pwd):/usr/src\" \\
                                sonarsource/sonar-scanner-cli \\
                                -Dsonar.projectKey=6510110356_jenkins-fastapi \\
                                -Dsonar.sources=app \\
                                -Dsonar.tests=tests \\
                                -Dsonar.python.coverage.reportPaths=coverage.xml
                            """
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
