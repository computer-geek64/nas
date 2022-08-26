// Jenkinsfile

pipeline {
    agent any;

    stages {
        stage('Build') {
            steps {
                sh 'docker-compose build'
            }
        }

        stage('Test') {}

        stage('Deploy') {
            when {
                branch pattern: '^master$|^main$|stable|release',
                comparator: 'REGEXP'
            }

            steps {
                sh 'docker-compose down'
                sh 'docker-compose up -d'
            }
        }
    }

    post {
        regression {
            withCredentials([string(credentialsId: 'ifttt-push-notification-webhook', variable: 'IFTTT_PUSH_NOTIFICATION_WEBHOOK')]) {
                sh 'curl -X POST -H \'Content-Type: application/json\' -d \'{"value1": "Jenkins Build Broke", "value2": "Branch ' + env.BRANCH_NAME + ' of ' + env.JOB_NAME.split('/')[0] + ' has failed"}\' ' + env.IFTTT_PUSH_NOTIFICATION_WEBHOOK
            }
        }

        fixed {
            withCredentials([string(credentialsId: 'ifttt-push-notification-webhook', variable: 'IFTTT_PUSH_NOTIFICATION_WEBHOOK')]) {
                sh 'curl -X POST -H \'Content-Type: application/json\' -d \'{"value1": "Jenkins Build Fixed", "value2": "Branch ' + env.BRANCH_NAME + ' of ' + env.JOB_NAME.split('/')[0] + ' was successful"}\' ' + env.IFTTT_PUSH_NOTIFICATION_WEBHOOK
            }
        }

        cleanup {
            cleanWs()
        }
    }
}