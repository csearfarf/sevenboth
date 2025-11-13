# Amazon EventBridge Setup Guide

## Overview

Amazon EventBridge (formerly CloudWatch Events) is used to schedule the Email Fetcher Lambda function to run automatically at regular intervals. This guide covers setting up rules, schedules, and targets for automated email polling.

## Prerequisites

- AWS Account with EventBridge permissions
- Email Fetcher Lambda function deployed
- AWS CLI installed (optional)
- Basic understanding of cron expressions

## What EventBridge Does

```
EventBridge Rule (Schedule)
         ↓
  Triggers every 5 minutes
         ↓
   Email Fetcher Lambda
         ↓
  Fetches emails from Gmail
         ↓
   Stores in S3
```

---

## Step 1: Understanding Schedule Expressions

EventBridge supports two types of schedule expressions:

### Rate Expressions

Simple interval-based schedules:

```
rate(5 minutes)    # Every 5 minutes
rate(1 hour)       # Every hour
rate(1 day)        # Every day
```

### Cron Expressions

More precise scheduling:

```
cron(0/5 * * * ? *)     # Every 5 minutes
cron(0 * * * ? *)       # Every hour at minute 0
cron(0 9 * * ? *)       # Every day at 9:00 AM UTC
cron(0 */2 * * ? *)     # Every 2 hours
```

**Format:** `cron(Minutes Hours Day-of-month Month Day-of-week Year)`

**Note:** EventBridge uses UTC time zone.

### Recommended Schedule for Email Fetching

| Frequency | Expression | Use Case |
|-----------|------------|----------|
| Every 5 minutes | `rate(5 minutes)` | High-priority emails |
| Every 10 minutes | `rate(10 minutes)` | Standard usage |
| Every 15 minutes | `rate(15 minutes)` | Low-priority/cost savings |
| Every hour | `rate(1 hour)` | Minimal usage |

**Recommendation:** Start with `rate(5 minutes)` for testing, adjust based on needs.

---

## Step 2: Create EventBridge Rule via AWS Console

### Navigate to EventBridge

