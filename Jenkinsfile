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

                    withCredentials([usernamePassword(
                        credentialsId: 'github-token',
                        usernameVariable: 'GIT_USERNAME',
                        passwordVariable: 'GIT_PASSWORD'
                    )]) {

                        sh """
                        rm -f samconfig.toml
                        rm -rf config-repo

                        if echo "${GIT_BRANCH}" | grep -q develop; then
                            git clone -b staging https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Garajalda/todo-list-aws-config.git config-repo
                        else
                            git clone -b production https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Garajalda/todo-list-aws-config.git config-repo
                        fi

                        cp config-repo/samconfig.toml .
                        """
                    }

                    sh """
                    sam build
                    sam deploy --resolve-s3 --no-fail-on-empty-changeset
                    """
                }
            }
        }

        stage('Get API URL') {
            steps {
                script {

                    if (env.GIT_BRANCH.contains('develop')) {
                        env.STACK_NAME = 'todo-list-aws-staging'
                    } else {
                        env.STACK_NAME = 'todo-list-aws-production'
                    }

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

                    if (env.GIT_BRANCH.contains('develop')) {

                        sh '''
                        export BASE_URL=${BASE_URL}
                        python3 -m pytest test/integration/todoApiTest.py -v
                        '''

                    } else if (env.GIT_BRANCH.contains('main')) {

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

            git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Garajalda/todo-list-aws.git
            git push origin main
            '''
        }

        build job: 'todo-list-aws-cd'
    }
}

    }

    post {
        always {
            cleanWs()
        }
    }
}
