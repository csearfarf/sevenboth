# Email Fetcher Lambda Setup Guide

## Overview

The Email Fetcher Lambda function connects to Gmail via IMAP, retrieves unread emails, and stores them in S3 for processing. It runs on a schedule (typically every 5-15 minutes) using EventBridge.

## Prerequisites

- Gmail account configured - See [Gmail Setup Guide](../../../gmail-setup/SETUP_GUIDE.md)
  - IMAP enabled
  - App password generated
  - 2-Step Verification enabled
- S3 bucket created - See [S3 Setup Guide](../../s3/SETUP_GUIDE.md)
- AWS Lambda execution role with necessary permissions
- AWS CLI installed (for deployment)

## Architecture

```
EventBridge Schedule
         ↓
   Email Fetcher Lambda
         ↓
   Gmail IMAP Connection
         ↓
  Fetch Unread Emails
         ↓
   Store in S3 Bucket
         ↓
  S3 Event Notification
         ↓
   Email Processor Lambda
```

---

## Step 1: Prepare Lambda Function Code

### Create Project Directory

```bash
mkdir email-fetcher
cd email-fetcher
```

### Create lambda_function.py

```python
import imaplib
import email
import boto3
import json
import hashlib
from datetime import datetime
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Read creds and config from ENV
        gmail_username = os.environ['GMAIL_USER']
        gmail_password = os.environ['GMAIL_PASS']
        bucket_name = os.environ['S3_BUCKET_NAME']

        # Connect to Gmail IMAP
        logger.info("Connecting to Gmail IMAP...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_username, gmail_password)
        mail.select('inbox')

        # Search for unread emails
        logger.info("Searching for unread emails...")
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            logger.error("Failed to search emails")
            return {'statusCode': 500, 'body': 'Failed to search emails'}

        message_ids = messages[0].split() if messages and messages[0] else []
        logger.info(f"Found {len(message_ids)} unread emails")

        processed_count = 0

        for msg_id in message_ids:
            try:
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue

                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Extract email metadata
                email_data = {
                    'message_id': email_message.get('Message-ID', ''),
                    'from': email_message.get('From', ''),
                    'to': email_message.get('To', ''),
                    'subject': email_message.get('Subject', ''),
                    'date': email_message.get('Date', ''),
                    'timestamp': datetime.now().isoformat(),
                    'body': extract_email_body(email_message),
                    'raw_email': raw_email.decode('utf-8', errors='ignore')
                }

                # Unique S3 key
                email_hash = hashlib.md5(raw_email).hexdigest()
                now = datetime.now()
                key = f"raw-emails/{now.year}/{now.month:02d}/{now.day:02d}/{email_hash}_{int(now.timestamp())}.json"

                # Store in S3
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=json.dumps(email_data),
                    ContentType='application/json',
                    Metadata={
                        'from': email_data['from'][:100],
                        'subject': email_data['subject'][:100],
                        'processed': 'false'
                    }
                )

                logger.info(f"Stored email: {key}")
                processed_count += 1

                # Mark as read
                mail.store(msg_id, '+FLAGS', '\\Seen')

            except Exception as e:
                logger.error(f"Error processing email {msg_id}: {str(e)}")
                continue

        mail.close()
        mail.logout()

        logger.info(f"Successfully processed {processed_count} emails")
        return {'statusCode': 200, 'body': json.dumps({'processed_count': processed_count})}

    except Exception as e:
        logger.error(f"Lambda execution error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def extract_email_body(email_message):
    """Extract plain text and HTML body from email"""
    body = ""
    html_body = ""
    
    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
            elif content_type == "text/html":
                try:
                    html_body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
    else:
        try:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            body = str(email_message.get_payload())
    
    # Return plain text if available, otherwise HTML
    return body if body else html_body
```

### Create requirements.txt

```txt
boto3==1.26.137
```

**Note:** Standard library modules like `imaplib` and `email` are included in Lambda runtime.

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
   - `AWSLambdaBasicExecutionRole` (for CloudWatch logs)
   - Create custom policy (see below)

