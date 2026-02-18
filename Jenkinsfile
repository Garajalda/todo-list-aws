pipeline {
    agent any

    stages {

        stage('Get Code') {
            steps {
                git branch: env.BRANCH_NAME,
                    credentialsId: 'github-token',
                    url: 'https://github.com/Garajalda/todo-list-aws.git'
            }
        }

        stage('Static Test') {
            when {
                branch 'develop'
            }
            steps {
                sh 'python3 -m pip install --user flake8 bandit'
                sh 'python3 -m flake8 src/ --output-file=flake8-report.txt || true'
                sh 'python3 -m bandit -r src/ -f txt -o bandit-report.txt || true'
            }
        }

        stage('Deploy') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'develop') {
                        sh '''
                        sam build
                        sam deploy \
                        --stack-name todo-list-aws-staging \
                        --region us-east-1 \
                        --capabilities CAPABILITY_IAM \
                        --parameter-overrides Stage=staging \
                        --resolve-s3
                        '''
                    } else if (env.BRANCH_NAME == 'master') {
                        sh '''
                        sam build
                        sam deploy \
                        --stack-name todo-list-aws-production \
                        --region us-east-1 \
                        --capabilities CAPABILITY_IAM \
                        --parameter-overrides Stage=production \
                        --resolve-s3
                        '''
                    }
                }
            }
        }

        stage('REST Test') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'develop') {
                        sh '''
                        python3 -m pip install --user pytest requests
                        export BASE_URL=https://TU_API_STAGING
                        python3 -m pytest test/integration/todoApiTest.py -v
                        '''
                    } else if (env.BRANCH_NAME == 'master') {
                        sh '''
                        python3 -m pip install --user pytest requests
                        export BASE_URL=https://TU_API_PROD
                        python3 -m pytest test/integration/testReadOnly.py -v
                        '''
                    }
                }
            }
        }

        stage('Promote') {
            when {
                branch 'develop'
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USERNAME',
                    passwordVariable: 'GIT_PASSWORD'
                )]) {
                    sh '''
                    git config user.email "jenkins@local"
                    git config user.name "Jenkins"

                    git checkout master
                    git merge develop

                    git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Garajalda/todo-list-aws.git
                    git push origin master
                    '''
                }
            }
        }
    }
}
