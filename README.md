# SevenBot - Telegram Email Summarization System

## 📚 Documentation Quick Links

- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 2 hours
- 📖 **[Setup Index](SETUP_INDEX.md)** - Complete navigation for all guides
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system design
- 📝 **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all documentation

### Component Setup Guides
- **AWS Infrastructure:** [DynamoDB](aws/dynamodb/SETUP_GUIDE.md) | [S3](aws/s3/SETUP_GUIDE.md) | [API Gateway](aws/api-gateway/SETUP_GUIDE.md) | [EventBridge](aws/eventbridge/SETUP_GUIDE.md)
- **Lambda Functions:** [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md) | [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md) | [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md)
- **Email Services:** [Gmail Setup](gmail-setup/SETUP_GUIDE.md) | [Cloudflare Email Routing](cloudflare-setup/SETUP_GUIDE.md)

---

## 🎯 Project Overview

SevenBot is an intelligent email summarization system that generates unique email addresses for Telegram users, processes incoming emails, and delivers AI-powered summaries directly to Telegram. Built entirely on serverless architecture using AWS Lambda, DynamoDB, S3, Cloudflare Email Routing, and OpenAI GPT.

**Domain**: csearfarf.dev  
**Platform**: AWS + Cloudflare + Telegram  
**AI Engine**: OpenAI GPT-3.5-turbo

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│ Telegram User│────▶│ Telegram Bot   │────▶│  DynamoDB   │
│              │     │ (API Gateway + │     │   (Users)   │
│              │     │   Lambda)      │     │             │
└──────────────┘     └────────────────┘     └─────────────┘
                              │
                              │
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│   Email      │────▶│  Cloudflare    │────▶│    Gmail    │
│   Sender     │     │  Email Router  │     │    IMAP     │
└──────────────┘     └────────────────┘     └─────────────┘
                                                     │
                                                     ▼
                              ┌────────────────────────────┐
                              │  Email Fetcher Lambda      │
                              │  (Polls every 5 minutes)   │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │         S3 Bucket          │
                              │    (Email Storage)         │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │  Email Processor Lambda    │
                              │  (OpenAI Summarization)    │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │    Telegram Notification   │
                              │    (Summary Delivered)     │
                              └────────────────────────────┘
```

## ✨ Key Features

- **Unique Email Generation**: Each user gets personalized email addresses (e.g., `user_123456789_abc123@csearfarf.dev`)
- **AI-Powered Summaries**: OpenAI GPT creates concise 2-3 sentence email summaries
- **Real-Time Notifications**: Instant Telegram notifications when emails arrive
- **Serverless Architecture**: Zero server management, scales automatically
- **Secure & Private**: Email content encrypted, user data protected
- **Cost-Effective**: Pay only for what you use

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS Account (AWS Academy Lab or personal account)
- [ ] Cloudflare Account with domain (csearfarf.dev)
- [ ] Telegram Account
- [ ] Gmail Account with App Password
- [ ] OpenAI API Account
- [ ] AWS CLI installed and configured
- [ ] Basic knowledge of Python, AWS Lambda, and REST APIs

## 🚀 Quick Start

### 1. Clone or Download This Repository
```bash
cd "d:\Opensource Dev\238\sevenbot"
```

### 2. Follow the Setup Guides in Order

1. **[Architecture Guide](ARCHITECTURE.md)** - Understand the system design
2. **[AWS DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md)** - Create database tables
3. **[AWS S3 Setup](aws/s3/SETUP_GUIDE.md)** - Configure email storage
4. **[AWS Lambda Functions](aws/lambda-functions/)** - Deploy all three functions
   - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
   - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md)
   - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md)
5. **[AWS API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md)** - Create webhook endpoint
6. **[Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md)** - Configure email routing

### 3. Test the System
```bash
# Send a test email
echo "Test email body" | mail -s "Test Subject" user_123456789_abc123@csearfarf.dev

# Check if summary arrives in Telegram
```

## 📁 Project Structure

```
sevenbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture guide
│
├── aws/
│   ├── dynamodb/
│   │   └── SETUP_GUIDE.md            # DynamoDB tables setup
│   │
│   ├── s3/
│   │   └── SETUP_GUIDE.md            # S3 bucket configuration
│   │
│   ├── lambda-functions/
│   │   ├── email-fetcher/
│   │   │   ├── SETUP_GUIDE.md        # Email fetcher setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   ├── email-processor/
│   │   │   ├── SETUP_GUIDE.md        # Email processor setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   └── telegram-webhook/
│   │       ├── SETUP_GUIDE.md        # Webhook setup
│   │       ├── lambda_function.py    # Function code
│   │       └── requirements.txt      # Dependencies
│   │
│   └── api-gateway/
│       └── SETUP_GUIDE.md            # API Gateway configuration
│
└── cloudflare-setup/
    └── SETUP_GUIDE.md                # Cloudflare email routing
```

## 🎯 Email Address Format

All generated email addresses follow this pattern:

```
user_<telegram_user_id>_<random_6_chars>@csearfarf.dev

Examples:
- user_123456789_abc123@csearfarf.dev
- user_987654321_xyz789@csearfarf.dev
```

**Components**:
- `user_` - Fixed prefix
- `<telegram_user_id>` - User's Telegram chat ID (numeric)
- `<random_6_chars>` - Random alphanumeric suffix for uniqueness
- `@csearfarf.dev` - Domain registered with Cloudflare

## 🔧 Technology Stack

### AWS Services
- **Lambda**: Serverless compute for all functions
- **DynamoDB**: NoSQL database for user data and email summaries
- **S3**: Object storage for raw email content
- **API Gateway**: REST API endpoint for Telegram webhook
- **CloudWatch**: Logging and monitoring
- **Systems Manager Parameter Store**: Secure credential storage

### External Services
- **Cloudflare**: Domain management and email routing
- **Gmail**: Email reception via IMAP
- **Telegram Bot API**: User interface and notifications
- **OpenAI API**: GPT-3.5-turbo for email summarization

### Development
- **Language**: Python 3.9+
- **Libraries**: boto3, requests, openai
- **Deployment**: AWS CLI, ZIP packages

## 📊 How It Works

### Step 1: User Registration
1. User starts conversation with Telegram bot
2. Sends `/start` command
3. Bot creates user record in DynamoDB
4. User receives welcome message

### Step 2: Email Generation
1. User sends `/generate_email` command
2. System generates unique email address
3. Address format: `user_<telegram_id>_<random>@csearfarf.dev`
4. Stored in DynamoDB linked to user
5. User receives email address in Telegram

### Step 3: Email Processing
1. Someone sends email to user's generated address
2. Cloudflare Email Router receives email
3. Cloudflare Worker validates format and forwards to Gmail
4. Email Fetcher Lambda polls Gmail every 5 minutes
5. New email detected and stored in S3
6. S3 event triggers Email Processor Lambda
7. Email content sent to OpenAI for summarization
8. Summary generated (2-3 sentences)
9. Summary stored in DynamoDB
10. Telegram notification sent to user with summary

### Step 4: User Receives Summary
User gets formatted message in Telegram:
```
📧 New Email Summary