4. **Custom Policy**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::sevenbot-emails-YOUR-ACCOUNT-ID/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:YOUR-ACCOUNT-ID:secret:sevenbot/gmail-credentials-*"
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
   - Role name: `email-fetcher-lambda-role`
   - Click "Create role"

---

## Step 3: Create Deployment Package

### For Linux/Mac

```bash
# Create deployment directory
mkdir package
cd package

# Install dependencies
pip install -r ../requirements.txt -t .

# Copy Lambda function
cp ../lambda_function.py .

# Create ZIP file
zip -r ../email-fetcher.zip .

# Go back and add any additional files
cd ..
zip -g email-fetcher.zip lambda_function.py
```

### For Windows (cmd)

```cmd
:: Create deployment directory
mkdir package
cd package

:: Install dependencies
pip install -r ..\requirements.txt -t .

:: Copy Lambda function
copy ..\lambda_function.py .

:: Create ZIP file (requires 7zip or similar)
7z a -tzip ..\email-fetcher.zip *

:: Go back
cd ..
```

### Using Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash

# Configuration
FUNCTION_NAME="email-fetcher"
REGION="us-east-1"
ROLE_ARN="arn:aws:iam::YOUR-ACCOUNT-ID:role/email-fetcher-lambda-role"

# Clean and prepare
rm -rf package
rm -f email-fetcher.zip
mkdir package

# Install dependencies
pip install -r requirements.txt -t package/

# Copy Lambda function
cp lambda_function.py package/

# Create deployment package
cd package
zip -r ../email-fetcher.zip .
cd ..

# Deploy to Lambda
aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.9 \
    --role $ROLE_ARN \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://email-fetcher.zip \
    --timeout 60 \
    --memory-size 256 \
    --region $REGION \
    --environment Variables="{
        GMAIL_USER=group7bot@gmail.com,
        GMAIL_PASS=YOUR-APP-PASSWORD,
        S3_BUCKET_NAME=sevenbot-emails-YOUR-ACCOUNT-ID
    }"

echo "Deployment complete!"
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
   | Function name | `email-fetcher` |
   | Runtime | Python 3.9 |
   | Architecture | x86_64 |
   | Execution role | Use existing role: `email-fetcher-lambda-role` |

3. **Create Function**

### Via AWS CLI

```bash
aws lambda create-function \
    --function-name email-fetcher \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR-ACCOUNT-ID:role/email-fetcher-lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://email-fetcher.zip \
    --timeout 60 \
    --memory-size 256 \
    --region us-east-1
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
   | `GMAIL_USER` | group7bot@gmail.com |
   | `GMAIL_PASS` | your-16-char-app-password |
   | `S3_BUCKET_NAME` | sevenbot-emails-YOUR-ACCOUNT-ID |

3. **Save**

### Via AWS CLI

```bash
aws lambda update-function-configuration \
    --function-name email-fetcher \
    --environment Variables="{
        GMAIL_USER=group7bot@gmail.com,
        GMAIL_PASS=YOUR-APP-PASSWORD,
        S3_BUCKET_NAME=sevenbot-emails-YOUR-ACCOUNT-ID
    }" \
    --region us-east-1
```

**Security Best Practice:** Use AWS Secrets Manager instead of plain environment variables.

---

## Step 6: Configure Lambda Settings

### Timeout

```bash
aws lambda update-function-configuration \
    --function-name email-fetcher \
    --timeout 60 \
    --region us-east-1
```

### Memory

```bash
aws lambda update-function-configuration \
    --function-name email-fetcher \
    --memory-size 256 \
    --region us-east-1
```

### Concurrency (Optional)

```bash
# Limit concurrent executions to prevent overwhelming Gmail
aws lambda put-function-concurrency \
    --function-name email-fetcher \
    --reserved-concurrent-executions 1 \
    --region us-east-1
```

---

## Step 7: Create EventBridge Schedule

📖 **For detailed EventBridge setup, see [EventBridge Setup Guide](../../eventbridge/SETUP_GUIDE.md)**

### Quick Setup via AWS CLI

```bash
# Create rule
aws events put-rule \
    --name email-fetcher-schedule \
    --description "Fetch emails every 5 minutes" \
    --schedule-expression "rate(5 minutes)" \
    --region us-east-1

