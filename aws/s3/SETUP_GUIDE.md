# S3 Setup Guide

## Overview

This guide provides step-by-step instructions for setting up Amazon S3 buckets required by SevenBot. S3 is used to store raw emails, Lambda deployment packages, and optionally logs.

## Prerequisites

- AWS Account with S3 permissions
- AWS CLI installed and configured (optional)
- Basic understanding of S3 buckets and policies

## Buckets Required

SevenBot requires the following S3 buckets:

1. **sevenbot-emails** - Stores raw email content and attachments
2. **sevenbot-deployments** - Stores Lambda deployment packages (optional)
3. **sevenbot-logs** - Stores application logs (optional)

---

## Step 1: Create the Email Storage Bucket

### Via AWS Console

1. **Navigate to S3**
   - Open the [AWS Console](https://console.aws.amazon.com/)
   - Search for "S3" and click on the service

2. **Create Bucket**
   - Click "Create bucket"
   - Enter bucket configuration:

   | Field | Value |
   |-------|-------|
   | Bucket name | `sevenbot-emails-[YOUR-ACCOUNT-ID]` |
   | AWS Region | `us-east-1` (or your preferred region) |
   | Block Public Access | **Keep all enabled** (recommended) |

   **Note:** Bucket names must be globally unique. Add your AWS account ID or a unique identifier.

3. **Configure Bucket Versioning**
   - Under "Bucket Versioning"
   - Select "Enable" (recommended for data protection)

4. **Configure Encryption**
   - Under "Default encryption"
   - Choose "Server-side encryption with Amazon S3 managed keys (SSE-S3)"
   - Or use "AWS Key Management Service (SSE-KMS)" for enhanced security

5. **Create Bucket**
   - Click "Create bucket"

### Via AWS CLI

```bash
# Replace YOUR-ACCOUNT-ID with your AWS account ID
aws s3api create-bucket \
    --bucket sevenbot-emails-YOUR-ACCOUNT-ID \
    --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket sevenbot-emails-YOUR-ACCOUNT-ID \
    --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket sevenbot-emails-YOUR-ACCOUNT-ID \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'
```

---

## Step 2: Configure Bucket Structure

Create a logical folder structure for organizing emails:

```
sevenbot-emails-[ACCOUNT-ID]/
├── raw-emails/              # Raw email content
│   ├── YYYY/MM/DD/         # Date-based organization
│   └── [message-id].json
├── attachments/            # Email attachments
│   └── [message-id]/
│       ├── file1.pdf
│       └── file2.jpg
└── processed/              # Processed emails archive
    └── YYYY/MM/DD/
```

**Note:** S3 folders are virtual; they're created automatically when objects are uploaded with prefixes.

---

## Step 3: Set Up Lifecycle Policies

Configure lifecycle rules to automatically archive or delete old emails:

### Via AWS Console

1. **Navigate to Bucket**
   - Click on your `sevenbot-emails` bucket
   - Go to "Management" tab
   - Click "Create lifecycle rule"

2. **Create Archive Rule**
   | Field | Value |
   |-------|-------|
   | Rule name | `archive-old-emails` |
   | Prefix | `raw-emails/` |
   | Transition to Glacier | 90 days |
   | Expire | 365 days |

3. **Apply Rule**
   - Review and click "Create rule"

### Via AWS CLI

```bash
aws s3api put-bucket-lifecycle-configuration \
    --bucket sevenbot-emails-YOUR-ACCOUNT-ID \
    --lifecycle-configuration file://lifecycle-policy.json
```

**lifecycle-policy.json:**

```json
{
    "Rules": [
        {
            "Id": "archive-old-emails",
            "Status": "Enabled",
            "Prefix": "raw-emails/",
            "Transitions": [
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ],
            "Expiration": {
                "Days": 365
            }
        }
    ]
}
```

---

## Step 4: Configure Bucket Policy

Set up bucket policy to allow Lambda functions to read/write:

### Via AWS Console

1. **Navigate to Bucket Permissions**
   - Click on your bucket
   - Go to "Permissions" tab
   - Scroll to "Bucket policy"
   - Click "Edit"

2. **Add Policy**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowLambdaAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::YOUR-ACCOUNT-ID:role/email-processor-role",
                    "arn:aws:iam::YOUR-ACCOUNT-ID:role/email-fetcher-role"
                ]
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::sevenbot-emails-YOUR-ACCOUNT-ID/*"
        },
        {
            "Sid": "AllowLambdaListBucket",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::YOUR-ACCOUNT-ID:role/email-processor-role",
                    "arn:aws:iam::YOUR-ACCOUNT-ID:role/email-fetcher-role"
                ]
            },
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::sevenbot-emails-YOUR-ACCOUNT-ID"
        }
    ]
}
```

3. **Save Changes**

### Via AWS CLI

```bash
aws s3api put-bucket-policy \
    --bucket sevenbot-emails-YOUR-ACCOUNT-ID \
    --policy file://bucket-policy.json
```

---

## Step 5: Set Up IAM Permissions for Lambda

Create an IAM policy for Lambda functions:

### Create IAM Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::sevenbot-emails-YOUR-ACCOUNT-ID",
                "arn:aws:s3:::sevenbot-emails-YOUR-ACCOUNT-ID/*"
            ]
        }
    ]
}
```

### Attach to Lambda Roles

1. Navigate to IAM > Policies
2. Create policy with name `SevenBot-S3-Policy`
3. Attach to Lambda execution roles:
   - `email-processor-role`
   - `email-fetcher-role`

---

## Step 6: Enable S3 Event Notifications (Optional)

Configure S3 to trigger Lambda when new emails arrive:

### Via AWS Console

1. **Navigate to Bucket Properties**
   - Click on your bucket
   - Go to "Properties" tab
   - Scroll to "Event notifications"
   - Click "Create event notification"

2. **Configure Event**
   | Field | Value |
   |-------|-------|
   | Event name | `new-email-notification` |
   | Prefix | `raw-emails/` |
   | Suffix | `.json` |
   | Event types | ✓ PUT |
   | Destination | Lambda function |
   | Lambda function | `email-processor` |

3. **Save Configuration**

### Via AWS CLI

```bash
aws s3api put-bucket-notification-configuration \
    --bucket sevenbot-emails-YOUR-ACCOUNT-ID \
    --notification-configuration file://notification-config.json
```

**notification-config.json:**

```json
{
    "LambdaFunctionConfigurations": [
        {
            "Id": "new-email-notification",
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:YOUR-ACCOUNT-ID:function:email-processor",
            "Events": ["s3:ObjectCreated:Put"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {
                            "Name": "prefix",
                            "Value": "raw-emails/"
                        },
                        {
                            "Name": "suffix",
                            "Value": ".json"
                        }
                    ]
                }
            }
        }
    ]
}
```

---

## Step 7: Create Deployment Bucket (Optional)

For storing Lambda deployment packages:

### Quick Setup

```bash
# Create bucket
aws s3api create-bucket \
    --bucket sevenbot-deployments-YOUR-ACCOUNT-ID \
    --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket sevenbot-deployments-YOUR-ACCOUNT-ID \
    --versioning-configuration Status=Enabled
```

---

## Step 8: Test Your Setup

### Test Upload

```python
import boto3
import json
from datetime import datetime

s3 = boto3.client('s3', region_name='us-east-1')
bucket_name = 'sevenbot-emails-YOUR-ACCOUNT-ID'

# Create test email
test_email = {
    'message_id': 'test-123',
    'subject': 'Test Email',
    'from': 'test@example.com',
    'timestamp': datetime.utcnow().isoformat()
}

# Upload to S3
s3.put_object(
    Bucket=bucket_name,
    Key='raw-emails/2024/01/01/test-123.json',
    Body=json.dumps(test_email),
    ContentType='application/json'
)

print("Upload successful!")
```

### Test Read

```python
# Read from S3
response = s3.get_object(
    Bucket=bucket_name,
    Key='raw-emails/2024/01/01/test-123.json'
)

email_data = json.loads(response['Body'].read())
print("Email data:", email_data)
```

### Test List

```python
# List objects
response = s3.list_objects_v2(
    Bucket=bucket_name,
    Prefix='raw-emails/'
)

for obj in response.get('Contents', []):
    print(f"Found: {obj['Key']}")
```

### Clean Up

```python
# Delete test object
s3.delete_object(
    Bucket=bucket_name,
    Key='raw-emails/2024/01/01/test-123.json'
)
```

---

## Step 9: Enable CloudWatch Metrics

### Via AWS Console

1. **Navigate to S3 Metrics**
   - Click on your bucket
   - Go to "Metrics" tab
   - Enable "Request metrics"

2. **Create Metric Filter**
   - Filter name: `all-operations`
   - Prefix: (leave empty for all)

### Set Up Alarms

Create CloudWatch alarms for:
- **High Error Rate**: 4xx/5xx errors
- **Storage Size**: Alert when bucket size exceeds threshold
- **Request Rate**: Unusually high request rate

---

## Best Practices

1. **Use Versioning**: Protect against accidental deletions
2. **Enable Encryption**: Always encrypt sensitive data
3. **Implement Lifecycle Policies**: Reduce storage costs
4. **Use Intelligent-Tiering**: For unpredictable access patterns
5. **Monitor Access Logs**: Enable S3 server access logging
6. **Tag Resources**: Add tags for cost tracking
7. **Use Least Privilege**: Grant minimal required permissions
8. **Enable MFA Delete**: For production buckets (extra protection)

---

## Troubleshooting

### Issue: "AccessDenied" Error

**Solution:**
1. Check bucket policy allows your Lambda role
2. Verify IAM policy is attached to Lambda execution role
3. Check bucket is not public (unless intentional)

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket sevenbot-emails-YOUR-ACCOUNT-ID
```

### Issue: "NoSuchBucket" Error

**Solution:**
1. Verify bucket name and region
2. Check bucket exists:

```bash
aws s3 ls
```

### Issue: High Costs

**Solution:**
1. Review lifecycle policies
2. Check storage class (use Intelligent-Tiering)
3. Delete old/unused objects
4. Monitor with AWS Cost Explorer

### Issue: Slow Performance

**Solution:**
1. Use multipart upload for large files
2. Implement caching with CloudFront
3. Use S3 Transfer Acceleration
4. Optimize object key naming (avoid sequential prefixes)

---

## Security Checklist

- [ ] Block all public access enabled
- [ ] Bucket versioning enabled
- [ ] Default encryption enabled
- [ ] Bucket policy restricts access to specific roles
- [ ] Access logging enabled
- [ ] MFA delete enabled (for production)
- [ ] Object lock enabled (if compliance required)
- [ ] Regular security audits scheduled

---

## Cost Optimization

### Storage Classes

| Class | Use Case | Cost |
|-------|----------|------|
| Standard | Frequently accessed | $$$ |
| Intelligent-Tiering | Unknown access patterns | $$ |
| Glacier | Archive (90+ days) | $ |

### Tips

1. Use lifecycle policies to transition to cheaper storage
2. Delete incomplete multipart uploads
3. Compress data before uploading
4. Use CloudFront for frequently accessed content

---

## Related Documentation

- [DynamoDB Setup Guide](../dynamodb/SETUP_GUIDE.md)
- [Lambda Functions Setup](../lambda-functions/)
- [API Gateway Setup](../api-gateway/SETUP_GUIDE.md)
- [Architecture Overview](../../ARCHITECTURE.md)

---

## Next Steps

After setting up S3:

1. ✅ Verify buckets are created
2. ✅ Test upload/download operations
3. → Deploy [Lambda functions](../lambda-functions/)
4. → Configure [API Gateway](../api-gateway/SETUP_GUIDE.md)
5. → Set up [Cloudflare Email Routing](../../cloudflare-setup/SETUP_GUIDE.md)

---

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [S3 Pricing Calculator](https://calculator.aws/#/addService/S3)