From: sender@example.com
Subject: Meeting Update

Summary:
The meeting has been rescheduled to 3 PM tomorrow. 
Please confirm your attendance.

Received: Wed, 13 Nov 2024 10:30:00 UTC
```

## 💰 Cost Estimate

Monthly costs (based on moderate usage - ~500 emails/month):

| Service | Cost | Notes |
|---------|------|-------|
| AWS Lambda | $2-5 | First 1M requests free |
| DynamoDB | $1-3 | On-demand pricing |
| S3 | $1-2 | Storage + requests |
| API Gateway | $1-2 | First 1M requests $3.50 |
| CloudWatch | $0-1 | Basic monitoring free |
| OpenAI API | $5-15 | GPT-3.5-turbo usage |
| Cloudflare | $0 | Free plan sufficient |
| **Total** | **$10-30/month** | Variable based on usage |

**Cost Optimization Tips**:
- Use S3 lifecycle policies to archive old emails
- Optimize Lambda memory allocation
- Monitor OpenAI API usage
- Use DynamoDB on-demand billing

## 🔐 Security Features

- **Encrypted Storage**: All data encrypted at rest (S3, DynamoDB)
- **Secure Transmission**: TLS/HTTPS for all API calls
- **Credential Management**: Secrets stored in AWS Systems Manager
- **IAM Roles**: Least-privilege access policies
- **Email Validation**: Format validation prevents abuse
- **Rate Limiting**: Prevents spam and abuse

## 🐛 Troubleshooting

### Common Issues

**1. Email not received in Telegram**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/email-fetcher --follow
aws logs tail /aws/lambda/email-processor --follow

# Verify S3 storage
aws s3 ls s3://YOUR_BUCKET/emails/ --recursive
```

**2. Telegram commands not working**
```bash
# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo

# Check Lambda webhook logs
aws logs tail /aws/lambda/telegram-webhook --follow
```

**3. OpenAI summarization failing**
```bash
# Verify API key
aws ssm get-parameter --name /openai/api-key --with-decryption

# Check processor logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/email-processor \
  --filter-pattern "OpenAI"
```

For detailed troubleshooting, see each component's setup guide.

## 📚 Complete Documentation

### Quick Access
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 2 hours
- 📖 **[Setup Index](SETUP_INDEX.md)** - Navigation hub for all setup guides
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- 📝 **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all docs

### Component Setup Guides
- **AWS Services**
  - [DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md) - User data storage
  - [S3 Setup](aws/s3/SETUP_GUIDE.md) - Email storage
  - [API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md) - Webhook endpoint
  
- **Lambda Functions**
  - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md) - Bot interface
  - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md) - IMAP email retrieval
  - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md) - AI summarization
  
- **Email Routing**
  - [Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md) - Email forwarding & DNS

---

## 🎯 Project Overview

SevenBot is an intelligent email summarization system that generates unique email addresses for Telegram users, processes incoming emails, and delivers AI-powered summaries directly to Telegram. Built entirely on serverless architecture using AWS Lambda, DynamoDB, S3, Cloudflare Email Routing, and OpenAI GPT.

**Domain**: csearfarf.dev  
**Platform**: AWS + Cloudflare + Telegram  
**AI Engine**: OpenAI GPT-3.5-turbo

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│ Telegram User│────▶│ Telegram Bot   │────▶│  DynamoDB   │
│              │     │ (API Gateway + │     │   (Users)   │
│              │     │   Lambda)      │     │             │
└──────────────┘     └────────────────┘     └─────────────┘
                              │
                              │
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│   Email      │────▶│  Cloudflare    │────▶│    Gmail    │
│   Sender     │     │  Email Router  │     │    IMAP     │
└──────────────┘     └────────────────┘     └─────────────┘
                                                     │
                                                     ▼
                              ┌────────────────────────────┐
                              │  Email Fetcher Lambda      │
                              │  (Polls every 5 minutes)   │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │         S3 Bucket          │
                              │    (Email Storage)         │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │  Email Processor Lambda    │
                              │  (OpenAI Summarization)    │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │    Telegram Notification   │
                              │    (Summary Delivered)     │
                              └────────────────────────────┘
```

## ✨ Key Features

- **Unique Email Generation**: Each user gets personalized email addresses (e.g., `user_123456789_abc123@csearfarf.dev`)
- **AI-Powered Summaries**: OpenAI GPT creates concise 2-3 sentence email summaries
- **Real-Time Notifications**: Instant Telegram notifications when emails arrive
- **Serverless Architecture**: Zero server management, scales automatically
- **Secure & Private**: Email content encrypted, user data protected
- **Cost-Effective**: Pay only for what you use

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS Account (AWS Academy Lab or personal account)
- [ ] Cloudflare Account with domain (csearfarf.dev)
- [ ] Telegram Account
- [ ] Gmail Account with App Password
- [ ] OpenAI API Account
- [ ] AWS CLI installed and configured
- [ ] Basic knowledge of Python, AWS Lambda, and REST APIs

## 🚀 Quick Start

### 1. Clone or Download This Repository
```bash
cd "d:\Opensource Dev\238\sevenbot"
```

### 2. Follow the Setup Guides in Order

1. **[Architecture Guide](ARCHITECTURE.md)** - Understand the system design
2. **[AWS DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md)** - Create database tables
3. **[AWS S3 Setup](aws/s3/SETUP_GUIDE.md)** - Configure email storage
4. **[AWS Lambda Functions](aws/lambda-functions/)** - Deploy all three functions
   - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
   - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md)
   - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md)
5. **[AWS API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md)** - Create webhook endpoint
6. **[Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md)** - Configure email routing

### 3. Test the System
```bash
# Send a test email
echo "Test email body" | mail -s "Test Subject" user_123456789_abc123@csearfarf.dev

# Check if summary arrives in Telegram
```

## 📁 Project Structure

```
sevenbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture guide
│
├── aws/
│   ├── dynamodb/
│   │   └── SETUP_GUIDE.md            # DynamoDB tables setup
│   │
│   ├── s3/
│   │   └── SETUP_GUIDE.md            # S3 bucket configuration
│   │
│   ├── lambda-functions/
│   │   ├── email-fetcher/
│   │   │   ├── SETUP_GUIDE.md        # Email fetcher setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   ├── email-processor/
│   │   │   ├── SETUP_GUIDE.md        # Email processor setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   └── telegram-webhook/
│   │       ├── SETUP_GUIDE.md        # Webhook setup
│   │       ├── lambda_function.py    # Function code
│   │       └── requirements.txt      # Dependencies
│   │
│   └── api-gateway/
│       └── SETUP_GUIDE.md            # API Gateway configuration
│
└── cloudflare-setup/
    └── SETUP_GUIDE.md                # Cloudflare email routing