# Add Lambda permission
aws lambda add-permission \
    --function-name email-fetcher \
    --statement-id eventbridge-invoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:YOUR-ACCOUNT-ID:rule/email-fetcher-schedule \
    --region us-east-1

# Add target
aws events put-targets \
    --rule email-fetcher-schedule \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR-ACCOUNT-ID:function:email-fetcher" \
    --region us-east-1
```

**For more options including:**
- Different schedule patterns (cron expressions)
- Dead Letter Queue configuration
- Retry policies
- Monitoring and troubleshooting

See the complete [EventBridge Setup Guide](../../eventbridge/SETUP_GUIDE.md)

---

## Step 8: Test Your Function

### Test via AWS Console

1. **Create Test Event**
   - Go to "Test" tab
   - Event name: `test-event`
   - Event JSON: `{}`
   - Click "Test"

2. **Check Results**
   - View execution results
   - Check CloudWatch logs
   - Verify S3 bucket for new emails

### Test via AWS CLI

```bash
aws lambda invoke \
    --function-name email-fetcher \
    --payload '{}' \
    --region us-east-1 \
    response.json

cat response.json
```

### Verify S3 Storage

```bash
aws s3 ls s3://sevenbot-emails-YOUR-ACCOUNT-ID/raw-emails/ --recursive
```

---

## Monitoring and Troubleshooting

### CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/email-fetcher --follow --region us-east-1
```

### Common Issues

#### Issue: "Authentication failed"

**Solution:** Verify Gmail app password and 2FA settings.

```python
# Test IMAP connection locally
import imaplib
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('group7bot@gmail.com', 'your-app-password')
print("Success!")
```

#### Issue: "AccessDeniedException" (S3)

**Solution:** Check IAM role permissions.

```bash
aws iam get-role-policy \
    --role-name email-fetcher-lambda-role \
    --policy-name SevenBot-S3-Policy
```

#### Issue: No emails being fetched

**Solution:**
1. Check Gmail inbox for unread emails
2. Verify IMAP is enabled
3. Check Lambda execution logs
4. Test function manually

---

## Best Practices

1. **Use Secrets Manager**: Don't store passwords in environment variables
2. **Implement Retry Logic**: Handle transient Gmail errors
3. **Monitor Costs**: Watch Lambda invocations and S3 storage
4. **Set Concurrency Limits**: Prevent overwhelming Gmail
5. **Enable DLQ**: Use Dead Letter Queue for failed invocations
6. **Regular Testing**: Test function monthly to ensure Gmail access works

---

## Cost Estimation

| Resource | Usage | Cost/Month |
|----------|-------|------------|
| Lambda Invocations | 8,640 (every 5 min) | $0.00 (free tier) |
| Lambda Duration | ~10s per invocation | $0.02 |
| S3 Storage | 1 GB | $0.02 |
| S3 PUT Requests | ~8,640 | $0.04 |
| **Total** | | **~$0.08/month** |

---

## Related Documentation

- [Gmail Setup Guide](../../../gmail-setup/SETUP_GUIDE.md) - Configure Gmail IMAP
- [EventBridge Setup Guide](../../eventbridge/SETUP_GUIDE.md) - Detailed scheduling options
- [Email Processor Setup](../email-processor/SETUP_GUIDE.md) - Process fetched emails
- [S3 Setup Guide](../../s3/SETUP_GUIDE.md) - Configure email storage
- [Cloudflare Email Routing](../../../cloudflare-setup/SETUP_GUIDE.md) - Email forwarding
- [Architecture Overview](../../../ARCHITECTURE.md)

---

## Next Steps

1. ✅ Deploy Email Fetcher Lambda
2. ✅ Configure [Gmail IMAP](../../../gmail-setup/SETUP_GUIDE.md)
3. ✅ Set up [EventBridge schedule](../../eventbridge/SETUP_GUIDE.md)
4. → Deploy [Email Processor Lambda](../email-processor/SETUP_GUIDE.md)
5. → Configure [S3 event notifications](../../s3/SETUP_GUIDE.md)
6. → Test end-to-end email flow
