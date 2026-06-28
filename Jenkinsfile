pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/YOUR_USERNAME/lark-bot.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    rm -rf package
                    mkdir package
                    pip3 install requests python-dotenv -t ./package
                '''
            }
        }

        stage('Package') {
            steps {
                sh '''
                    cp lambda_function.py ./package/
                    cp lark_client.py ./package/
                    cd package && zip -r ../lark-bot.zip .
                '''
            }
        }

        stage('Deploy to Lambda') {
            steps {
                sh '''
                    aws lambda update-function-code \
                        --function-name lark-bot \
                        --zip-file fileb://lark-bot.zip \
                        --region ap-southeast-1
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Deployed to Lambda successfully!'
        }
        failure {
            echo '❌ Deployment failed — check logs above'
        }
    }
}