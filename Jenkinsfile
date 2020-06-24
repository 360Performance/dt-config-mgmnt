pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = "halfdome.local:50000"
        LOG_LEVEL = "INFO"
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
                    withEnv(['API_HOST=https://api.dy.natrace.it:8443', 'LOG_LEVEL=INFO']) {
                        withCredentials([usernamePassword(credentialsId: 'apiuser', passwordVariable: 'API_PWD', usernameVariable: 'API_USER')]) {
                            sh label: 'Run Configcache', script: 'docker-compose --no-ansi up -d configcache'
                            sh label: 'Run Configmanger', script: 'docker-compose --no-ansi up configmanager'
                        }
                    }
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