```

## 🎯 Email Address Format

All generated email addresses follow this pattern:

```
user_<telegram_user_id>_<random_6_chars>@csearfarf.dev

Examples:
- user_123456789_abc123@csearfarf.dev
- user_987654321_xyz789@csearfarf.dev
```

**Components**:
- `user_` - Fixed prefix
- `<telegram_user_id>` - User's Telegram chat ID (numeric)
- `<random_6_chars>` - Random alphanumeric suffix for uniqueness
- `@csearfarf.dev` - Domain registered with Cloudflare

## 🔧 Technology Stack

### AWS Services
- **Lambda**: Serverless compute for all functions
- **DynamoDB**: NoSQL database for user data and email summaries
- **S3**: Object storage for raw email content
- **API Gateway**: REST API endpoint for Telegram webhook
- **CloudWatch**: Logging and monitoring
- **Systems Manager Parameter Store**: Secure credential storage

### External Services
- **Cloudflare**: Domain management and email routing
- **Gmail**: Email reception via IMAP
- **Telegram Bot API**: User interface and notifications
- **OpenAI API**: GPT-3.5-turbo for email summarization

### Development
- **Language**: Python 3.9+
- **Libraries**: boto3, requests, openai
- **Deployment**: AWS CLI, ZIP packages

## 📊 How It Works

### Step 1: User Registration
1. User starts conversation with Telegram bot
2. Sends `/start` command
3. Bot creates user record in DynamoDB
4. User receives welcome message

### Step 2: Email Generation
1. User sends `/generate_email` command
2. System generates unique email address
3. Address format: `user_<telegram_id>_<random>@csearfarf.dev`
4. Stored in DynamoDB linked to user
5. User receives email address in Telegram

### Step 3: Email Processing
1. Someone sends email to user's generated address
2. Cloudflare Email Router receives email
3. Cloudflare Worker validates format and forwards to Gmail
4. Email Fetcher Lambda polls Gmail every 5 minutes
5. New email detected and stored in S3
6. S3 event triggers Email Processor Lambda
7. Email content sent to OpenAI for summarization
8. Summary generated (2-3 sentences)
9. Summary stored in DynamoDB
10. Telegram notification sent to user with summary

### Step 4: User Receives Summary
User gets formatted message in Telegram:
```
📧 New Email Summary

From: sender@example.com
Subject: Meeting Update

Summary:
The meeting has been rescheduled to 3 PM tomorrow. 
Please confirm your attendance.

Received: Wed, 13 Nov 2024 10:30:00 UTC
```

## 💰 Cost Estimate

Monthly costs (based on moderate usage - ~500 emails/month):

| Service | Cost | Notes |
|---------|------|-------|
| AWS Lambda | $2-5 | First 1M requests free |
| DynamoDB | $1-3 | On-demand pricing |
| S3 | $1-2 | Storage + requests |
| API Gateway | $1-2 | First 1M requests $3.50 |
| CloudWatch | $0-1 | Basic monitoring free |
| OpenAI API | $5-15 | GPT-3.5-turbo usage |
| Cloudflare | $0 | Free plan sufficient |
| **Total** | **$10-30/month** | Variable based on usage |

**Cost Optimization Tips**:
- Use S3 lifecycle policies to archive old emails
- Optimize Lambda memory allocation
- Monitor OpenAI API usage
- Use DynamoDB on-demand billing

## 🔐 Security Features

- **Encrypted Storage**: All data encrypted at rest (S3, DynamoDB)
- **Secure Transmission**: TLS/HTTPS for all API calls
- **Credential Management**: Secrets stored in AWS Systems Manager
- **IAM Roles**: Least-privilege access policies
- **Email Validation**: Format validation prevents abuse
- **Rate Limiting**: Prevents spam and abuse

## 🐛 Troubleshooting

### Common Issues

**1. Email not received in Telegram**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/email-fetcher --follow
aws logs tail /aws/lambda/email-processor --follow

# Verify S3 storage
aws s3 ls s3://YOUR_BUCKET/emails/ --recursive
```

**2. Telegram commands not working**
```bash
# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo

# Check Lambda webhook logs
aws logs tail /aws/lambda/telegram-webhook --follow
```

**3. OpenAI summarization failing**
```bash
# Verify API key
aws ssm get-parameter --name /openai/api-key --with-decryption

# Check processor logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/email-processor \
  --filter-pattern "OpenAI"
```

For detailed troubleshooting, see each component's setup guide.

## 📚 Complete Documentation

### Quick Access
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 2 hours
- 📖 **[Setup Index](SETUP_INDEX.md)** - Navigation hub for all setup guides
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- 📝 **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all docs

### Component Setup Guides
- **AWS Services**
  - [DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md) - User data storage
  - [S3 Setup](aws/s3/SETUP_GUIDE.md) - Email storage
  - [API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md) - Webhook endpoint
  
- **Lambda Functions**
  - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md) - Bot interface
  - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md) - IMAP email retrieval
  - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md) - AI summarization
  
- **Email Routing**
  - [Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md) - Email forwarding & DNS

---

## 🎯 Project Overview

SevenBot is an intelligent email summarization system that generates unique email addresses for Telegram users, processes incoming emails, and delivers AI-powered summaries directly to Telegram. Built entirely on serverless architecture using AWS Lambda, DynamoDB, S3, Cloudflare Email Routing, and OpenAI GPT.

**Domain**: csearfarf.dev  
**Platform**: AWS + Cloudflare + Telegram  
**AI Engine**: OpenAI GPT-3.5-turbo

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│ Telegram User│────▶│ Telegram Bot   │────▶│  DynamoDB   │
│              │     │ (API Gateway + │     │   (Users)   │
│              │     │   Lambda)      │     │             │
└──────────────┘     └────────────────┘     └─────────────┘
                              │
                              │
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│   Email      │────▶│  Cloudflare    │────▶│    Gmail    │
│   Sender     │     │  Email Router  │     │    IMAP     │
└──────────────┘     └────────────────┘     └─────────────┘
                                                     │
                                                     ▼
                              ┌────────────────────────────┐
                              │  Email Fetcher Lambda      │
                              │  (Polls every 5 minutes)   │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │         S3 Bucket          │
                              │    (Email Storage)         │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │  Email Processor Lambda    │
                              │  (OpenAI Summarization)    │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │    Telegram Notification   │
                              │    (Summary Delivered)     │
                              └────────────────────────────┘
