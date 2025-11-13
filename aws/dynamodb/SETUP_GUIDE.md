# DynamoDB Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the DynamoDB tables required by SevenBot. The bot uses DynamoDB to store user data, email mappings, and processing states.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured (optional but recommended)
- Basic understanding of DynamoDB concepts (tables, keys, indexes)

## Tables Required

SevenBot requires the following DynamoDB tables:

1. **telegram-users** - Stores user information and email mappings
2. **email-processing-state** - Tracks email processing status (optional, for idempotency)

---

## Step 1: Create the telegram-users Table

### Via AWS Console

1. **Navigate to DynamoDB**
   - Open the [AWS Console](https://console.aws.amazon.com/)
   - Search for "DynamoDB" in the services search bar
   - Click on "DynamoDB"

2. **Create Table**
   - Click "Create table"
   - Enter the following details:

   | Field | Value |
   |-------|-------|
   | Table name | `telegram-users` |
   | Partition key | `chat_id` (Number) |
   | Sort key | Leave empty |

3. **Configure Settings**
   - **Table settings**: Choose "Customize settings"
   - **Table class**: Standard
   - **Capacity mode**: On-demand (recommended) or Provisioned
     - If Provisioned: Start with 5 RCU and 5 WCU
   
4. **Encryption**
   - Keep default (AWS owned key) or choose AWS managed key for additional security

5. **Create Table**
   - Click "Create table"
   - Wait for table status to become "Active" (usually 1-2 minutes)

### Via AWS CLI

```bash
aws dynamodb create-table \
    --table-name telegram-users \
    --attribute-definitions \
        AttributeName=chat_id,AttributeType=N \
    --key-schema \
        AttributeName=chat_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

**Replace `us-east-1` with your preferred AWS region.**

---

## Step 2: Configure telegram-users Table Attributes

The table will store the following attributes (created automatically when items are inserted):

| Attribute | Type | Description |
|-----------|------|-------------|
| `chat_id` | Number | Telegram chat ID (Primary Key) |
| `email_address` | String | Generated unique email address |
| `created_at` | String | ISO 8601 timestamp of user registration |
| `last_summary_time` | String | Timestamp of last email summary sent |
| `email_count` | Number | Total emails processed for this user |
| `username` | String | Telegram username (optional) |
| `first_name` | String | User's first name (optional) |

**Note:** DynamoDB is schema-less, so these attributes don't need to be defined upfront.

---

## Step 3: Create email-processing-state Table (Optional)

This table helps prevent duplicate email processing.

### Via AWS Console

1. **Create Table**
   - Click "Create table"
   - Enter the following details:

   | Field | Value |
   |-------|-------|
   | Table name | `email-processing-state` |
   | Partition key | `message_id` (String) |
   | Sort key | Leave empty |

2. **Enable TTL (Time to Live)**
   - After table is created, go to "Additional settings" tab
   - Click "Edit" in the TTL section
   - Enable TTL with attribute name: `ttl`
   - This will auto-delete old records after 30 days

### Via AWS CLI

```bash
aws dynamodb create-table \
    --table-name email-processing-state \
    --attribute-definitions \
        AttributeName=message_id,AttributeType=S \
    --key-schema \
        AttributeName=message_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1

# Enable TTL
aws dynamodb update-time-to-live \
    --table-name email-processing-state \
    --time-to-live-specification \
        "Enabled=true, AttributeName=ttl" \
    --region us-east-1
```

---

## Step 4: Create Global Secondary Index (Optional Enhancement)

To query users by email address, create a GSI:

### Via AWS Console

1. **Navigate to telegram-users Table**
   - Click on the `telegram-users` table
   - Go to "Indexes" tab
   - Click "Create index"

2. **Configure Index**
   | Field | Value |
   |-------|-------|
   | Partition key | `email_address` (String) |
   | Index name | `email-address-index` |
   | Attribute projections | All |

3. **Create Index**
   - Click "Create index"
   - Wait for status to become "Active"

### Via AWS CLI

```bash
aws dynamodb update-table \
    --table-name telegram-users \
    --attribute-definitions \
        AttributeName=email_address,AttributeType=S \
    --global-secondary-index-updates \
        "[{\"Create\":{\"IndexName\":\"email-address-index\",\"KeySchema\":[{\"AttributeName\":\"email_address\",\"KeyType\":\"HASH\"}],\"Projection\":{\"ProjectionType\":\"ALL\"},\"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}}}]" \
    --region us-east-1
```

---

## Step 5: Set Up IAM Permissions

Your Lambda functions need permissions to access DynamoDB.

### Create IAM Policy

1. **Open IAM Console**
   - Navigate to IAM > Policies
   - Click "Create policy"

2. **Define Policy (JSON)**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DeleteItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/telegram-users",
                "arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/telegram-users/index/*",
                "arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/email-processing-state"
            ]
        }
    ]
}
```

3. **Name and Create**
   - Name: `SevenBot-DynamoDB-Policy`
   - Click "Create policy"

4. **Attach to Lambda Execution Roles**
   - Go to IAM > Roles
   - Find your Lambda execution roles
   - Attach the `SevenBot-DynamoDB-Policy` to each role

---

## Step 6: Test Your Setup

### Test Write Operation

```python
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('telegram-users')

# Insert a test user
response = table.put_item(
    Item={
        'chat_id': 123456789,
        'email_address': 'test-user@csearfarf.dev',
        'created_at': datetime.utcnow().isoformat(),
        'email_count': 0
    }
)
print("Write successful:", response)
```

### Test Read Operation

```python
# Read the test user
response = table.get_item(
    Key={'chat_id': 123456789}
)
print("User data:", response.get('Item'))
```

### Clean Up Test Data

```python
# Delete test user
table.delete_item(
    Key={'chat_id': 123456789}
)
```

---

## Step 7: Monitor and Optimize

### Enable CloudWatch Metrics

1. **Navigate to DynamoDB Console**
   - Select your table
   - Go to "Monitoring" tab
   - Enable "Contributor Insights" for detailed metrics

### Set Up Alarms

Create CloudWatch alarms for:
- **Throttled Requests**: Alert when read/write throttling occurs
- **User Errors**: Alert on 400-level errors
- **Consumed Capacity**: Monitor capacity usage

### Cost Optimization

- **On-Demand vs Provisioned**: Switch to provisioned if you have predictable traffic
- **Review TTL Settings**: Ensure old data is being cleaned up
- **Monitor Table Size**: Large tables impact costs

---

## Troubleshooting

### Issue: "ResourceNotFoundException"

**Solution**: Verify table name and region match your Lambda configuration.

```python
# Check table exists
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
tables = dynamodb.list_tables()
print("Available tables:", tables['TableNames'])
```

### Issue: "AccessDeniedException"

**Solution**: Verify IAM role has DynamoDB permissions:

1. Check Lambda execution role
2. Verify policy is attached
3. Check resource ARNs in policy

### Issue: High Latency

**Solution**:
- Use consistent reads only when necessary
- Implement caching (ElastiCache or Lambda environment variables)
- Optimize query patterns

### Issue: Hot Partition

**Solution**:
- Review access patterns
- Consider adding a random suffix to partition keys
- Use DynamoDB Accelerator (DAX) for read-heavy workloads

---

## Best Practices

1. **Use Consistent Naming**: Follow AWS naming conventions
2. **Enable Point-in-Time Recovery**: For production tables
3. **Tag Your Resources**: Add tags for cost tracking and organization
4. **Use Batch Operations**: When processing multiple items
5. **Implement Exponential Backoff**: For retry logic
6. **Monitor Costs**: Set up billing alerts

---

## Related Documentation

- [S3 Setup Guide](../s3/SETUP_GUIDE.md)
- [Lambda Functions Setup](../lambda-functions/)
- [API Gateway Setup](../api-gateway/SETUP_GUIDE.md)
- [Architecture Overview](../../ARCHITECTURE.md)

---

## Next Steps

After setting up DynamoDB:

1. ✅ Verify tables are active
2. ✅ Test read/write operations
3. → Set up [S3 buckets](../s3/SETUP_GUIDE.md)
4. → Deploy [Lambda functions](../lambda-functions/)
5. → Configure [API Gateway](../api-gateway/SETUP_GUIDE.md)

---

## Additional Resources

- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
