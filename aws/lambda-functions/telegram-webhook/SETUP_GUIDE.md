# Telegram Webhook Lambda Setup Guide

## Overview

The Telegram Webhook Lambda function handles all user interactions with the Telegram bot. It processes commands like `/start`, `/register`, `/status`, and manages user data in DynamoDB. This function is triggered by API Gateway when Telegram sends webhook updates.

## Prerequisites

- Telegram bot created via BotFather
- Bot token obtained
- DynamoDB table (`telegram-users`) created
- API Gateway configured
- AWS Lambda execution role with necessary permissions

## Architecture

```
Telegram Bot API
         ↓
   API Gateway
         ↓
Telegram Webhook Lambda
         ↓
   DynamoDB Operations
   (Create, Read, Update users)
         ↓
   Send Response to Telegram
```

---

## Step 1: Create Telegram Bot

### Via BotFather

1. **Start Chat with BotFather**
   - Open Telegram
   - Search for `@BotFather`
   - Send `/start`

2. **Create New Bot**
   - Send `/newbot`
   - Enter bot name: `SevenBot Email Summarizer`
   - Enter username: `sevenbot_emailsum_bot` (must end with "bot")

3. **Save Bot Token**
   - BotFather sends you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - **Keep this secret!**
   - Store in AWS Secrets Manager or Parameter Store

4. **Configure Bot (Optional)**
   ```
   /setdescription - Email summary bot
   /setabouttext - Get AI-powered summaries of emails
   /setuserpic - Upload bot profile picture
   /setcommands - Set command list:
   ```

   Command list:
   ```
   start - Welcome message and commands
   register - Create your unique email address
   status - Check your email address and status
   deactivate - Disable email forwarding
   help - Show help
   ```

---

## Step 2: Prepare Lambda Function Code

### Create Project Directory

```bash
mkdir telegram-webhook
cd telegram-webhook
```

### Create lambda_function.py

