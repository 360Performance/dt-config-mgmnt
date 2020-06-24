pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = "halfdome.local:50000"
        BUILD_NUMBER = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                dir("${env.WORKSPACE}/docker"){
                    sh label: 'Run Docker Compose', script: 'docker-compose build'
                }
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}