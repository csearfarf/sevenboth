# Email Processor Lambda Setup Guide

## Overview

The Email Processor Lambda function is triggered when a new email is stored in S3. It extracts the recipient's Telegram user ID, generates an AI summary using OpenAI, and sends a notification to the user via Telegram.

## Prerequisites

- S3 bucket created with event notifications configured
- DynamoDB table (`telegram-users`) created
- OpenAI API key
- Telegram bot token
- AWS Lambda execution role with necessary permissions

## Architecture

```
S3 Event (New Email)
         ↓
  Email Processor Lambda
         ↓
   Extract User ID
         ↓
   Fetch from DynamoDB
         ↓
   Generate Summary (OpenAI)
         ↓
   Send to Telegram
         ↓
   Update DynamoDB
```

---

## Step 1: Prepare Lambda Function Code

### Create Project Directory

```bash
mkdir email-processor
cd email-processor
```

### Create lambda_function.py

```python
import boto3
import json
import requests
import logging
import os
import html
from urllib.parse import unquote_plus
from datetime import datetime

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('telegram-users')

# Read secrets from env
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

def lambda_handler(event, context):
    try:
        # Process S3 events
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = unquote_plus(record['s3']['object']['key'])
            logger.info(f"Processing file: {key}")

            # Load email JSON from S3
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            email_data = json.loads(obj['Body'].read())

            # Map recipient to Telegram user id
            recipient_email = email_data.get('to', '')
            telegram_user_id = extract_user_id_from_email(recipient_email)
            if not telegram_user_id:
                logger.warning(f"Could not extract user ID from email: {recipient_email}")
                continue

            # Ensure user exists
            user_data = get_user_data(telegram_user_id)
            if not user_data:
                logger.warning(f"User not found: {telegram_user_id}")
                continue

            # Summarize and send
            summary = generate_email_summary(email_data.get('subject', ''), email_data.get('body', ''))
            send_telegram_message(telegram_user_id, format_message(email_data, summary))

            # Update last-email timestamp
            update_user_last_email(telegram_user_id)

        return {'statusCode': 200, 'body': 'Successfully processed emails'}

    except Exception as e:
        logger.error(f"Error processing emails: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}

def extract_user_id_from_email(email_address):
    """Extract Telegram user ID from email like user-123456@csearfarf.dev"""
    try:
        local_part = (email_address or '').split('@')[0]
        parts = local_part.split('-')
        if len(parts) >= 2 and parts[0] == 'user':
            return parts[1]
    except Exception:
        pass
    return None

def get_user_data(telegram_user_id):
    """Fetch user data from DynamoDB"""
    try:
        resp = table.get_item(Key={'chat_id': int(telegram_user_id)})
        return resp.get('Item')
    except Exception as e:
        logger.error(f"Error getting user data: {str(e)}")
        return None

def generate_email_summary(subject, body):
    """Generate email summary using OpenAI API"""
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        prompt = (
            "Provide a concise summary of this email.\n\n"
            f"Subject: {subject}\n\n"
            f"Body: {body[:2000]}\n\n"
            "Summary must be 2–3 sentences highlighting key points."
        )
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        # Use custom OpenAI endpoint
        r = requests.post(
            'https://openai.is238.upou.io/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        
        logger.error(f"OpenAI API error: {r.status_code} {r.text}")
        return f"Summary: {subject}"
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"Summary: {subject}"

def send_telegram_message(user_id, message):
    """Send message to Telegram user with HTML formatting"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {'chat_id': user_id, 'text': message, 'parse_mode': 'HTML'}
        r = requests.post(url, json=data, timeout=10)
        
        if r.status_code != 200:
            logger.error(f"Failed to send message with HTML: {r.status_code} {r.text}")
            
            # Fallback: Try sending without HTML parse mode
            data_plain = {'chat_id': user_id, 'text': message}
            r_plain = requests.post(url, json=data_plain, timeout=10)
            
            if r_plain.status_code == 200:
                logger.info(f"Successfully sent message as plain text to user {user_id}")
            else:
                logger.error(f"Failed to send plain text message: {r_plain.status_code} {r_plain.text}")
        else:
            logger.info(f"Successfully sent HTML message to user {user_id}")
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")

def format_message(email_data, summary):
    """Format message with HTML, escaping user content"""
    # HTML-escape user content to prevent parsing errors
    from_address = html.escape(email_data.get('from', 'Unknown'))
    subject = html.escape(email_data.get('subject', 'No Subject'))
    summary = html.escape(summary)
    date_str = html.escape(email_data.get('date', 'Unknown time'))
    
    return (
        "📧 <b>New Email Summary</b>\n\n"
        f"<b>From:</b> {from_address}\n"
        f"<b>Subject:</b> {subject}\n\n"
        f"<b>Summary:</b>\n{summary}\n\n"
        f"<i>Received: {date_str}</i>"
    )

def update_user_last_email(telegram_user_id):
    """Update user's last email timestamp in DynamoDB"""
    try:
        table.update_item(
            Key={'chat_id': int(telegram_user_id)},
            UpdateExpression='SET last_email_received = :ts',
            ExpressionAttributeValues={':ts': datetime.now().isoformat()}
        )
    except Exception as e:
        logger.error(f"Error updating user timestamp: {str(e)}")
```