```python
import os
import json
import base64
import logging
import random
import string
from datetime import datetime

import boto3
import requests

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS resources
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('telegram-users')

# Environment variables
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

def lambda_handler(event, context):
    """Handle Telegram webhook requests"""
    try:
        logger.info(f"RAW EVENT: {json.dumps(event)[:2000]}")

        # Parse body
        body_str = event.get('body', '')
        if event.get('isBase64Encoded'):
            try:
                body_str = base64.b64decode(body_str).decode('utf-8', errors='ignore')
            except Exception as e:
                logger.error(f"Base64 decode failed: {e}")
                body_str = ''

        logger.info(f"BODY STRING: {body_str[:1000]}")

        try:
            body = json.loads(body_str) if body_str else {}
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            body = {}

        logger.info(f"PARSED BODY: {json.dumps(body)[:1000]}")

        # Extract message
        message = body.get('message')
        if not message:
            logger.info("No 'message' in update; returning 200.")
            return {'statusCode': 200, 'body': 'OK'}

        chat_id = str(message.get('chat', {}).get('id'))
        text = (message.get('text') or '').strip()

        logger.info(f"Received message from {chat_id}: {text}")

        # Handle commands
        if text.startswith('/'):
            response_text = handle_command(text, chat_id)
        else:
            response_text = "Use /start to see available commands."

        # Send response
        if response_text and chat_id:
            send_response(chat_id, response_text)

        return {'statusCode': 200, 'body': 'OK'}

    except Exception as e:
        logger.exception(f"Webhook error: {e}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}


def handle_command(command, chat_id):
    """Route commands to appropriate handlers"""
    cmd = command.lower().strip()
    
    if cmd == '/start':
        return handle_start_command(chat_id)
    elif cmd == '/register':
        return handle_register_command(chat_id)
    elif cmd == '/status':
        return handle_status_command(chat_id)
    elif cmd == '/deactivate':
        return handle_deactivate_command(chat_id)
    elif cmd == '/help':
        return handle_help_command()
    else:
        return "Unknown command. Use /help to see available commands."


def handle_start_command(chat_id):
    """Welcome message"""
    return (
        "Welcome to SevenBot Email Summarizer! 📧\n\n"
        "I help you manage email overload by:\n"
        "• Creating unique email addresses\n"
        "• Summarizing emails with AI\n"
        "• Delivering summaries to Telegram\n\n"
        "Commands:\n"
        "/register – Create your unique email address\n"
        "/status – Check your email address and status\n"
        "/deactivate – Disable email forwarding\n"
        "/help – Show help\n\n"
        "Quick Start:\n"
        "1. Use /register to get your email\n"
        "2. Give that address to any service\n"
        "3. Receive AI summaries here!"
    )


def handle_register_command(chat_id):
    """Register new user and generate email address"""
    try:
        # Check if user already exists
        resp = table.get_item(Key={'chat_id': int(chat_id)})
        if 'Item' in resp and resp['Item'].get('status') == 'active':
            return f"✅ You already have an active email:\n\n{resp['Item']['email_address']}"

        # Generate unique email address
        email_address = generate_email_address(chat_id)
        
        # Store in DynamoDB
        table.put_item(Item={
            'chat_id': int(chat_id),
            'email_address': email_address,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_email_received': None,
            'email_count': 0
        })

        return (
            "✅ Email address created successfully!\n\n"
            f"📧 Your Email:\n{email_address}\n\n"
            "Use this address anywhere you want email summaries.\n\n"
            "💡 Tips:\n"
            "• Give it to newsletters\n"
            "• Use for online services\n"
            "• Share with teams\n\n"
            "Use /status to check your details."
        )

    except Exception as e:
        logger.error(f"/register error for {chat_id}: {e}")
        return "❌ Error creating email. Please try again later."


def handle_status_command(chat_id):
    """Show user status and email details"""
    try:
        resp = table.get_item(Key={'chat_id': int(chat_id)})
        if 'Item' not in resp:
            return "❌ You don't have an email yet. Use /register to create one."

        user = resp['Item']
        created = (user.get('created_at') or 'Unknown')[:19]
        last = user.get('last_email_received') or 'Never'
        if last and last != 'Never':
            last = last[:19]
        
        email_count = user.get('email_count', 0)
        status_emoji = "✅" if user['status'] == 'active' else "⏸️"

        return (
            f"{status_emoji} Your Email Status\n\n"
            f"📧 Email: {user['email_address']}\n"
            f"📊 Status: {user['status'].title()}\n"
            f"📅 Created: {created}\n"
            f"📨 Emails Processed: {email_count}\n"
            f"🕐 Last Email: {last}"
        )

    except Exception as e:
        logger.error(f"/status error for {chat_id}: {e}")
        return "❌ Error retrieving status. Please try again later."


def handle_deactivate_command(chat_id):
    """Deactivate user's email address"""
    try:
        resp = table.get_item(Key={'chat_id': int(chat_id)})
        if 'Item' not in resp:
            return "❌ No email to deactivate. Use /register to create one."

        table.update_item(
            Key={'chat_id': int(chat_id)},
            UpdateExpression='SET #s = :inactive',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':inactive': 'inactive'}
        )
        
        return (
            "⏸️ Email address deactivated.\n\n"
            "You won't receive summaries anymore.\n"
            "Use /register to reactivate."
        )

    except Exception as e:
        logger.error(f"/deactivate error for {chat_id}: {e}")
        return "❌ Error deactivating email. Please try again later."


def handle_help_command():
    """Show help message"""
    return (
        "📚 Available Commands:\n\n"
        "/start - Welcome message\n"
        "/register - Create email address\n"
        "/status - Check your status\n"
        "/deactivate - Disable forwarding\n"
        "/help - Show this help\n\n"
        "Need support? Contact @your-username"
    )


def generate_email_address(telegram_user_id):
    """Generate unique email address for user"""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"user-{telegram_user_id}-{suffix}@csearfarf.dev"


def send_response(chat_id, text):
    """Send message to Telegram user"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        r = requests.post(url, json=payload, timeout=10)
        logger.info(f"sendMessage -> {r.status_code} {r.text}")
        
        if r.status_code != 200:
            logger.error(f"Telegram send failed: {r.status_code} {r.text}")
            
    except Exception as e:
        logger.exception(f"send_response error: {e}")
```

### Create requirements.txt

```txt
boto3==1.26.137
requests==2.31.0
```

