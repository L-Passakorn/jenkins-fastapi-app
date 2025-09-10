pipeline {
    agent any

    environment {
        SONAR_TOKEN = credentials('sonar-token')  // SonarQube token
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/wKritwara/Jenkins_Demopipe01.git'
            }
        }

        stage('Setup Python & Install Dependencies') {
            agent {
                docker {
                    image 'python-docker:3.11'
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
                    image 'python-docker:3.11'
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
                sh '''
                    docker run --rm \
                      -e SONAR_HOST_URL=http://172.17.0.3:9000 \
                      -e SONAR_LOGIN=sqp_eb7b5bb7e277b631cb405148bd3a50bf6c239a6c \
                      -v $(pwd):/usr/src \
                      sonarsource/sonar-scanner-cli  
                '''
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
