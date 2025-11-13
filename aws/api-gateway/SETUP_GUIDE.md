# API Gateway Setup Guide

## Overview

This guide provides step-by-step instructions for setting up AWS API Gateway to handle Telegram webhook requests and any future HTTP endpoints for SevenBot.

## Prerequisites

- AWS Account with API Gateway permissions
- Telegram Bot Token (from BotFather)
- Lambda functions deployed (telegram-webhook)
- Basic understanding of REST APIs

## API Gateway Components

1. **REST API** - Main API for webhook handling
2. **Resources** - URL paths (/webhook, /health)
3. **Methods** - HTTP methods (POST, GET)
4. **Integrations** - Lambda function connections
5. **Deployment Stages** - Production, development environments

---

## Step 1: Create REST API

### Via AWS Console

1. **Navigate to API Gateway**
   - Open the [AWS Console](https://console.aws.amazon.com/)
   - Search for "API Gateway"
   - Click on the service

2. **Create API**
   - Click "Create API"
   - Choose "REST API" (not Private or HTTP API)
   - Click "Build"

3. **Configure API**
   | Field | Value |
   |-------|-------|
   | Choose protocol | REST |
   | Create new API | New API |
   | API name | `sevenbot-api` |
   | Description | SevenBot Telegram Webhook API |
   | Endpoint Type | Regional |

4. **Create API**
   - Click "Create API"

### Via AWS CLI

```bash
aws apigateway create-rest-api \
    --name sevenbot-api \
    --description "SevenBot Telegram Webhook API" \
    --endpoint-configuration types=REGIONAL \
    --region us-east-1
```

---

## Step 2: Create Webhook Resource

### Via AWS Console

1. **Create Resource**
   - Click "Actions" > "Create Resource"
   - Configure resource:

   | Field | Value |
   |-------|-------|
   | Resource Name | webhook |
   | Resource Path | /webhook |
   | Enable CORS | ✓ (checked) |

2. **Create Resource**
   - Click "Create Resource"

### Via AWS CLI

```bash
# Get API ID
API_ID=$(aws apigateway get-rest-apis --query "items[?name=='sevenbot-api'].id" --output text)

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/'].id" --output text)

# Create webhook resource
aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part webhook
```

---

## Step 3: Create POST Method for Webhook

### Via AWS Console

1. **Create Method**
   - Select the `/webhook` resource
   - Click "Actions" > "Create Method"
   - Choose "POST" from dropdown
   - Click the checkmark

2. **Set Up Integration**
   | Field | Value |
   |-------|-------|
   | Integration type | Lambda Function |
   | Use Lambda Proxy integration | ✓ (checked) |
   | Lambda Region | us-east-1 |
   | Lambda Function | telegram-webhook |

3. **Save**
   - Click "Save"
   - Click "OK" to give API Gateway permission to invoke Lambda

### Via AWS CLI

```bash
# Get webhook resource ID
WEBHOOK_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/webhook'].id" --output text)

# Create POST method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $WEBHOOK_ID \
    --http-method POST \
    --authorization-type NONE

# Get Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function --function-name telegram-webhook --query 'Configuration.FunctionArn' --output text)

# Create integration
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $WEBHOOK_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations"

# Grant permission to API Gateway
aws lambda add-permission \
    --function-name telegram-webhook \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:YOUR-ACCOUNT-ID:$API_ID/*/*"
```

---

## Step 4: Create Health Check Endpoint (Optional)

### Via AWS Console

1. **Create Resource**
   - Click "Actions" > "Create Resource"
   - Resource Name: `health`
   - Resource Path: `/health`
   - Click "Create Resource"

2. **Create GET Method**
   - Select `/health` resource
   - Click "Actions" > "Create Method"
   - Choose "GET"
   - Integration type: "Mock"
   - Click "Save"

3. **Configure Response**
   - Click "Integration Response"
   - Expand the 200 response
   - Add mapping template:
     - Content-Type: `application/json`
     - Template:
     ```json
     {
         "status": "healthy",
         "service": "sevenbot-api",
         "timestamp": "$context.requestTime"
     }
     ```

### Test Health Endpoint

```bash
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health
```

---

## Step 5: Enable CORS (if needed)

### Via AWS Console

1. **Select Resource**
   - Click on `/webhook` resource

2. **Enable CORS**
   - Click "Actions" > "Enable CORS"
   - Keep default settings or customize:
     - Access-Control-Allow-Origin: `*` (or specific domain)
     - Access-Control-Allow-Methods: POST, OPTIONS
   - Click "Enable CORS and replace existing CORS headers"

---

## Step 6: Deploy API

### Via AWS Console

1. **Create Deployment**
   - Click "Actions" > "Deploy API"
   - Deployment stage: [New Stage]
   - Stage name: `prod`
   - Stage description: Production environment
   - Click "Deploy"

2. **Note Your API URL**
   - After deployment, you'll see the Invoke URL
   - Format: `https://[api-id].execute-api.[region].amazonaws.com/prod`
   - Example: `https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod`

### Via AWS CLI

```bash
# Create deployment
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --description "Production deployment"

# Get invoke URL
echo "Invoke URL: https://$API_ID.execute-api.us-east-1.amazonaws.com/prod"
```

---

## Step 7: Configure Telegram Webhook

Now register your API Gateway URL with Telegram:

### Set Webhook

```bash
# Replace with your values
BOT_TOKEN="your-telegram-bot-token"
API_URL="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/webhook"

# Set webhook
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"${API_URL}\"}"
```

### Verify Webhook

```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
```

Expected response:
```json
{
    "ok": true,
    "result": {
        "url": "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/webhook",
        "has_custom_certificate": false,
        "pending_update_count": 0,
        "max_connections": 40
    }
}
```

---

## Step 8: Configure API Gateway Settings

### Throttling Settings

1. **Navigate to Stages**
   - Click "Stages" > "prod"
   - Go to "Settings" tab

2. **Configure Throttling**
   | Setting | Recommended Value |
   |---------|-------------------|
   | Rate | 1000 requests per second |
   | Burst | 2000 requests |

### Enable Logging

1. **Create CloudWatch Role**
   - IAM > Roles > Create role
   - Trusted entity: API Gateway
   - Permissions: `AmazonAPIGatewayPushToCloudWatchLogs`
   - Role name: `api-gateway-cloudwatch-role`

2. **Configure API Gateway Logging**
   - API Gateway > Settings (in left sidebar)
   - CloudWatch log role ARN: (paste role ARN)
   - Save

3. **Enable Stage Logging**
   - Stages > prod > Logs/Tracing tab
   - Enable CloudWatch Logs
   - Log level: INFO (or ERROR for production)
   - Log full requests/responses: ✓ (for debugging)

---

## Step 9: Set Up Custom Domain (Optional)

### Prerequisites

- Domain registered (e.g., csearfarf.dev)
- ACM certificate in us-east-1 region

### Via AWS Console

1. **Request Certificate (if needed)**
   - Navigate to AWS Certificate Manager (ACM)
   - Request a certificate for `api.csearfarf.dev`
   - Validate via DNS or email

2. **Create Custom Domain**
   - API Gateway > Custom domain names
   - Click "Create"
   - Domain name: `api.csearfarf.dev`
   - ACM certificate: Select your certificate
   - Click "Create domain name"

3. **Add API Mapping**
   - Click "API mappings" tab
   - Click "Configure API mappings"
   - API: `sevenbot-api`
   - Stage: `prod`
   - Path: (empty)
   - Click "Save"

4. **Update DNS**
   - Note the "API Gateway domain name" (e.g., `d-abc123.execute-api.us-east-1.amazonaws.com`)
   - Create CNAME record in your DNS:
     - Name: `api`
     - Type: `CNAME`
     - Value: (API Gateway domain name)

5. **Update Telegram Webhook**
   ```bash
   curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
       -H "Content-Type: application/json" \
       -d '{"url": "https://api.csearfarf.dev/webhook"}'
   ```

---

## Step 10: Test Your Setup

### Test Webhook Endpoint

```bash
# Test with curl
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/webhook \
    -H "Content-Type: application/json" \
    -d '{
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "first_name": "Test"
            },
            "chat": {
                "id": 123456789,
                "type": "private"
            },
            "date": 1234567890,
            "text": "/start"
        }
    }'
```

### Test with Telegram

1. Open your Telegram bot
2. Send `/start` command
3. Check CloudWatch logs for Lambda invocation
4. Verify bot responds

---

## Monitoring and Troubleshooting

### CloudWatch Metrics

Key metrics to monitor:
- **4XXError**: Client errors
- **5XXError**: Server errors
- **Count**: Total API calls
- **Latency**: Response time
- **IntegrationLatency**: Lambda execution time

### Common Issues

#### Issue: 403 Forbidden

**Solution:** Check API key requirements and Lambda permissions.

```bash
# Verify Lambda permission
aws lambda get-policy --function-name telegram-webhook
```

#### Issue: 502 Bad Gateway

**Solution:** Lambda function error or timeout.

1. Check CloudWatch logs
2. Verify Lambda function works independently
3. Check Lambda timeout settings

#### Issue: 504 Gateway Timeout

**Solution:** Lambda execution exceeds API Gateway timeout (29 seconds).

1. Optimize Lambda function
2. Implement asynchronous processing
3. Use Step Functions for long-running tasks

#### Issue: Webhook Not Receiving Updates

**Solution:**
1. Verify webhook URL is correct
2. Check API Gateway deployment
3. Test endpoint with curl
4. Check Lambda permissions

```bash
# Get webhook info
curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"

# Delete and reset webhook
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook"
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
    -d '{"url": "your-new-url"}'
```

---

## Security Best Practices

1. **Use API Keys**: For non-Telegram endpoints
2. **Implement Rate Limiting**: Prevent abuse
3. **Enable WAF**: Use AWS WAF for DDoS protection
4. **Validate Input**: Always validate webhook payloads
5. **Use HTTPS**: Never use HTTP for webhooks
6. **Rotate Secrets**: Regularly rotate bot tokens
7. **Monitor Access**: Set up CloudWatch alarms

### Example: Validate Telegram Secret Token

Telegram supports secret tokens for webhook validation:

```bash
# Set webhook with secret token
curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
    -H "Content-Type: application/json" \
    -d '{
        "url": "https://api.csearfarf.dev/webhook",
        "secret_token": "your-secret-token-here"
    }'
```

Update Lambda to validate:

```python
import os

def lambda_handler(event, context):
    # Get secret token from environment
    expected_token = os.environ.get('TELEGRAM_SECRET_TOKEN')
    
    # Get token from header
    received_token = event['headers'].get('X-Telegram-Bot-Api-Secret-Token')
    
    # Validate
    if received_token != expected_token:
        return {
            'statusCode': 403,
            'body': 'Forbidden'
        }
    
    # Process webhook...
```

---

## Cost Optimization

### API Gateway Pricing

- **REST API**: $3.50 per million requests
- **Data Transfer**: $0.09 per GB
- **Cache**: Optional, $0.02/hour per GB

### Tips

1. Use caching for repeated requests
2. Implement efficient Lambda functions
3. Use CloudFront for static content
4. Monitor and set billing alarms

---

## Related Documentation

- [DynamoDB Setup Guide](../dynamodb/SETUP_GUIDE.md)
- [S3 Setup Guide](../s3/SETUP_GUIDE.md)
- [Lambda Functions Setup](../lambda-functions/)
- [Architecture Overview](../../ARCHITECTURE.md)

---

## Next Steps

After setting up API Gateway:

1. ✅ Verify API is deployed
2. ✅ Test webhook endpoint
3. ✅ Configure Telegram webhook
4. → Deploy remaining [Lambda functions](../lambda-functions/)
5. → Set up [monitoring and alerts](../../ARCHITECTURE.md#monitoring)

---

## Additional Resources

- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [API Gateway Best Practices](https://docs.aws.amazon.com/apigateway/latest/developerguide/best-practices.html)
