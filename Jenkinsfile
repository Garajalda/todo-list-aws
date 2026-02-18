pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
    }

    stages {

        stage('Get Code') {
            steps {
                checkout scm
            }
        }

        stage('Static Test (CI only)') {
            when {
                expression { env.GIT_BRANCH.contains('develop') }
            }

            steps {
                sh '''
                python3 -m pip install --user flake8 bandit
                python3 -m flake8 src/ --output-file=flake8-report.txt || true
                python3 -m bandit -r src/ -f txt -o bandit-report.txt || true
                '''
                archiveArtifacts artifacts: '*.txt'
            }
        }

        stage('Deploy') {
            steps {
                script {

                    sh 'echo GIT_BRANCH=$GIT_BRANCH'

                    if (env.GIT_BRANCH.contains('develop')) {
                        env.STACK_NAME = 'todo-list-aws-staging'
                        env.STAGE_PARAM = 'staging'
                    } else if (env.GIT_BRANCH.contains('main')) {
                        env.STACK_NAME = 'todo-list-aws-production'
                        env.STAGE_PARAM = 'production'
                    }

                    sh """
                    rm -f samconfig.toml
                    sam build
                    sam deploy \
                    --stack-name ${env.STACK_NAME} \
                    --region ${AWS_REGION} \
                    --capabilities CAPABILITY_IAM \
                    --parameter-overrides Stage=${env.STAGE_PARAM} \
                    --resolve-s3 \
                    --no-fail-on-empty-changeset
                    """
                }
            }
        }

        stage('Get API URL') {
            steps {
                script {
                    env.BASE_URL = sh(
                        script: """
                        aws cloudformation describe-stacks \
                          --stack-name ${env.STACK_NAME} \
                          --region ${AWS_REGION} \
                          --query "Stacks[0].Outputs[?OutputKey=='BaseUrlApi'].OutputValue" \
                          --output text
                        """,
                        returnStdout: true
                    ).trim()
                }

                sh 'echo BASE_URL=${BASE_URL}'
            }
        }

        stage('REST Test') {
            steps {
                script {
                    sh 'python3 -m pip install --user pytest requests'

                    if (env.BRANCH_NAME == 'develop') {

                        sh '''
                        export BASE_URL=${BASE_URL}
                        python3 -m pytest test/integration/todoApiTest.py -v
                        '''

                    } else if (env.BRANCH_NAME == 'main') {

                        sh '''
                        export BASE_URL=${BASE_URL}
                        python3 -m pytest test/integration/testReadOnly.py -v
                        '''
                    }
                }
            }
        }

        stage('Promote to Main') {
           when {
                expression { env.GIT_BRANCH.contains('develop') }
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

                    git checkout main
                    git pull origin main
                    git merge -X theirs origin/develop

                    git merge origin/develop

                    git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Garajalda/todo-list-aws.git
                    git push origin main
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
