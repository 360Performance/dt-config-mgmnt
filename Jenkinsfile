pipeline {
    agent any
    
    environment {
        DOCKER_HOST = "tcp://192.168.1.123:2375"
        DOCKER_REGISTRY = "360performance"
        LOG_LEVEL = "INFO"
        BUILD_NUMBER = "${BUILD_NUMBER}"
        TAG = "0.${BUILD_NUMBER}"
    }

    stages {
        stage('Build Docker Images') {
            steps {
                dir("${env.WORKSPACE}/docker/configmanager"){
                    sh label: 'Build Configmanager', script: 'docker -H ${DOCKER_HOST} build - -t configmanager:${TAG}'
                }
            }
        }
        stage('Push Docker Images') {
            steps {
                dir("${env.WORKSPACE}/docker/configmanager") {
                    sh label: 'Push Configmanager', script: 'docker -H ${DOCKER_HOST} push -t configmanager:${TAG}'
                }
            }   
        }
    }
}