```

## ✨ Key Features

- **Unique Email Generation**: Each user gets personalized email addresses (e.g., `user_123456789_abc123@csearfarf.dev`)
- **AI-Powered Summaries**: OpenAI GPT creates concise 2-3 sentence email summaries
- **Real-Time Notifications**: Instant Telegram notifications when emails arrive
- **Serverless Architecture**: Zero server management, scales automatically
- **Secure & Private**: Email content encrypted, user data protected
- **Cost-Effective**: Pay only for what you use

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS Account (AWS Academy Lab or personal account)
- [ ] Cloudflare Account with domain (csearfarf.dev)
- [ ] Telegram Account
- [ ] Gmail Account with App Password
- [ ] OpenAI API Account
- [ ] AWS CLI installed and configured
- [ ] Basic knowledge of Python, AWS Lambda, and REST APIs

## 🚀 Quick Start

### 1. Clone or Download This Repository
```bash
cd "d:\Opensource Dev\238\sevenbot"
```

### 2. Follow the Setup Guides in Order

1. **[Architecture Guide](ARCHITECTURE.md)** - Understand the system design
2. **[AWS DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md)** - Create database tables
3. **[AWS S3 Setup](aws/s3/SETUP_GUIDE.md)** - Configure email storage
4. **[AWS Lambda Functions](aws/lambda-functions/)** - Deploy all three functions
   - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
   - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md)
   - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md)
5. **[AWS API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md)** - Create webhook endpoint
6. **[Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md)** - Configure email routing

### 3. Test the System
```bash
# Send a test email
echo "Test email body" | mail -s "Test Subject" user_123456789_abc123@csearfarf.dev

# Check if summary arrives in Telegram
```

## 📁 Project Structure

```
sevenbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture guide
│
├── aws/
│   ├── dynamodb/
│   │   └── SETUP_GUIDE.md            # DynamoDB tables setup
│   │
│   ├── s3/
│   │   └── SETUP_GUIDE.md            # S3 bucket configuration
│   │
│   ├── lambda-functions/
│   │   ├── email-fetcher/
│   │   │   ├── SETUP_GUIDE.md        # Email fetcher setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   ├── email-processor/
│   │   │   ├── SETUP_GUIDE.md        # Email processor setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   └── telegram-webhook/
│   │       ├── SETUP_GUIDE.md        # Webhook setup
│   │       ├── lambda_function.py    # Function code
│   │       └── requirements.txt      # Dependencies
│   │
│   └── api-gateway/
│       └── SETUP_GUIDE.md            # API Gateway configuration
│
└── cloudflare-setup/
    └── SETUP_GUIDE.md                # Cloudflare email routing
```

## 🎯 Email Address Format

All generated email addresses follow this pattern:

```
user_<telegram_user_id>_<random_6_chars>@csearfarf.dev

Examples:
- user_123456789_abc123@csearfarf.dev
- user_987654321_xyz789@csearfarf.dev
```

**Components**:
- `user_` - Fixed prefix
- `<telegram_user_id>` - User's Telegram chat ID (numeric)
- `<random_6_chars>` - Random alphanumeric suffix for uniqueness
- `@csearfarf.dev` - Domain registered with Cloudflare

## 🔧 Technology Stack

### AWS Services
- **Lambda**: Serverless compute for all functions
- **DynamoDB**: NoSQL database for user data and email summaries
- **S3**: Object storage for raw email content
- **API Gateway**: REST API endpoint for Telegram webhook
- **CloudWatch**: Logging and monitoring
- **Systems Manager Parameter Store**: Secure credential storage

### External Services
- **Cloudflare**: Domain management and email routing
- **Gmail**: Email reception via IMAP
- **Telegram Bot API**: User interface and notifications
- **OpenAI API**: GPT-3.5-turbo for email summarization

### Development
- **Language**: Python 3.9+
- **Libraries**: boto3, requests, openai
- **Deployment**: AWS CLI, ZIP packages

## 📊 How It Works

### Step 1: User Registration
1. User starts conversation with Telegram bot
2. Sends `/start` command
3. Bot creates user record in DynamoDB
4. User receives welcome message

### Step 2: Email Generation
1. User sends `/generate_email` command
2. System generates unique email address
3. Address format: `user_<telegram_id>_<random>@csearfarf.dev`
4. Stored in DynamoDB linked to user
5. User receives email address in Telegram

### Step 3: Email Processing
1. Someone sends email to user's generated address
2. Cloudflare Email Router receives email
3. Cloudflare Worker validates format and forwards to Gmail
4. Email Fetcher Lambda polls Gmail every 5 minutes
5. New email detected and stored in S3
6. S3 event triggers Email Processor Lambda
7. Email content sent to OpenAI for summarization
8. Summary generated (2-3 sentences)
9. Summary stored in DynamoDB
10. Telegram notification sent to user with summary

### Step 4: User Receives Summary
User gets formatted message in Telegram:
```
📧 New Email Summary

From: sender@example.com
Subject: Meeting Update

Summary:
The meeting has been rescheduled to 3 PM tomorrow. 
Please confirm your attendance.

Received: Wed, 13 Nov 2024 10:30:00 UTC
```

## 💰 Cost Estimate

Monthly costs (based on moderate usage - ~500 emails/month):

| Service | Cost | Notes |
|---------|------|-------|
| AWS Lambda | $2-5 | First 1M requests free |
| DynamoDB | $1-3 | On-demand pricing |
| S3 | $1-2 | Storage + requests |
| API Gateway | $1-2 | First 1M requests $3.50 |
| CloudWatch | $0-1 | Basic monitoring free |
| OpenAI API | $5-15 | GPT-3.5-turbo usage |
| Cloudflare | $0 | Free plan sufficient |
| **Total** | **$10-30/month** | Variable based on usage |

**Cost Optimization Tips**:
- Use S3 lifecycle policies to archive old emails
- Optimize Lambda memory allocation
- Monitor OpenAI API usage
- Use DynamoDB on-demand billing

## 🔐 Security Features

- **Encrypted Storage**: All data encrypted at rest (S3, DynamoDB)
- **Secure Transmission**: TLS/HTTPS for all API calls
- **Credential Management**: Secrets stored in AWS Systems Manager
- **IAM Roles**: Least-privilege access policies
- **Email Validation**: Format validation prevents abuse
- **Rate Limiting**: Prevents spam and abuse

## 🐛 Troubleshooting

### Common Issues

**1. Email not received in Telegram**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/email-fetcher --follow
aws logs tail /aws/lambda/email-processor --follow

# Verify S3 storage
aws s3 ls s3://YOUR_BUCKET/emails/ --recursive
```

**2. Telegram commands not working**
```bash
# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo

# Check Lambda webhook logs
aws logs tail /aws/lambda/telegram-webhook --follow
```

**3. OpenAI summarization failing**
```bash
# Verify API key
aws ssm get-parameter --name /openai/api-key --with-decryption

# Check processor logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/email-processor \
  --filter-pattern "OpenAI"
```

For detailed troubleshooting, see each component's setup guide.

## 📚 Complete Documentation

### Quick Access
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 2 hours
- 📖 **[Setup Index](SETUP_INDEX.md)** - Navigation hub for all setup guides
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- 📝 **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all docs

### Component Setup Guides
- **AWS Services**
  - [DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md) - User data storage
  - [S3 Setup](aws/s3/SETUP_GUIDE.md) - Email storage
  - [API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md) - Webhook endpoint
  
