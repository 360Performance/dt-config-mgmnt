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
                    sh label: 'Run Docker Compose', script: 'docker-compose --no-ansi build'
                }
            }
        }
        stage('Test') {
            steps {
                dir("${env.WORKSPACE}/docker"){
                    sh label: 'Run Configcache', script: 'docker-compose --no-ansi up -d configcache'
                    sh label: 'Run Configmanger', script: 'docker-compose --no-ansi up configmanager'
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}