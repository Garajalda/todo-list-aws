pipeline {
    agent any
    stages {
        stage('Get Code') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/Garajalda/todo-list-aws.git'
            }
        }
        stage('Static Test') {
            steps {
                sh 'python3 -m pip install --user flake8 bandit'
                sh 'python3 -m flake8 src/ --output-file=flake8-report.txt || true'
                sh 'python3 -m bandit -r src/ -f txt -o bandit-report.txt || true'
                archiveArtifacts artifacts: '*.txt'
            }
        }
        stage('Deploy') {
            steps {
                sh 'sam build'
                sh '''
                sam deploy \
                --stack-name todo-list-aws-staging \
                --region us-east-1 \
                --capabilities CAPABILITY_IAM \
                --parameter-overrides Stage=staging \
                --resolve-s3
                '''
            }
        }
    }
}