- **Lambda Functions**
  - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md) - Bot interface
  - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md) - IMAP email retrieval
  - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md) - AI summarization
  
- **Email Routing**
  - [Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md) - Email forwarding & DNS

---

## 🎯 Project Overview

SevenBot is an intelligent email summarization system that generates unique email addresses for Telegram users, processes incoming emails, and delivers AI-powered summaries directly to Telegram. Built entirely on serverless architecture using AWS Lambda, DynamoDB, S3, Cloudflare Email Routing, and OpenAI GPT.

**Domain**: csearfarf.dev  
**Platform**: AWS + Cloudflare + Telegram  
**AI Engine**: OpenAI GPT-3.5-turbo

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│ Telegram User│────▶│ Telegram Bot   │────▶│  DynamoDB   │
│              │     │ (API Gateway + │     │   (Users)   │
│              │     │   Lambda)      │     │             │
└──────────────┘     └────────────────┘     └─────────────┘
                              │
                              │
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│   Email      │────▶│  Cloudflare    │────▶│    Gmail    │
│   Sender     │     │  Email Router  │     │    IMAP     │
└──────────────┘     └────────────────┘     └─────────────┘
                                                     │
                                                     ▼
                              ┌────────────────────────────┐
                              │  Email Fetcher Lambda      │
                              │  (Polls every 5 minutes)   │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │         S3 Bucket          │
                              │    (Email Storage)         │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │  Email Processor Lambda    │
                              │  (OpenAI Summarization)    │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │    Telegram Notification   │
                              │    (Summary Delivered)     │
                              └────────────────────────────┘
```

## ✨ Key Features

- **Unique Email Generation**: Each user gets personalized email addresses (e.g., `user_123456789_abc123@csearfarf.dev`)
- **AI-Powered Summaries**: OpenAI GPT creates concise 2-3 sentence email summaries
- **Real-Time Notifications**: Instant Telegram notifications when emails arrive
- **Serverless Architecture**: Zero server management, scales automatically
- **Secure & Private**: Email content encrypted, user data protected
- **Cost-Effective**: Pay only for what you use

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS Account (AWS Academy Lab or personal account)
- [ ] Cloudflare Account with domain (csearfarf.dev)
- [ ] Telegram Account
- [ ] Gmail Account with App Password
- [ ] OpenAI API Account
- [ ] AWS CLI installed and configured
- [ ] Basic knowledge of Python, AWS Lambda, and REST APIs

## 🚀 Quick Start

### 1. Clone or Download This Repository
```bash
cd "d:\Opensource Dev\238\sevenbot"
```

### 2. Follow the Setup Guides in Order

1. **[Architecture Guide](ARCHITECTURE.md)** - Understand the system design
2. **[AWS DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md)** - Create database tables
3. **[AWS S3 Setup](aws/s3/SETUP_GUIDE.md)** - Configure email storage
4. **[AWS Lambda Functions](aws/lambda-functions/)** - Deploy all three functions
   - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
   - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md)
   - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md)
5. **[AWS API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md)** - Create webhook endpoint
6. **[Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md)** - Configure email routing

### 3. Test the System
```bash
# Send a test email
echo "Test email body" | mail -s "Test Subject" user_123456789_abc123@csearfarf.dev

# Check if summary arrives in Telegram
```

## 📁 Project Structure

```
sevenbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture guide
│
├── aws/
│   ├── dynamodb/
│   │   └── SETUP_GUIDE.md            # DynamoDB tables setup
│   │
│   ├── s3/
│   │   └── SETUP_GUIDE.md            # S3 bucket configuration
│   │
│   ├── lambda-functions/
│   │   ├── email-fetcher/
│   │   │   ├── SETUP_GUIDE.md        # Email fetcher setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   ├── email-processor/
│   │   │   ├── SETUP_GUIDE.md        # Email processor setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   └── telegram-webhook/
│   │       ├── SETUP_GUIDE.md        # Webhook setup
│   │       ├── lambda_function.py    # Function code
│   │       └── requirements.txt      # Dependencies
│   │
│   └── api-gateway/
│       └── SETUP_GUIDE.md            # API Gateway configuration
│
└── cloudflare-setup/
    └── SETUP_GUIDE.md                # Cloudflare email routing
```

## 🎯 Email Address Format

All generated email addresses follow this pattern:

```
user_<telegram_user_id>_<random_6_chars>@csearfarf.dev

Examples:
- user_123456789_abc123@csearfarf.dev
- user_987654321_xyz789@csearfarf.dev
```

**Components**:
- `user_` - Fixed prefix
- `<telegram_user_id>` - User's Telegram chat ID (numeric)
- `<random_6_chars>` - Random alphanumeric suffix for uniqueness
- `@csearfarf.dev` - Domain registered with Cloudflare

## 🔧 Technology Stack

### AWS Services
- **Lambda**: Serverless compute for all functions
- **DynamoDB**: NoSQL database for user data and email summaries
- **S3**: Object storage for raw email content
- **API Gateway**: REST API endpoint for Telegram webhook
- **CloudWatch**: Logging and monitoring
- **Systems Manager Parameter Store**: Secure credential storage

### External Services
- **Cloudflare**: Domain management and email routing
- **Gmail**: Email reception via IMAP
- **Telegram Bot API**: User interface and notifications
- **OpenAI API**: GPT-3.5-turbo for email summarization

### Development
- **Language**: Python 3.9+
- **Libraries**: boto3, requests, openai
- **Deployment**: AWS CLI, ZIP packages

## 📊 How It Works

### Step 1: User Registration
1. User starts conversation with Telegram bot
2. Sends `/start` command
3. Bot creates user record in DynamoDB
4. User receives welcome message

### Step 2: Email Generation
1. User sends `/generate_email` command
2. System generates unique email address
3. Address format: `user_<telegram_id>_<random>@csearfarf.dev`
4. Stored in DynamoDB linked to user
5. User receives email address in Telegram

### Step 3: Email Processing
1. Someone sends email to user's generated address
2. Cloudflare Email Router receives email
3. Cloudflare Worker validates format and forwards to Gmail
4. Email Fetcher Lambda polls Gmail every 5 minutes
5. New email detected and stored in S3
6. S3 event triggers Email Processor Lambda
7. Email content sent to OpenAI for summarization
8. Summary generated (2-3 sentences)
9. Summary stored in DynamoDB
10. Telegram notification sent to user with summary

### Step 4: User Receives Summary
User gets formatted message in Telegram:
```
📧 New Email Summary

From: sender@example.com
Subject: Meeting Update

Summary:
The meeting has been rescheduled to 3 PM tomorrow. 
Please confirm your attendance.

