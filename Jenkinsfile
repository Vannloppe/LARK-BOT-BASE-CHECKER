pipeline {
    agent any  // run on any available Jenkins server

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/YOUR_USERNAME/lark-bot.git'
                // pulls the latest code from GitHub
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt -t ./package'
                // installs libraries INTO a folder called "package"
                // "-t ./package" = target directory (needed for Lambda packaging)
            }
        }

        stage('Package') {
            steps {
                sh 'cp *.py ./package/'          // copy your .py files into package/
                sh 'cd package && zip -r ../lark-bot.zip .'  // zip everything
                // AWS Lambda needs a .zip file to deploy
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
                // uploads the zip to AWS Lambda
                // --region: use whatever region your Lambda is in
            }
        }
    }
}