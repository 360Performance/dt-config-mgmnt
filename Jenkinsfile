pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = "halfdome.local:50000/rweber"
        LOG_LEVEL = "INFO"
        BUILD_NUMBER = "${BUILD_NUMBER}"
        TAG = "1.${BUILD_NUMBER}"
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
                            sh label: 'Run Configcache', script: 'docker-compose --no-ansi up --remove-orphans -d configcache'
                            sh label: 'Run Configmanger', script: 'docker-compose --no-ansi up --remove-orphans -d configmanager'
                        }
                    }
                    sh label: 'Copy test config files', script: 'docker cp config configmanager:/'
                    sh label: 'Set permissions on config folder', script: 'docker exec configmanager chown root:root -R /config'
                    sh label: 'Set up configcache', script: 'docker exec -i configcache redis-cli -x set config < test/config.json'
                    sh label: 'Set up configcache', script: 'docker exec -i configcache redis-cli -x set parameters < test/parameters.json'
                    sh label: 'Set up configcache', script: 'docker exec -i configcache redis-cli -x set source < test/source.json'
                    sh label: 'Set up configcache', script: 'docker exec -i configcache redis-cli -x set target < test/target.json'
                    sh label: 'Resetting Config', script: 'docker exec -i configcache redis-cli publish configcontrol RESET'
                    sh label: 'Pull Config', script: 'docker exec -i configcache redis-cli publish configcontrol PULL_CONFIG'
                    sh label: 'Verify Config', script: 'docker exec -i configcache redis-cli publish configcontrol VERIFY_CONFIG'
                    sh label: 'Resetting Config', script: 'docker exec -i configcache redis-cli publish configcontrol RESET'
                    sh label: 'Reset Confirmed', script: 'docker logs -f configmanager | grep -q "RELOADING STANDARD CONFIG"'
                    sh label: 'Execution Logs', script: 'docker logs configmanager'
                }
            }
        }
        stage('Teardown') {
            steps {
                dir("${env.WORKSPACE}/"){
                    sh label: 'Stop Containers', script: 'docker stop configmanager'
                    sh label: 'Stop Containers', script: 'docker stop configcache'
                }
            }
        }
        stage('Push Images') {
            steps {
                dir("${env.WORKSPACE}/docker") {
                    sh label: 'Push Docker Images', script: 'docker-compose --no-ansi push'
                    withEnv(['TAG=latest']) {
                        sh label: 'Tag with latest', script: 'docker-compose --no-ansi build'
                        sh label: 'Push Docker Images', script: 'docker-compose --no-ansi push'
                    }
                }
            }   
        }
    }
}