Received: Wed, 13 Nov 2024 10:30:00 UTC
```

## 💰 Cost Estimate

Monthly costs (based on moderate usage - ~500 emails/month):

| Service | Cost | Notes |
|---------|------|-------|
| AWS Lambda | $2-5 | First 1M requests free |
| DynamoDB | $1-3 | On-demand pricing |
| S3 | $1-2 | Storage + requests |
| API Gateway | $1-2 | First 1M requests $3.50 |
| CloudWatch | $0-1 | Basic monitoring free |
| OpenAI API | $5-15 | GPT-3.5-turbo usage |
| Cloudflare | $0 | Free plan sufficient |
| **Total** | **$10-30/month** | Variable based on usage |

**Cost Optimization Tips**:
- Use S3 lifecycle policies to archive old emails
- Optimize Lambda memory allocation
- Monitor OpenAI API usage
- Use DynamoDB on-demand billing

## 🔐 Security Features

- **Encrypted Storage**: All data encrypted at rest (S3, DynamoDB)
- **Secure Transmission**: TLS/HTTPS for all API calls
- **Credential Management**: Secrets stored in AWS Systems Manager
- **IAM Roles**: Least-privilege access policies
- **Email Validation**: Format validation prevents abuse
- **Rate Limiting**: Prevents spam and abuse

## 🐛 Troubleshooting

### Common Issues

**1. Email not received in Telegram**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/email-fetcher --follow
aws logs tail /aws/lambda/email-processor --follow

# Verify S3 storage
aws s3 ls s3://YOUR_BUCKET/emails/ --recursive
```

**2. Telegram commands not working**
```bash
# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo

# Check Lambda webhook logs
aws logs tail /aws/lambda/telegram-webhook --follow
```

**3. OpenAI summarization failing**
```bash
# Verify API key
aws ssm get-parameter --name /openai/api-key --with-decryption

# Check processor logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/email-processor \
  --filter-pattern "OpenAI"
```

For detailed troubleshooting, see each component's setup guide.

## 📚 Complete Documentation

### Quick Access
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 2 hours
- 📖 **[Setup Index](SETUP_INDEX.md)** - Navigation hub for all setup guides
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- 📝 **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all docs

### Component Setup Guides
- **AWS Services**
  - [DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md) - User data storage
  - [S3 Setup](aws/s3/SETUP_GUIDE.md) - Email storage
  - [API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md) - Webhook endpoint
  
- **Lambda Functions**
  - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md) - Bot interface
  - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md) - IMAP email retrieval
  - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md) - AI summarization
  
- **Email Routing**
  - [Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md) - Email forwarding & DNS

---

## 🎯 Project Overview

SevenBot is an intelligent email summarization system that generates unique email addresses for Telegram users, processes incoming emails, and delivers AI-powered summaries directly to Telegram. Built entirely on serverless architecture using AWS Lambda, DynamoDB, S3, Cloudflare Email Routing, and OpenAI GPT.

**Domain**: csearfarf.dev  
**Platform**: AWS + Cloudflare + Telegram  
**AI Engine**: OpenAI GPT-3.5-turbo

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│ Telegram User│────▶│ Telegram Bot   │────▶│  DynamoDB   │
│              │     │ (API Gateway + │     │   (Users)   │
│              │     │   Lambda)      │     │             │
└──────────────┘     └────────────────┘     └─────────────┘
                              │
                              │
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│   Email      │────▶│  Cloudflare    │────▶│    Gmail    │
│   Sender     │     │  Email Router  │     │    IMAP     │
└──────────────┘     └────────────────┘     └─────────────┘
                                                     │
                                                     ▼
                              ┌────────────────────────────┐
                              │  Email Fetcher Lambda      │
                              │  (Polls every 5 minutes)   │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │         S3 Bucket          │
                              │    (Email Storage)         │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │  Email Processor Lambda    │
                              │  (OpenAI Summarization)    │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │    Telegram Notification   │
                              │    (Summary Delivered)     │
                              └────────────────────────────┘
```

## ✨ Key Features

- **Unique Email Generation**: Each user gets personalized email addresses (e.g., `user_123456789_abc123@csearfarf.dev`)
- **AI-Powered Summaries**: OpenAI GPT creates concise 2-3 sentence email summaries
- **Real-Time Notifications**: Instant Telegram notifications when emails arrive
- **Serverless Architecture**: Zero server management, scales automatically
- **Secure & Private**: Email content encrypted, user data protected
- **Cost-Effective**: Pay only for what you use

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS Account (AWS Academy Lab or personal account)
- [ ] Cloudflare Account with domain (csearfarf.dev)
- [ ] Telegram Account
- [ ] Gmail Account with App Password
- [ ] OpenAI API Account
- [ ] AWS CLI installed and configured
- [ ] Basic knowledge of Python, AWS Lambda, and REST APIs

## 🚀 Quick Start

### 1. Clone or Download This Repository
```bash
cd "d:\Opensource Dev\238\sevenbot"
```

### 2. Follow the Setup Guides in Order

1. **[Architecture Guide](ARCHITECTURE.md)** - Understand the system design
2. **[AWS DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md)** - Create database tables
3. **[AWS S3 Setup](aws/s3/SETUP_GUIDE.md)** - Configure email storage
4. **[AWS Lambda Functions](aws/lambda-functions/)** - Deploy all three functions
   - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
   - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md)
   - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md)
5. **[AWS API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md)** - Create webhook endpoint
6. **[Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md)** - Configure email routing

### 3. Test the System
```bash
# Send a test email
echo "Test email body" | mail -s "Test Subject" user_123456789_abc123@csearfarf.dev

# Check if summary arrives in Telegram
```

## 📁 Project Structure

```
sevenbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture guide
│
├── aws/
│   ├── dynamodb/
│   │   └── SETUP_GUIDE.md            # DynamoDB tables setup
│   │
│   ├── s3/
│   │   └── SETUP_GUIDE.md            # S3 bucket configuration
│   │
│   ├── lambda-functions/
│   │   ├── email-fetcher/
│   │   │   ├── SETUP_GUIDE.md        # Email fetcher setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   ├── email-processor/
│   │   │   ├── SETUP_GUIDE.md        # Email processor setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   └── telegram-webhook/
│   │       ├── SETUP_GUIDE.md        # Webhook setup
│   │       ├── lambda_function.py    # Function code
│   │       └── requirements.txt      # Dependencies
│   │
│   └── api-gateway/
│       └── SETUP_GUIDE.md            # API Gateway configuration
│
└── cloudflare-setup/
    └── SETUP_GUIDE.md                # Cloudflare email routing
```

## 🎯 Email Address Format

All generated email addresses follow this pattern:

```
user_<telegram_user_id>_<random_6_chars>@csearfarf.dev

