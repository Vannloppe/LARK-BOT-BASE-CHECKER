# 🤖 Lark Bot Base Checker

A scheduled bot that monitors Lark Base tables and sends alerts to a Lark group chat when records have not been updated within 8 hours. Deployed on AWS Lambda and automated via Jenkins CI/CD pipeline on EC2.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [AWS Lambda Setup](#aws-lambda-setup)
- [Jenkins CI/CD Setup](#jenkins-cicd-setup)
- [Running Locally](#running-locally)
- [Deployment](#deployment)

---

## Overview

This bot reads records from two Lark Base tables and checks when each record was last modified. If a record has not been updated in the last 8 hours and its status is not `Case Closed` or `Done`, the bot sends an alert to a designated Lark group chat.

The bot runs automatically twice a day — 9AM and 9PM Manila time (UTC+8) — triggered by AWS EventBridge.

---

## Features

- Reads records from multiple Lark Base tables
- Filters out closed and completed records automatically
- Alerts the team when records have not been updated in 8 hours
- Skips empty records gracefully
- Paginated fetching — handles tables with 1000+ records
- Deployed on AWS Lambda with EventBridge scheduling
- Automated deployments via Jenkins CI/CD pipeline

---

## Architecture

```
GitHub (source code)
    ↓  push triggers Jenkins
EC2 (Jenkins server)
    ↓  builds and deploys
AWS Lambda (lark-bot function)
    ↓  triggered by EventBridge (9AM and 9PM Manila)
Lark Base (reads records)
    ↓  sends alerts
Lark Group Chat
```

---

## Project Structure

```
lark-bot/
├── lambda_function.py    # Main bot logic — Lambda entry point
├── lark_client.py        # Lark API helper functions
├── test_local.py         # Local testing script
├── Jenkinsfile           # Jenkins CI/CD pipeline definition
├── requirements.txt      # Python dependencies
├── .env                  # Local environment variables (never commit this)
└── .gitignore            # Excludes .env, venv, __pycache__
```

---

## Prerequisites

- Python 3.11+
- AWS Account with Lambda and EC2 access
- Lark Developer Account with a Custom App created
- GitHub account
- Jenkins installed on EC2 (see Jenkins Setup below)

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vannloppe/LARK-BOT-BASE-CHECKER.git
cd LARK-BOT-BASE-CHECKER
```

### 2. Create a virtual environment

```bash
python3 -m venv env
source env/bin/activate        # Mac/Linux
env\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

```bash
cp .env.example .env
```

Fill in your actual values (see Environment Variables below).

---

## Environment Variables

Create a `.env` file in the root of the project with these values:

```env
# Lark App Credentials
LARK_APP_ID=your_app_id
LARK_APP_SECRET=your_app_secret

# Lark Base Configuration
LARK_BASE_APP_TOKEN=your_base_app_token

# Table 1 — Task Table
LARK_BASE_TABLE_ID_1=your_table_id_1
LARK_BASE_TABLE_NAME_1=Task

# Table 2 — P0 Task Table
LARK_BASE_TABLE_ID_2=your_table_id_2
LARK_BASE_TABLE_NAME_2=P0 Task

# Lark Chat
LARK_CHAT_ID=your_chat_id
```

### How to get these values

| Variable | Where to find it |
|---|---|
| `LARK_APP_ID` | Lark Developer Console → Your App → App ID |
| `LARK_APP_SECRET` | Lark Developer Console → Your App → App Secret |
| `LARK_BASE_APP_TOKEN` | Lark Base URL → `larksuite.com/base/TOKEN?table=...` |
| `LARK_BASE_TABLE_ID` | Lark Base URL → `...?table=TABLE_ID` |
| `LARK_CHAT_ID` | Call Lark IM API → `/im/v1/chats` → find your group |

---

## AWS Lambda Setup

### 1. Create the Lambda function

```
AWS Console → Lambda → Create Function
Name:     lark-bot
Runtime:  Python 3.11
```

### 2. Add Environment Variables

```
Lambda → Configuration → Environment Variables
```

Add all variables from the `.env` file section above.

### 3. Increase timeout and memory

```
Lambda → Configuration → General Configuration
Timeout: 5 minutes
Memory:  256 MB
```

### 4. Set up EventBridge schedule

```
Lambda → Add Trigger → EventBridge
Schedule: cron(0 1 * * ? *)    # 9AM Manila (1AM UTC)
Schedule: cron(0 13 * * ? *)   # 9PM Manila (1PM UTC)
```

### 5. Attach IAM Role

Attach a role with `AWSLambdaFullAccess` to allow Jenkins to deploy.

---

## Jenkins CI/CD Setup

### Prerequisites on EC2

```bash
# Java 21 (required by latest Jenkins)
sudo dnf install java-21-amazon-corretto -y

# Jenkins
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo dnf install jenkins -y
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Git
sudo dnf install git -y

# Python and pip
sudo dnf install python3 python3-pip -y

# AWS CLI
sudo dnf install awscli -y
```

### Jenkins Plugins Required

- Git
- Pipeline
- GitHub Integration
- AWS Steps

### Pipeline Configuration

```
New Item → Pipeline
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/Vannloppe/LARK-BOT-BASE-CHECKER.git
Branch: */main
Script Path: Jenkinsfile
```

### IAM Role for EC2

Attach an IAM Role with `AWSLambdaFullAccess` to your EC2 instance so Jenkins can deploy without storing credentials.

```
IAM → Roles → Create Role
Trusted entity: EC2
Permissions: AWSLambdaFullAccess
Name: ec2-jenkins-role

EC2 → Instances → Your Instance
Actions → Security → Modify IAM Role → ec2-jenkins-role
```

---

## Running Locally

Run the full test suite to verify everything works before deploying:

```bash
python test_local.py
```

The test checks:
1. `.env` values are loading correctly
2. Lark access token is generated
3. Records are being read from both tables
4. Modified time is being detected correctly
5. Full bot simulation — sends real alerts to Lark chat

---

## Deployment

### Manual deployment

```bash
# package the code
mkdir package
pip install requests python-dotenv -t ./package
cp lambda_function.py ./package/
cp lark_client.py ./package/
cd package && zip -r ../lark-bot.zip . && cd ..

# deploy to Lambda
aws lambda update-function-code \
    --function-name lark-bot \
    --zip-file fileb://lark-bot.zip \
    --region ap-southeast-1
```

### Automatic deployment via Jenkins

Push your code to the `main` branch:

```bash
git add .
git commit -m "your change description"
git push origin main
```

Jenkins will automatically:
1. Pull the latest code from GitHub
2. Install Python dependencies
3. Package everything into a zip
4. Deploy the zip to AWS Lambda

---

## Required Lark App Permissions

Make sure your Lark App has these permissions enabled in the Developer Console:

| Permission | Purpose |
|---|---|
| `bitable:app:readonly` | Read Lark Base records |
| `im:message` | Send messages |
| `im:message:send_as_bot` | Send as bot user |
| `im:chat:readonly` | Get list of chats |

---

## Notes

- The bot filters out records with status `Case Closed` or `Done`
- Records with empty `Email Title / Task and Meegle ticket` AND empty `Remarks` are skipped
- The 8-hour threshold matches the twice-daily schedule
- All logs are available in AWS CloudWatch under the `lark-bot` function
