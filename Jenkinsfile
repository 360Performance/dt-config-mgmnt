pipeline {
    agent any
    
    environment {
        DOCKER_HOST = ""
        //DOCKER_HOST = "tcp://192.168.1.123:2375"
        DOCKER_REGISTRY = "360performance"
        LOG_LEVEL = "INFO"
        BUILD_NUMBER = "${BUILD_NUMBER}"
        TAG = "0.${BUILD_NUMBER}"
        DOCKERHUB_LOGIN = credentials('dockerhub-login')
    }

    stages {
        stage('Build Docker Images') {
            steps {
                dir("${env.WORKSPACE}/docker/configmanager"){
                    sh label: 'Build Configmanager', script: 'docker build -t ${DOCKER_REGISTRY}/configmanager:${TAG} .'
                }
                dir("${env.WORKSPACE}/docker/configcache"){
                    sh label: 'Build Configcache', script: 'docker build -t ${DOCKER_REGISTRY}/configcache:${TAG} .'
                }
            }
        }
        stage('Push Docker Images') {
            steps {
                sh label: 'Docker Login', script: 'docker login -u ${DOCKERHUB_LOGIN_USR} -p ${DOCKERHUB_LOGIN_PSW}'
                dir("${env.WORKSPACE}/docker/configmanager") {
                    sh label: 'Push Configmanager', script: 'docker push ${DOCKER_REGISTRY}/configmanager:${TAG}'
                }
                dir("${env.WORKSPACE}/docker/configcache") {
                    sh label: 'Push Configcache', script: 'docker push ${DOCKER_REGISTRY}/configcache:${TAG}'
                }
            }   
        }
    }
}