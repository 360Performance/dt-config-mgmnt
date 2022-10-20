pipeline {
    agent { label 'docker-builder' }
    
    environment {
        DOCKER_HOST = "tcp://192.168.1.123:2375"
        DOCKER_REGISTRY = "360performance"
        LOG_LEVEL = "INFO"
        BUILD_NUMBER = "${BUILD_NUMBER}"
        TAG = "0.${BUILD_NUMBER}"
        DOCKERHUB_LOGIN = credentials('dockerhub-login')
    }

    stages {
        stage('Build Docker Images') {
            steps {
                sh 'printenv'
                dir("${env.WORKSPACE}/docker/configmanager"){
                    sh label: 'Build Configmanager', script: 'docker -H ${DOCKER_HOST} build -t ${DOCKER_REGISTRY}/configmanager:${env.BRANCH_NAME} .'
                }
                dir("${env.WORKSPACE}/docker/configcache"){
                    sh label: 'Build Configcache', script: 'docker -H ${DOCKER_HOST} build -t ${DOCKER_REGISTRY}/configcache:${env.BRANCH_NAME} .'
                }
            }
        }
        stage('Push Docker Images') {
            steps {
                sh label: 'Docker Login', script: 'docker login -u ${DOCKERHUB_LOGIN_USR} -p ${DOCKERHUB_LOGIN_PSW}'
                dir("${env.WORKSPACE}/docker/configmanager") {
                    sh label: 'Push Configmanager', script: 'docker push -q ${DOCKER_REGISTRY}/configmanager:${env.BRANCH_NAME}'
                }
                dir("${env.WORKSPACE}/docker/configcache") {
                    sh label: 'Push Configcache', script: 'docker push -q ${DOCKER_REGISTRY}/configcache:${env.BRANCH_NAME}'
                }
            }   
        }
    }
}