### Create requirements.txt

```txt
boto3==1.26.137
requests==2.31.0
```

---

## Step 2: Create IAM Role

### Via AWS Console

1. **Navigate to IAM**
   - Go to IAM > Roles
   - Click "Create role"

2. **Configure Role**
   | Field | Value |
   |-------|-------|
   | Trusted entity | AWS service |
   | Use case | Lambda |

3. **Attach Policies**
   - `AWSLambdaBasicExecutionRole`
   - Create custom policy (see below)

4. **Custom Policy: SevenBot-EmailProcessor-Policy**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::sevenbot-emails-YOUR-ACCOUNT-ID/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:YOUR-ACCOUNT-ID:table/telegram-users"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

5. **Name Role**
   - Role name: `email-processor-lambda-role`
   - Click "Create role"

---

## Step 3: Create Deployment Package

### Deployment Script (deploy.sh)

```bash
#!/bin/bash

# Configuration
FUNCTION_NAME="email-processor"
REGION="us-east-1"
ROLE_ARN="arn:aws:iam::YOUR-ACCOUNT-ID:role/email-processor-lambda-role"

# Clean and prepare
rm -rf package
rm -f email-processor.zip
mkdir package

# Install dependencies
pip install -r requirements.txt -t package/

# Copy Lambda function
cp lambda_function.py package/

# Create deployment package
cd package
zip -r ../email-processor.zip .
cd ..

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://email-processor.zip \
        --region $REGION
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.9 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://email-processor.zip \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION \
        --environment Variables="{
            TELEGRAM_BOT_TOKEN=YOUR-BOT-TOKEN,
            OPENAI_API_KEY=YOUR-OPENAI-KEY
        }"
fi

echo "Deployment complete!"
```

### Windows Deployment Script (deploy.bat)

```batch
@echo off
SET FUNCTION_NAME=email-processor
SET REGION=us-east-1
SET ROLE_ARN=arn:aws:iam::YOUR-ACCOUNT-ID:role/email-processor-lambda-role

:: Clean and prepare
if exist package rmdir /s /q package
if exist email-processor.zip del email-processor.zip
mkdir package

:: Install dependencies
pip install -r requirements.txt -t package

:: Copy Lambda function
copy lambda_function.py package\

:: Create deployment package
cd package
7z a -tzip ..\email-processor.zip *
cd ..

:: Update or create function
aws lambda get-function --function-name %FUNCTION_NAME% --region %REGION% >nul 2>&1
if %errorlevel% equ 0 (
    echo Updating existing function...
    aws lambda update-function-code ^
        --function-name %FUNCTION_NAME% ^
        --zip-file fileb://email-processor.zip ^
        --region %REGION%
) else (
    echo Creating new function...
    aws lambda create-function ^
        --function-name %FUNCTION_NAME% ^
        --runtime python3.9 ^
        --role %ROLE_ARN% ^
        --handler lambda_function.lambda_handler ^
        --zip-file fileb://email-processor.zip ^
        --timeout 30 ^
        --memory-size 256 ^
        --region %REGION%
)

echo Deployment complete!
pause
```

---

## Step 4: Create Lambda Function

### Via AWS Console

1. **Navigate to Lambda**
   - AWS Console > Lambda
   - Click "Create function"

2. **Configure Function**
   | Field | Value |
   |-------|-------|
   | Function name | `email-processor` |
   | Runtime | Python 3.9 |
   | Architecture | x86_64 |
   | Execution role | Use existing: `email-processor-lambda-role` |

3. **Upload Code**
   - Code > Upload from > .zip file
   - Select `email-processor.zip`

### Via Deployment Script

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Step 5: Configure Environment Variables

### Via AWS Console

1. **Navigate to Configuration**
   - Click on your function
   - Go to "Configuration" > "Environment variables"
   - Click "Edit"

2. **Add Variables**
   | Key | Value |
   |-----|-------|
   | `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
   | `OPENAI_API_KEY` | Your OpenAI API key |

3. **Save**

### Via AWS CLI

```bash
aws lambda update-function-configuration \
    --function-name email-processor \
    --environment Variables="{
        TELEGRAM_BOT_TOKEN=YOUR-BOT-TOKEN,
        OPENAI_API_KEY=YOUR-OPENAI-KEY
    }" \
    --region us-east-1