---

## Step 3: Create IAM Role

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
   - Create custom policy

4. **Custom Policy**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
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
   - Role name: `telegram-webhook-lambda-role`

---

## Step 4: Deploy Lambda Function

### Deployment Script (deploy.sh)

```bash
#!/bin/bash

FUNCTION_NAME="telegram-webhook"
REGION="us-east-1"
ROLE_ARN="arn:aws:iam::YOUR-ACCOUNT-ID:role/telegram-webhook-lambda-role"

# Clean and prepare
rm -rf package
rm -f telegram-webhook.zip
mkdir package

# Install dependencies
pip install -r requirements.txt -t package/

# Copy Lambda function
cp lambda_function.py package/

# Create deployment package
cd package
zip -r ../telegram-webhook.zip .
cd ..

# Deploy
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://telegram-webhook.zip \
        --region $REGION
else
    echo "Creating..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.9 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://telegram-webhook.zip \
        --timeout 10 \
        --memory-size 128 \
        --region $REGION \
        --environment Variables="{TELEGRAM_BOT_TOKEN=YOUR-BOT-TOKEN}"
fi

echo "Deployment complete!"
```

### Via AWS CLI

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Step 5: Configure Environment Variables

```bash
aws lambda update-function-configuration \
    --function-name telegram-webhook \
    --environment Variables="{TELEGRAM_BOT_TOKEN=YOUR-BOT-TOKEN}" \
    --region us-east-1
```

---

## Step 6: Connect to API Gateway

See [API Gateway Setup Guide](../../api-gateway/SETUP_GUIDE.md) for detailed instructions.

### Quick Setup

```bash
# Get API Gateway URL
API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/webhook"

# Set Telegram webhook
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"${API_URL}\"}"

# Verify webhook
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

---

## Step 7: Test Your Bot

### Test via Telegram

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Expected response: Welcome message
5. Send `/register`
6. Expected response: Your unique email address

### Test via AWS Console

Create test event:

```json
{
    "body": "{\"message\":{\"message_id\":1,\"from\":{\"id\":123456789,\"first_name\":\"Test\"},\"chat\":{\"id\":123456789,\"type\":\"private\"},\"date\":1234567890,\"text\":\"/start\"}}",
    "isBase64Encoded": false
}
```

---

## Monitoring and Troubleshooting

### CloudWatch Logs

```bash
aws logs tail /aws/lambda/telegram-webhook --follow --region us-east-1
```

### Common Issues

#### Issue: Bot not responding

**Solutions:**
1. Check webhook is set correctly
2. Verify API Gateway is deployed
3. Check Lambda function logs
4. Test Lambda function manually

#### Issue: DynamoDB errors

**Solutions:**
1. Verify table exists
2. Check IAM permissions
3. Verify table key schema matches code

#### Issue: "User already exists" error

**Expected behavior** - user can only register once.

---

## Security Best Practices

1. **Use Secrets Manager** for bot token
2. **Validate Webhook** with secret token
3. **Rate Limiting** in API Gateway
4. **Input Validation** for all commands
5. **Error Handling** for all operations

---

## Cost Estimation

| Resource | Usage | Cost/Month |
|----------|-------|------------|
| Lambda Invocations | ~1,000 | $0.00 (free tier) |
| Lambda Duration | ~1s per invocation | $0.00 |
| API Gateway | ~1,000 requests | $0.00 (free tier) |
| DynamoDB | ~2,000 ops | $0.00 (free tier) |
| **Total** | | **$0.00/month** |

---

## Related Documentation

- [API Gateway Setup](../../api-gateway/SETUP_GUIDE.md)
- [DynamoDB Setup](../../dynamodb/SETUP_GUIDE.md)
- [Email Processor Setup](../email-processor/SETUP_GUIDE.md)
- [Architecture Overview](../../../ARCHITECTURE.md)

---

## Next Steps

1. ✅ Deploy Telegram Webhook Lambda
2. ✅ Connect to API Gateway
3. ✅ Test bot commands
4. → Complete [end-to-end testing](../../../README.md#testing)
5. → Set up [monitoring](../../../ARCHITECTURE.md#monitoring)