1. **Open AWS Console**
   - Go to [AWS Console](https://console.aws.amazon.com/)
   - Search for "EventBridge" or "Amazon EventBridge"
   - Click on the service

2. **Go to Rules**
   - In the left sidebar, click "Rules"
   - Ensure you're in the correct region (e.g., us-east-1)

### Create New Rule

1. **Click "Create rule"**

2. **Define Rule Detail**
   | Field | Value |
   |-------|-------|
   | Name | `email-fetcher-schedule` |
   | Description | Triggers Email Fetcher Lambda every 5 minutes |
   | Event bus | `default` |
   | Rule type | `Schedule` |
   | State | `Enabled` |

3. **Click "Next"**

### Define Schedule Pattern

1. **Schedule Pattern Options**
   - Choose: **A schedule that runs at a regular rate, such as every 10 minutes**

2. **Rate Expression**
   - Value: `5`
   - Unit: `Minutes`
   - Or enter manually: `rate(5 minutes)`

   **Alternative: Cron Expression**
   - Choose: **A fine-grained schedule that runs at a specific time**
   - Cron expression: `cron(0/5 * * * ? *)`

3. **Click "Next"**

### Select Target

1. **Target Types**
   - Choose: **AWS service**

2. **Select a target**
   - Select: `Lambda function`
   - Function: `email-fetcher`

3. **Additional Settings** (Optional)
   - Retry policy: 2 retries (default)
   - Maximum age of event: 1 hour
   - Dead-letter queue: (configure if needed)

4. **Click "Next"**

### Configure Tags (Optional)

Add tags for organization:
- Key: `Environment`, Value: `Production`
- Key: `Project`, Value: `SevenBot`
- Key: `Component`, Value: `EmailFetcher`

### Review and Create

1. Review all settings
2. Click "Create rule"
3. Wait for confirmation: "Rule created successfully"

---

## Step 3: Create EventBridge Rule via AWS CLI

### Single Command Setup

```bash
# Set variables
FUNCTION_NAME="email-fetcher"
RULE_NAME="email-fetcher-schedule"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create EventBridge rule
aws events put-rule \
    --name $RULE_NAME \
    --description "Fetch emails every 5 minutes" \
    --schedule-expression "rate(5 minutes)" \
    --state ENABLED \
    --region $REGION

echo "✅ EventBridge rule created: $RULE_NAME"
```

### Add Lambda Permission

EventBridge needs permission to invoke your Lambda function:

```bash
# Add permission to Lambda
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id eventbridge-invoke-permission \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/${RULE_NAME}" \
    --region $REGION

echo "✅ Lambda permission added"
```

### Add Lambda as Target

```bash
# Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Configuration.FunctionArn' \
    --output text)

# Add Lambda as target to EventBridge rule
aws events put-targets \
    --rule $RULE_NAME \
    --targets "Id"="1","Arn"="$LAMBDA_ARN" \
    --region $REGION

echo "✅ Lambda target added to EventBridge rule"
```

### Verify Setup

```bash
# List rules
aws events list-rules --region $REGION

# Describe specific rule
aws events describe-rule --name $RULE_NAME --region $REGION

# List targets for rule
aws events list-targets-by-rule --rule $RULE_NAME --region $REGION
```

---

## Step 4: Complete Setup Script

Create `setup-eventbridge.sh`:

```bash
#!/bin/bash

# Configuration
FUNCTION_NAME="email-fetcher"
RULE_NAME="email-fetcher-schedule"
SCHEDULE="rate(5 minutes)"  # Change as needed
REGION="us-east-1"

echo "Setting up EventBridge for $FUNCTION_NAME..."

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $ACCOUNT_ID"

# Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Configuration.FunctionArn' \
    --output text 2>/dev/null)

if [ -z "$LAMBDA_ARN" ]; then
    echo "❌ Error: Lambda function '$FUNCTION_NAME' not found"
    exit 1
fi

echo "Lambda ARN: $LAMBDA_ARN"

# Check if rule exists
RULE_EXISTS=$(aws events describe-rule \
    --name $RULE_NAME \
    --region $REGION \
    2>/dev/null)

if [ -n "$RULE_EXISTS" ]; then
    echo "Rule already exists. Updating..."
    aws events put-rule \
        --name $RULE_NAME \
        --description "Fetch emails at regular intervals" \
        --schedule-expression "$SCHEDULE" \
        --state ENABLED \
        --region $REGION
else
    echo "Creating new rule..."
    aws events put-rule \
        --name $RULE_NAME \
        --description "Fetch emails at regular intervals" \
        --schedule-expression "$SCHEDULE" \
        --state ENABLED \
        --region $REGION
fi

# Add Lambda permission (ignore if already exists)
echo "Adding Lambda permission..."
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id eventbridge-invoke-permission \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:${REGION}:${ACCOUNT_ID}:rule/${RULE_NAME}" \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Add target
echo "Adding Lambda as target..."
aws events put-targets \
    --rule $RULE_NAME \
    --targets "Id"="1","Arn"="$LAMBDA_ARN" \
    --region $REGION

echo ""
echo "✅ EventBridge setup complete!"
echo "Rule: $RULE_NAME"
echo "Schedule: $SCHEDULE"
echo "Target: $FUNCTION_NAME"
echo ""
echo "To verify: aws events describe-rule --name $RULE_NAME --region $REGION"
```

**Make executable and run:**

```bash
chmod +x setup-eventbridge.sh
./setup-eventbridge.sh
```

---

## Step 5: Configure Advanced Options

### Enable Rule Temporarily

```bash
# Disable rule
aws events disable-rule --name email-fetcher-schedule --region us-east-1

# Enable rule
aws events enable-rule --name email-fetcher-schedule --region us-east-1
```

### Update Schedule

```bash
# Change to every 10 minutes
aws events put-rule \
    --name email-fetcher-schedule \
    --schedule-expression "rate(10 minutes)" \
    --region us-east-1

# Or use cron for specific times
aws events put-rule \
    --name email-fetcher-schedule \
    --schedule-expression "cron(0 9-17 * * MON-FRI *)" \
    --region us-east-1
# (Runs every hour from 9 AM to 5 PM, Monday-Friday)
```

### Add Dead Letter Queue (DLQ)

For handling failed invocations:

```bash
# Create SQS queue for DLQ
aws sqs create-queue --queue-name email-fetcher-dlq --region us-east-1

# Get queue ARN
DLQ_ARN=$(aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/${ACCOUNT_ID}/email-fetcher-dlq \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

# Update target with DLQ
aws events put-targets \
    --rule email-fetcher-schedule \
    --targets "Id"="1","Arn"="$LAMBDA_ARN","DeadLetterConfig"={"Arn":"$DLQ_ARN"} \
    --region us-east-1
```

### Add Retry Policy

```bash
# Update target with retry configuration
aws events put-targets \
    --rule email-fetcher-schedule \
    --targets "Id"="1","Arn"="$LAMBDA_ARN","RetryPolicy"={"MaximumRetryAttempts":2,"MaximumEventAge":3600} \
    --region us-east-1
```

---

## Step 6: Monitor EventBridge Rules

### View Rule Metrics via Console

1. **Navigate to EventBridge > Rules**
2. **Click on your rule** (`email-fetcher-schedule`)
3. **Go to "Monitoring" tab**
4. **View metrics:**
   - Invocations
   - Failed invocations
   - Throttled rules
   - Triggered rules

### CloudWatch Metrics

```bash
# Get invocation count
aws cloudwatch get-metric-statistics \
    --namespace AWS/Events \
    --metric-name Invocations \
    --dimensions Name=RuleName,Value=email-fetcher-schedule \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Sum \
    --region us-east-1
```

### Check Recent Invocations

```bash
# View Lambda logs to see EventBridge triggers
aws logs tail /aws/lambda/email-fetcher --follow --region us-east-1
```

---

## Step 7: Test EventBridge Rule

### Manual Test via Console

1. **Navigate to EventBridge > Rules**
2. **Select your rule**
3. **Click "Test schedule"**
4. **View test results**

### Manual Trigger via CLI

Simulate an event to test immediately:

```bash
# Create test event
cat > test-event.json << 'EOF'
{
    "version": "0",
    "id": "test-event-id",
    "detail-type": "Scheduled Event",
    "source": "aws.events",
    "account": "123456789012",
    "time": "2024-01-01T12:00:00Z",
    "region": "us-east-1",
    "resources": ["arn:aws:events:us-east-1:123456789012:rule/email-fetcher-schedule"],
    "detail": {}
}
EOF

# Invoke Lambda directly (simulates EventBridge trigger)
aws lambda invoke \
    --function-name email-fetcher \
    --payload file://test-event.json \
    --region us-east-1 \
    response.json

cat response.json
```

### Verify Schedule is Working

```bash
# Wait 5-10 minutes, then check Lambda invocations
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=email-fetcher \
    --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum \
    --region us-east-1
```

---

## Step 8: Cost Optimization

### EventBridge Pricing

- **Custom rules**: First 1 million events per month are free
- **After 1 million**: $1.00 per million events

### Calculate Your Costs

| Schedule | Invocations/Day | Invocations/Month | Cost |
|----------|-----------------|-------------------|------|
| Every 5 min | 288 | ~8,640 | $0.00 (free tier) |
| Every 10 min | 144 | ~4,320 | $0.00 (free tier) |
| Every 15 min | 96 | ~2,880 | $0.00 (free tier) |
| Every hour | 24 | ~720 | $0.00 (free tier) |

**Recommendation:** Even with 5-minute intervals, you're well within the free tier.

### Optimization Tips

1. **Adjust frequency** based on email volume
2. **Use cron** to avoid non-business hours
3. **Disable rule** when not needed
4. **Monitor usage** to avoid unexpected costs

---

## Troubleshooting

### Issue: Rule Not Triggering Lambda

**Solutions:**

1. **Check Rule State**
   ```bash
   aws events describe-rule --name email-fetcher-schedule --region us-east-1
   ```
   Ensure `State: "ENABLED"`

2. **Verify Lambda Permission**
   ```bash
   aws lambda get-policy --function-name email-fetcher --region us-east-1
   ```

3. **Check Target Configuration**
   ```bash
   aws events list-targets-by-rule --rule email-fetcher-schedule --region us-east-1
   ```

4. **View Lambda Logs**
   ```bash
   aws logs tail /aws/lambda/email-fetcher --follow --region us-east-1
   ```

### Issue: Lambda Invoked But Failing

**Solution:** This is a Lambda issue, not EventBridge. Check:
- Lambda function logs
- IAM permissions
- Environment variables
- Function timeout settings

### Issue: Too Many Invocations

**Solution:** Check for duplicate rules:

```bash
# List all rules
aws events list-rules --region us-east-1 | grep email-fetcher

# Remove duplicate rule
aws events remove-targets --rule OLD_RULE_NAME --ids 1 --region us-east-1
aws events delete-rule --name OLD_RULE_NAME --region us-east-1
```

### Issue: Schedule Not Following Expected Pattern

**Solution:** Verify schedule expression:

```bash
# Test cron expression at: https://crontab.guru/
# Remember EventBridge uses 6-field cron (includes year)

# Update schedule
aws events put-rule \
    --name email-fetcher-schedule \
    --schedule-expression "rate(5 minutes)" \
    --region us-east-1
```

---

## Best Practices

1. **Use Rate Expressions** for simple intervals (easier to read)
2. **Use Cron Expressions** for specific times or complex schedules
3. **Add Tags** to rules for organization
4. **Enable DLQ** for production environments
5. **Monitor Metrics** regularly via CloudWatch
6. **Test Changes** before applying to production
7. **Document Schedule** rationale (why 5 min vs 10 min?)
8. **Consider Time Zones** - EventBridge uses UTC

---

## Common Schedule Patterns

### Business Hours Only

```bash
# Monday-Friday, 9 AM - 5 PM (UTC)
cron(0/5 9-17 ? * MON-FRI *)

# Every hour during business hours
cron(0 9-17 ? * MON-FRI *)
```

### Daily at Specific Time

```bash
# Every day at 9 AM UTC
cron(0 9 * * ? *)

# Every day at 6 PM UTC
cron(0 18 * * ? *)
```

### Multiple Times Per Day

```bash
# 9 AM, 12 PM, 3 PM, 6 PM (UTC)
cron(0 9,12,15,18 * * ? *)
```

### Weekdays Only

```bash
# Every 10 minutes, Monday-Friday
cron(0/10 * ? * MON-FRI *)
```

---

## Security Considerations

1. **Least Privilege**: EventBridge only needs `lambda:InvokeFunction` permission
2. **Resource-Based Policy**: Use Lambda resource policy (not IAM role)
3. **Monitoring**: Enable CloudWatch alarms for failed invocations
4. **Audit**: Review EventBridge rules monthly
5. **Tags**: Use tags for access control and cost allocation

---

## Related Documentation

- [Email Fetcher Lambda Setup](../lambda-functions/email-fetcher/SETUP_GUIDE.md)
- [Gmail Setup Guide](../../gmail-setup/SETUP_GUIDE.md)
- [CloudWatch Monitoring](../cloudwatch/SETUP_GUIDE.md) (if exists)
- [Architecture Overview](../../ARCHITECTURE.md)

---

## Next Steps

After setting up EventBridge:

1. ✅ Verify rule is enabled
2. ✅ Wait 5-10 minutes for first trigger
3. ✅ Check CloudWatch logs for invocations
4. → Monitor for 24 hours to ensure stability
5. → Adjust schedule based on email volume
6. → Set up [CloudWatch alarms](#monitoring) for failures

---

## Quick Reference Commands

```bash
# Create rule
aws events put-rule --name email-fetcher-schedule \
  --schedule-expression "rate(5 minutes)" --region us-east-1

# Enable/Disable
aws events enable-rule --name email-fetcher-schedule --region us-east-1
aws events disable-rule --name email-fetcher-schedule --region us-east-1

# List rules
aws events list-rules --region us-east-1

# Delete rule
aws events remove-targets --rule email-fetcher-schedule --ids 1 --region us-east-1
aws events delete-rule --name email-fetcher-schedule --region us-east-1

# Check logs
aws logs tail /aws/lambda/email-fetcher --follow --region us-east-1
```

---

## Additional Resources

- [AWS EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)
- [Schedule Expression Reference](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)
- [Cron Expression Generator](https://crontab.guru/)
- [EventBridge Pricing](https://aws.amazon.com/eventbridge/pricing/)
