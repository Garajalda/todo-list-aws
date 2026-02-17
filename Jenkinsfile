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
                sh 'pip install flake8 bandit'
                sh 'flake8 src/ --output-file flake8-report.txt || true'
                sh 'bandit -r src/ -f txt -o bandit-report.txt || true'
                archiveArtifacts artifacts: '*.txt'
            }
        }
    }
}
