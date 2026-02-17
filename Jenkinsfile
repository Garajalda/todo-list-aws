pipeline {
    agent any
    stages {
        stage('Get Code') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/Garajalda/todo-list-aws.git'
            }
        }
    }
}