Examples:
- user_123456789_abc123@csearfarf.dev
- user_987654321_xyz789@csearfarf.dev
```

**Components**:
- `user_` - Fixed prefix
- `<telegram_user_id>` - User's Telegram chat ID (numeric)
- `<random_6_chars>` - Random alphanumeric suffix for uniqueness
- `@csearfarf.dev` - Domain registered with Cloudflare

## 🔧 Technology Stack

### AWS Services
- **Lambda**: Serverless compute for all functions
- **DynamoDB**: NoSQL database for user data and email summaries
- **S3**: Object storage for raw email content
- **API Gateway**: REST API endpoint for Telegram webhook
- **CloudWatch**: Logging and monitoring
- **Systems Manager Parameter Store**: Secure credential storage

### External Services
- **Cloudflare**: Domain management and email routing
- **Gmail**: Email reception via IMAP
- **Telegram Bot API**: User interface and notifications
- **OpenAI API**: GPT-3.5-turbo for email summarization

### Development
- **Language**: Python 3.9+
- **Libraries**: boto3, requests, openai
- **Deployment**: AWS CLI, ZIP packages

## 📊 How It Works

### Step 1: User Registration
1. User starts conversation with Telegram bot
2. Sends `/start` command
3. Bot creates user record in DynamoDB
4. User receives welcome message

### Step 2: Email Generation
1. User sends `/generate_email` command
2. System generates unique email address
3. Address format: `user_<telegram_id>_<random>@csearfarf.dev`
4. Stored in DynamoDB linked to user
5. User receives email address in Telegram

### Step 3: Email Processing
1. Someone sends email to user's generated address
2. Cloudflare Email Router receives email
3. Cloudflare Worker validates format and forwards to Gmail
4. Email Fetcher Lambda polls Gmail every 5 minutes
5. New email detected and stored in S3
6. S3 event triggers Email Processor Lambda
7. Email content sent to OpenAI for summarization
8. Summary generated (2-3 sentences)
9. Summary stored in DynamoDB
10. Telegram notification sent to user with summary

### Step 4: User Receives Summary
User gets formatted message in Telegram:
```
📧 New Email Summary

From: sender@example.com
Subject: Meeting Update

Summary:
The meeting has been rescheduled to 3 PM tomorrow. 
Please confirm your attendance.

Received: Wed, 13 Nov 2024 10:30:00 UTC
```

## 💰 Cost Estimate

Monthly costs (based on moderate usage - ~500 emails/month):

| Service | Cost | Notes |
|---------|------|-------|
| AWS Lambda | $2-5 | First 1M requests free |
| DynamoDB | $1-3 | On-demand pricing |
| S3 | $1-2 | Storage + requests |
| API Gateway | $1-2 | First 1M requests $3.50 |
| CloudWatch | $0-1 | Basic monitoring free |
| OpenAI API | $5-15 | GPT-3.5-turbo usage |
| Cloudflare | $0 | Free plan sufficient |
| **Total** | **$10-30/month** | Variable based on usage |

**Cost Optimization Tips**:
- Use S3 lifecycle policies to archive old emails
- Optimize Lambda memory allocation
- Monitor OpenAI API usage
- Use DynamoDB on-demand billing

## 🔐 Security Features

- **Encrypted Storage**: All data encrypted at rest (S3, DynamoDB)
- **Secure Transmission**: TLS/HTTPS for all API calls
- **Credential Management**: Secrets stored in AWS Systems Manager
- **IAM Roles**: Least-privilege access policies
- **Email Validation**: Format validation prevents abuse
- **Rate Limiting**: Prevents spam and abuse

## 🐛 Troubleshooting

### Common Issues

**1. Email not received in Telegram**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/email-fetcher --follow
aws logs tail /aws/lambda/email-processor --follow

# Verify S3 storage
aws s3 ls s3://YOUR_BUCKET/emails/ --recursive
```

**2. Telegram commands not working**
```bash
# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo

# Check Lambda webhook logs
aws logs tail /aws/lambda/telegram-webhook --follow
```

**3. OpenAI summarization failing**
```bash
# Verify API key
aws ssm get-parameter --name /openai/api-key --with-decryption

# Check processor logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/email-processor \
  --filter-pattern "OpenAI"
```

For detailed troubleshooting, see each component's setup guide.

## 📚 Complete Documentation

### Quick Access
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 2 hours
- 📖 **[Setup Index](SETUP_INDEX.md)** - Navigation hub for all setup guides
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- 📝 **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all docs

### Component Setup Guides
- **AWS Services**
  - [DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md) - User data storage
  - [S3 Setup](aws/s3/SETUP_GUIDE.md) - Email storage
  - [API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md) - Webhook endpoint
  
- **Lambda Functions**
  - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md) - Bot interface
  - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md) - IMAP email retrieval
  - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md) - AI summarization
  
- **Email Routing**
  - [Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md) - Email forwarding & DNS

---

## 🎯 Project Overview

SevenBot is an intelligent email summarization system that generates unique email addresses for Telegram users, processes incoming emails, and delivers AI-powered summaries directly to Telegram. Built entirely on serverless architecture using AWS Lambda, DynamoDB, S3, Cloudflare Email Routing, and OpenAI GPT.

**Domain**: csearfarf.dev  
**Platform**: AWS + Cloudflare + Telegram  
**AI Engine**: OpenAI GPT-3.5-turbo

## 🏗️ Architecture

```
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│ Telegram User│────▶│ Telegram Bot   │────▶│  DynamoDB   │
│              │     │ (API Gateway + │     │   (Users)   │
│              │     │   Lambda)      │     │             │
└──────────────┘     └────────────────┘     └─────────────┘
                              │
                              │
┌──────────────┐     ┌────────────────┐     ┌─────────────┐
│   Email      │────▶│  Cloudflare    │────▶│    Gmail    │
│   Sender     │     │  Email Router  │     │    IMAP     │
└──────────────┘     └────────────────┘     └─────────────┘
                                                     │
                                                     ▼
                              ┌────────────────────────────┐
                              │  Email Fetcher Lambda      │
                              │  (Polls every 5 minutes)   │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │         S3 Bucket          │
                              │    (Email Storage)         │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │  Email Processor Lambda    │
                              │  (OpenAI Summarization)    │
                              └────────────────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────┐
                              │    Telegram Notification   │
                              │    (Summary Delivered)     │
                              └────────────────────────────┘
```

## ✨ Key Features

- **Unique Email Generation**: Each user gets personalized email addresses (e.g., `user_123456789_abc123@csearfarf.dev`)
- **AI-Powered Summaries**: OpenAI GPT creates concise 2-3 sentence email summaries
- **Real-Time Notifications**: Instant Telegram notifications when emails arrive
- **Serverless Architecture**: Zero server management, scales automatically
- **Secure & Private**: Email content encrypted, user data protected
- **Cost-Effective**: Pay only for what you use

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS Account (AWS Academy Lab or personal account)
- [ ] Cloudflare Account with domain (csearfarf.dev)
- [ ] Telegram Account
- [ ] Gmail Account with App Password
- [ ] OpenAI API Account
- [ ] AWS CLI installed and configured
- [ ] Basic knowledge of Python, AWS Lambda, and REST APIs

## 🚀 Quick Start

### 1. Clone or Download This Repository
```bash
cd "d:\Opensource Dev\238\sevenbot"
```

### 2. Follow the Setup Guides in Order

