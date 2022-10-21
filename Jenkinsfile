pipeline {
    agent { label 'docker-builder' }
    
    environment {
        DOCKER_HOST = "tcp://docker.local:2375"
        DOCKER_REGISTRY = "360performance"
        LOG_LEVEL = "INFO"
        BUILD_NUMBER = "${BUILD_NUMBER}"
        TAG = "0.${BUILD_NUMBER}"
        DOCKERHUB_LOGIN = credentials('dockerhub-login')
        GITHUB_TOKEN = credentials('github_auth_token')
        git_branch = "${GIT_BRANCH}"
        BRANCH_NAME = git_branch.substring(git_branch.lastIndexOf('/') + 1, git_branch.length())
    }

    stages {
        stage('Build Docker Images') {
            steps {
                sh 'printenv'
                dir("${env.WORKSPACE}/docker/configmanager"){
                    sh label: 'Build Configmanager', script: 'docker -H ${DOCKER_HOST} build -t ${DOCKER_REGISTRY}/configmanager:${BRANCH_NAME} .'
                }
                dir("${env.WORKSPACE}/docker/configcache"){
                    sh label: 'Build Configcache', script: 'docker -H ${DOCKER_HOST} build -t ${DOCKER_REGISTRY}/configcache:${BRANCH_NAME} .'
                }
                script {
                    if (env.BRANCH_NAME == 'master') {
                        dir("${env.WORKSPACE}/docker/configmanager"){
                            sh label: 'Build Configmanager', script: 'docker -H ${DOCKER_HOST} build -t ${DOCKER_REGISTRY}/configmanager:${TAG} -t ${DOCKER_REGISTRY}/configmanager:latest .'
                        }
                        dir("${env.WORKSPACE}/imageexport") {
                            sh label: 'GitHub CLI login', script: 'echo ${GITHUB_TOKEN} | gh auth login --with-token'
                            sh label: 'GitHub CLI status', script: 'gh auth status'
                            sh label: 'Save images', script: 'docker save -o configmanager-${TAG}.tar'
                        }
                    }
                }
            }
        }
        stage('Push Docker Images') {
            steps {
                sh label: 'Docker Login', script: 'docker login -u ${DOCKERHUB_LOGIN_USR} -p ${DOCKERHUB_LOGIN_PSW}'
                dir("${env.WORKSPACE}/docker/configmanager") {
                    sh label: 'Push Configmanager', script: 'docker push -q ${DOCKER_REGISTRY}/configmanager:${BRANCH_NAME}'
                }
                dir("${env.WORKSPACE}/docker/configcache") {
                    sh label: 'Push Configcache', script: 'docker push -q ${DOCKER_REGISTRY}/configcache:${BRANCH_NAME}'
                }
                script {
                    if (env.BRANCH_NAME == 'master') {
                        dir("${env.WORKSPACE}/docker/configmanager"){
                            sh label: 'Push Configmanager', script: 'docker push -q ${DOCKER_REGISTRY}/configmanager:latest'
                            sh label: 'Push Configmanager', script: 'docker push -q ${DOCKER_REGISTRY}/configmanager:${TAG}'
                        }
                    }
                }
            }   
        }
    }
}