```

---

## Step 6: Configure S3 Trigger

### Via AWS Console

1. **Navigate to S3 Bucket**
   - Go to S3 > `sevenbot-emails-YOUR-ACCOUNT-ID`
   - Click "Properties" tab
   - Scroll to "Event notifications"
   - Click "Create event notification"

2. **Configure Event**
   | Field | Value |
   |-------|-------|
   | Event name | `new-email-trigger` |
   | Prefix | `raw-emails/` |
   | Suffix | `.json` |
   | Event types | ✓ PUT |
   | Destination | Lambda function |
   | Lambda function | `email-processor` |

3. **Save**

### Via AWS CLI

```bash
# Add Lambda permission for S3
aws lambda add-permission \
    --function-name email-processor \
    --statement-id s3-invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::sevenbot-emails-YOUR-ACCOUNT-ID \
    --region us-east-1

# Configure S3 notification
aws s3api put-bucket-notification-configuration \
    --bucket sevenbot-emails-YOUR-ACCOUNT-ID \
    --notification-configuration file://notification-config.json
```

**notification-config.json:**

```json
{
    "LambdaFunctionConfigurations": [
        {
            "Id": "new-email-trigger",
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:YOUR-ACCOUNT-ID:function:email-processor",
            "Events": ["s3:ObjectCreated:Put"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {"Name": "prefix", "Value": "raw-emails/"},
                        {"Name": "suffix", "Value": ".json"}
                    ]
                }
            }
        }
    ]
}
```

---

## Step 7: Test Your Function

### Create Test Event

```json
{
    "Records": [
        {
            "s3": {
                "bucket": {
                    "name": "sevenbot-emails-YOUR-ACCOUNT-ID"
                },
                "object": {
                    "key": "raw-emails/2024/01/01/test-email.json"
                }
            }
        }
    ]
}
```

### Create Test Email in S3

```bash
# Create test email JSON
cat > test-email.json << 'EOF'
{
    "message_id": "<test@example.com>",
    "from": "sender@example.com",
    "to": "user-123456789@csearfarf.dev",
    "subject": "Test Email",
    "date": "Mon, 1 Jan 2024 12:00:00 +0000",
    "timestamp": "2024-01-01T12:00:00",
    "body": "This is a test email body."
}
EOF

# Upload to S3
aws s3 cp test-email.json s3://sevenbot-emails-YOUR-ACCOUNT-ID/raw-emails/2024/01/01/test-email.json
```

### Verify Telegram Notification

Check your Telegram bot to see if you received the summary.

---

## Monitoring and Troubleshooting

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/lambda/email-processor --follow --region us-east-1
```

### Common Issues

#### Issue: "Bad Request: can't parse entities"

**Cause:** HTML formatting error in Telegram message.

**Solution:** Already implemented in code with `html.escape()` and fallback to plain text.

#### Issue: User not found in DynamoDB

**Solution:** Verify user registered via Telegram bot.

```python
# Check DynamoDB manually
import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('telegram-users')
response = table.scan()
print(response['Items'])
```

#### Issue: OpenAI API timeout

**Solution:** Increase Lambda timeout or implement retry logic.

```bash
aws lambda update-function-configuration \
    --function-name email-processor \
    --timeout 60 \
    --region us-east-1
```

---

## Security Best Practices

1. **Use Secrets Manager** for API keys
2. **Rotate Credentials** regularly
3. **Enable Encryption** on S3 and DynamoDB
4. **Limit Permissions** to minimum required
5. **Monitor API Usage** (OpenAI costs)
6. **Validate Input** from S3 events

---

## Cost Estimation

| Resource | Usage | Cost/Month |
|----------|-------|------------|
| Lambda Invocations | ~500/month | $0.00 (free tier) |
| Lambda Duration | ~5s per invocation | $0.01 |
| OpenAI API | ~500 requests | $0.10 |
| DynamoDB Read/Write | ~1,000 ops | $0.00 (free tier) |
| **Total** | | **~$0.11/month** |

---

## Related Documentation

- [Email Fetcher Setup](../email-fetcher/SETUP_GUIDE.md)
- [Telegram Webhook Setup](../telegram-webhook/SETUP_GUIDE.md)
- [DynamoDB Setup](../../dynamodb/SETUP_GUIDE.md)
- [S3 Setup](../../s3/SETUP_GUIDE.md)
- [Fix Documentation](QUICK_FIX.md) - Telegram HTML error fix

---

## Next Steps

1. ✅ Deploy Email Processor Lambda
2. ✅ Configure S3 trigger
3. ✅ Test with sample email
4. → Deploy [Telegram Webhook](../telegram-webhook/SETUP_GUIDE.md)
5. → Set up [monitoring and alerts](../../../ARCHITECTURE.md#monitoring)