1. **[Architecture Guide](ARCHITECTURE.md)** - Understand the system design
2. **[AWS DynamoDB Setup](aws/dynamodb/SETUP_GUIDE.md)** - Create database tables
3. **[AWS S3 Setup](aws/s3/SETUP_GUIDE.md)** - Configure email storage
4. **[AWS Lambda Functions](aws/lambda-functions/)** - Deploy all three functions
   - [Email Fetcher](aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
   - [Email Processor](aws/lambda-functions/email-processor/SETUP_GUIDE.md)
   - [Telegram Webhook](aws/lambda-functions/telegram-webhook/SETUP_GUIDE.md)
5. **[AWS API Gateway Setup](aws/api-gateway/SETUP_GUIDE.md)** - Create webhook endpoint
6. **[Cloudflare Setup](cloudflare-setup/SETUP_GUIDE.md)** - Configure email routing

### 3. Test the System
```bash
# Send a test email
echo "Test email body" | mail -s "Test Subject" user_123456789_abc123@csearfarf.dev

# Check if summary arrives in Telegram
```

## 📁 Project Structure

```
sevenbot/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture guide
│
├── aws/
│   ├── dynamodb/
│   │   └── SETUP_GUIDE.md            # DynamoDB tables setup
│   │
│   ├── s3/
│   │   └── SETUP_GUIDE.md            # S3 bucket configuration
│   │
│   ├── lambda-functions/
│   │   ├── email-fetcher/
│   │   │   ├── SETUP_GUIDE.md        # Email fetcher setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   ├── email-processor/
│   │   │   ├── SETUP_GUIDE.md        # Email processor setup
│   │   │   ├── lambda_function.py    # Function code
│   │   │   └── requirements.txt      # Dependencies
│   │   │
│   │   └── telegram-webhook/
│   │       ├── SETUP_GUIDE.md        # Webhook setup
│   │       ├── lambda_function.py    # Function code
│   │       └── requirements.txt      # Dependencies
│   │
│   └── api-gateway/
│       └── SETUP_GUIDE.md            # API Gateway configuration
│
└── cloudflare-setup/
    └── SETUP_GUIDE.md                # Cloudflare email routing
```

## 🎯 Email Address Format

All generated email addresses follow this pattern:

```
user_<telegram_user_id>_<random_6_chars>@csearfarf.dev

Examples:
- user_123456789_abc123@csearfarf.dev
- user_987654321_xyz789@csearfarf.dev
```

**Components**:
- `user_` - Fixed prefix
- `<telegram_user_id>` - User's Telegram chat ID (numeric)
- `<random_6_chars>` - Random alphanumeric suffix for uniqueness
- `@csearfarf.dev` - Domain registered with Cloudflare

## 🔧 Technology Stack

### AWS Services
- **Lambda**: Serverless compute for all functions
- **DynamoDB**: NoSQL database for user data and email summaries
- **S3**: Object storage for raw email content
- **API Gateway**: REST API endpoint for Telegram webhook
- **CloudWatch**: Logging and monitoring
- **Systems Manager Parameter Store**: Secure credential storage

### External Services
- **Cloudflare**: Domain management and email routing
- **Gmail**: Email reception via IMAP
- **Telegram Bot API**: User interface and notifications
- **OpenAI API**: GPT-3.5-turbo for email summarization

### Development
- **Language**: Python 3.9+
- **Libraries**: boto3, requests, openai
- **Deployment**: AWS CLI, ZIP packages

## 📊 How It Works

### Step 1: User Registration
1. User starts conversation with Telegram bot
2. Sends `/start` command
3. Bot creates user record in DynamoDB
4. User receives welcome message

### Step 2: Email Generation
1. User sends `/generate_email` command
2. System generates unique email address
3. Address format: `user_<telegram_id>_<random>@csearfarf.dev`
4. Stored in DynamoDB linked to user
5. User receives email address in Telegram

### Step 3: Email Processing
1. Someone sends email to user's generated address
2. Cloudflare Email Router receives email
3. Cloudflare Worker validates format and forwards to Gmail
4. Email Fetcher Lambda polls Gmail every 5 minutes
5. New email detected and stored in S3
6. S3 event triggers Email Processor Lambda
7. Email content sent to OpenAI for summarization
8. Summary generated (2-3 sentences)
9. Summary stored in DynamoDB
10. Telegram notification sent to user with summary

### Step 4: User Receives Summary
User gets formatted message in Telegram:
```
📧 New Email Summary

From: sender@example.com
Subject: Meeting Update

Summary:
The meeting has been rescheduled to 3 PM tomorrow. 
Please confirm your attendance.

Received: Wed, 13 Nov 2024 10:30:00 UTC
```

## 💰 Cost Estimate

Monthly costs (based on moderate usage - ~500 emails/month):

| Service | Cost | Notes |
|---------|------|-------|
| AWS Lambda | $2-5 | First 1M requests free |
| DynamoDB | $1-3 | On-demand pricing |
| S3 | $1-2 | Storage + requests |
| API Gateway | $1-2 | First 1M requests $3.50 |
| CloudWatch | $0-1 | Basic monitoring free |
| OpenAI API | $5-15 | GPT-3.5-turbo usage |
| Cloudflare | $0 | Free plan sufficient |
| **Total** | **$10-30/month** | Variable based on usage |

**Cost Optimization Tips**:
- Use S3 lifecycle policies to archive old emails
- Optimize Lambda memory allocation
- Monitor OpenAI API usage
- Use DynamoDB on-demand billing

## 🔐 Security Features

- **Encrypted Storage**: All data encrypted at rest (S3, DynamoDB)
- **Secure Transmission**: TLS/HTTPS for all API calls
- **Credential Management**: Secrets stored in AWS Systems Manager
- **IAM Roles**: Least-privilege access policies
- **Email Validation**: Format validation prevents abuse
- **Rate Limiting**: Prevents spam and abuse

## 🐛 Troubleshooting

### Common Issues

**1. Email not received in Telegram**
```bash
# Check Lambda logs
aws logs tail /aws/lambda/email-fetcher --follow
aws logs tail /aws/lambda/email-processor --follow

# Verify S3 storage
aws s3 ls s3://YOUR_BUCKET/emails/ --recursive
```

**2. Telegram commands not working**
```bash
# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo

# Check Lambda webhook logs
aws logs tail /aws/lambda/telegram-webhook --follow
```

**3. OpenAI summarization failing**
```bash
# Verify API key
aws ssm get-parameter --name /openai/api-key --with-decryption

# Check processor logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/email-processor \
  --filter-pattern "OpenAI"
```

For detailed troubleshooting, see each component's setup guide.

## 📚 Complete Documentation

### Quick Access
- 🚀 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 2 hours
- 📖 **[Setup Index](SETUP_INDEX.md)** - Navigation hub for all setup guides
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- 📝 **[Documentation Summary](DOCUMENTATION_SUMMARY.md)** - Overview of all docs

### Component Setup Guides
-