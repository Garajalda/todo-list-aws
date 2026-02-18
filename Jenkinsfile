pipeline {
    agent any

    stages {

        stage('Deploy Production') {
            steps {
                sh '''
                rm -f samconfig.toml
                sam build
                sam deploy \
                --stack-name todo-list-aws-production \
                --region us-east-1 \
                --capabilities CAPABILITY_IAM \
                --parameter-overrides Stage=production \
                --resolve-s3 \
                --no-fail-on-empty-changeset
                '''
            }
        }

        stage('Read Only Test Production') {
            steps {
                sh '''
                python3 -m pip install --user pytest requests
                export BASE_URL=https://abc123.execute-api.us-east-1.amazonaws.com/production
                python3 -m pytest test/integration/testReadOnly.py -v
                '''
            }
        }
    }
}
