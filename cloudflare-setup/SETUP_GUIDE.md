# Cloudflare Email Routing Setup Guide

## Overview

This guide provides step-by-step instructions for setting up Cloudflare Email Routing to forward emails to Gmail. This is a crucial component that allows SevenBot to receive emails sent to unique addresses at your domain (csearfarf.dev).

## Prerequisites

- Domain registered and managed by Cloudflare (csearfarf.dev)
- Gmail account for receiving forwarded emails
- Cloudflare account with domain access
- Basic understanding of DNS records

## Architecture Flow

```
User sends email to:
user-123@csearfarf.dev
         ↓
Cloudflare Email Routing
         ↓
Forward to:
group7bot@gmail.com
         ↓
Lambda Email Fetcher (IMAP)
         ↓
Process & Summarize
```

---

## Step 1: Enable Cloudflare Email Routing

### Via Cloudflare Dashboard

1. **Log in to Cloudflare**
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Select your domain: `csearfarf.dev`

2. **Navigate to Email Routing**
   - Click "Email" in the left sidebar
   - Or go to: https://dash.cloudflare.com/[account-id]/[domain]/email/routing

3. **Enable Email Routing**
   - Click "Enable Email Routing"
   - Cloudflare will automatically add required DNS records

4. **Verify DNS Records**
   Cloudflare adds these records automatically:

   | Type | Name | Value |
   |------|------|-------|
   | MX | @ | route1.mx.cloudflare.net (Priority: 84) |
   | MX | @ | route2.mx.cloudflare.net (Priority: 75) |
   | MX | @ | route3.mx.cloudflare.net (Priority: 46) |
   | TXT | @ | v=spf1 include:_spf.mx.cloudflare.net ~all |

5. **Wait for Activation**
   - Email routing typically activates within 5-10 minutes
   - Status indicator will turn green when ready

---

## Step 2: Add Destination Email Address

### Via Cloudflare Dashboard

1. **Navigate to Destination Addresses**
   - Go to Email > Routing > Destination addresses
   - Click "Add destination address"

2. **Enter Gmail Address**
   | Field | Value |
   |-------|-------|
   | Email address | group7bot@gmail.com |
   | Name (optional) | SevenBot Receiver |

3. **Verify Email Address**
   - Cloudflare sends a verification email to group7bot@gmail.com
   - Open the email and click "Verify email address"
   - This confirms you own the destination address

4. **Confirmation**
   - After verification, status shows "Verified" with a green checkmark

---

## Step 3: Create Catch-All Routing Rule

This allows all emails to *@csearfarf.dev to be forwarded to Gmail.

### Via Cloudflare Dashboard

1. **Navigate to Routing Rules**
   - Go to Email > Routing > Routing rules
   - Click "Create address"

2. **Create Catch-All Rule**
   | Field | Value |
   |-------|-------|
   | Custom address | Select "Catch-all address" |
   | Action | Send to an email |
   | Destination | group7bot@gmail.com |

3. **Enable Rule**
   - Toggle to "Enabled"
   - Click "Save"

### Alternative: Specific Address Pattern

If you want more control, create a rule for specific patterns:

| Field | Value |
|-------|-------|
| Custom address | Use matching pattern |
| Pattern | `*@csearfarf.dev` |
| Action | Send to an email |
| Destination | group7bot@gmail.com |

---

## Step 4: Test Email Routing

### Send Test Email

1. **Use External Email Service**
   - From your personal email (Gmail, Outlook, etc.)
   - Send test email to: `test@csearfarf.dev`
   - Subject: "Test Email Routing"
   - Body: "Testing Cloudflare Email Routing setup"

2. **Check Gmail Inbox**
   - Log in to group7bot@gmail.com
   - Look for the test email
   - Verify it arrives within 1-2 minutes

### Verify Email Headers

Open the received email and view headers to confirm routing:

```
Received: from route1.mx.cloudflare.net
X-Forwarded-To: group7bot@gmail.com
X-Forwarded-For: test@csearfarf.dev
```

---

## Step 5: Configure SPF, DKIM, and DMARC

These records improve email deliverability and prevent spoofing.

### SPF (Sender Policy Framework)

Cloudflare adds this automatically when you enable Email Routing:

```
Type: TXT
Name: @
Content: v=spf1 include:_spf.mx.cloudflare.net ~all
```

### DKIM (DomainKeys Identified Mail)

1. **Navigate to Email > DKIM**
   - Cloudflare provides DKIM signing automatically
   - No additional configuration needed for forwarding

### DMARC (Domain-based Message Authentication)

Add DMARC record for enhanced security:

1. **Add DNS Record**
   - Go to DNS > Records
   - Click "Add record"

   | Type | Name | Content |
   |------|------|---------|
   | TXT | _dmarc | v=DMARC1; p=quarantine; rua=mailto:dmarc@csearfarf.dev |

2. **DMARC Policy Options**
   - `p=none`: Monitor only
   - `p=quarantine`: Mark as spam
   - `p=reject`: Reject unauthorized emails (recommended for production)

---

## Step 6: Configure Gmail for IMAP Access

### Enable IMAP in Gmail

1. **Log in to Gmail**
   - Go to group7bot@gmail.com

2. **Navigate to Settings**
   - Click the gear icon > "See all settings"
   - Go to "Forwarding and POP/IMAP" tab

3. **Enable IMAP**
   - Under "IMAP access"
   - Select "Enable IMAP"
   - Click "Save Changes"

### Create App Password for Lambda

Gmail requires app-specific passwords for third-party apps:

1. **Enable 2-Step Verification**
   - Go to: https://myaccount.google.com/security
   - Under "Signing in to Google"
   - Click "2-Step Verification"
   - Follow prompts to enable

2. **Create App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in again if prompted
   - Select app: "Mail"
   - Select device: "Other (Custom name)"
   - Name it: "SevenBot Lambda"
   - Click "Generate"

3. **Save Password**
   - Copy the 16-character password
   - Store in AWS Secrets Manager or Systems Manager Parameter Store
   - **Never commit this to code!**

---

## Step 7: Set Up Email Filters (Optional)

Organize forwarded emails in Gmail:

### Create Label

1. **Create Label**
   - Gmail > Settings > Labels
   - Click "Create new label"
   - Name: "SevenBot Emails"

### Create Filter

1. **Create Filter**
   - Gmail > Settings > Filters and Blocked Addresses
   - Click "Create a new filter"

2. **Filter Criteria**
   | Field | Value |
   |-------|-------|
   | To | group7bot@gmail.com |
   | Has the words | to:(@csearfarf.dev) |

3. **Filter Actions**
   - ✓ Apply label: "SevenBot Emails"
   - ✓ Skip Inbox (Archive it)
   - ✓ Mark as read
   - Click "Create filter"

This keeps your Gmail inbox clean while allowing Lambda to process emails.

---

## Step 8: Store Gmail Credentials in AWS

### Using AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
    --name sevenbot/gmail-credentials \
    --description "Gmail IMAP credentials for SevenBot" \
    --secret-string '{
        "email": "group7bot@gmail.com",
        "password": "your-16-char-app-password"
    }' \
    --region us-east-1
```

### Using Systems Manager Parameter Store

```bash
# Store email
aws ssm put-parameter \
    --name /sevenbot/gmail/email \
    --value "group7bot@gmail.com" \
    --type String \
    --region us-east-1

# Store password (encrypted)
aws ssm put-parameter \
    --name /sevenbot/gmail/password \
    --value "your-16-char-app-password" \
    --type SecureString \
    --region us-east-1
```

### Grant Lambda Access

Update Lambda IAM role to allow secret access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:YOUR-ACCOUNT-ID:secret:sevenbot/gmail-credentials-*"
        }
    ]
}
```

---

## Step 9: Test End-to-End Flow

### Complete Test

1. **Send Test Email**
   - From external email
   - To: `testuser@csearfarf.dev`
   - Subject: "End-to-End Test"

2. **Verify Cloudflare Routing**
   - Check Cloudflare Email > Analytics
   - Should show 1 forwarded message

3. **Verify Gmail Receipt**
   - Check group7bot@gmail.com
   - Email should arrive within 1-2 minutes

4. **Test Lambda Fetcher**
   - Manually invoke email-fetcher Lambda
   - Check CloudWatch logs
   - Verify email is fetched and processed

5. **Verify Telegram Notification**
   - Check your Telegram bot
   - Should receive summary notification

---

## Monitoring and Analytics

### Cloudflare Email Analytics

1. **View Analytics**
   - Email > Analytics
   - Monitor:
     - Total emails received
     - Forwarded emails
     - Rejected emails
     - Bounced emails

2. **Set Up Notifications**
   - Configure alerts for:
     - High rejection rate
     - Delivery failures
     - Unusual traffic patterns

---

## Troubleshooting

### Issue: Emails Not Being Forwarded

**Solutions:**

1. **Check DNS Records**
   ```bash
   # Verify MX records
   nslookup -type=MX csearfarf.dev
   
   # Should return Cloudflare MX records
   ```

2. **Verify Destination Email**
   - Ensure group7bot@gmail.com is verified
   - Check for verification email in spam folder

3. **Check Routing Rules**
   - Ensure catch-all rule is enabled
   - Verify destination address is correct

### Issue: Gmail Not Receiving Emails

**Solutions:**

1. **Check Gmail Spam Folder**
   - Forwarded emails may be marked as spam
   - Mark as "Not Spam" to train filter

2. **Check Gmail Storage**
   - Ensure Gmail account has available storage
   - Clean up old emails if needed

3. **Verify IMAP is Enabled**
   - Settings > Forwarding and POP/IMAP
   - Ensure IMAP is enabled

### Issue: Lambda Can't Connect to Gmail

**Solutions:**

1. **Verify App Password**
   - Ensure correct 16-character password
   - Regenerate if necessary

2. **Check Security Settings**
   - Verify 2-Step Verification is enabled
   - Allow less secure apps (if using regular password)

3. **Test IMAP Connection**
   ```python
   import imaplib
   
   mail = imaplib.IMAP4_SSL('imap.gmail.com')
   mail.login('group7bot@gmail.com', 'your-app-password')
   print("Connection successful!")
   ```

### Issue: High Email Bounce Rate

**Solutions:**

1. **Check SPF/DKIM/DMARC**
   - Verify DNS records are correct
   - Test with: https://mxtoolbox.com/

2. **Verify Sender Reputation**
   - Check domain reputation
   - Avoid sending spam-like content

3. **Monitor Cloudflare Analytics**
   - Review rejection reasons
   - Address common issues

---

## Security Best Practices

1. **Use Strong Passwords**: Generate strong Gmail app passwords
2. **Limit Forwarding Rules**: Only forward necessary emails
3. **Monitor Access**: Regularly review Gmail security settings
4. **Rotate Credentials**: Change app passwords periodically
5. **Enable 2FA**: Always use 2-step verification
6. **Restrict IMAP Access**: Use IP restrictions if possible
7. **Audit Logs**: Review Gmail activity logs monthly

---

## Advanced Configuration

### Multiple Destination Addresses

Route different email patterns to different destinations:

```
Pattern: support-*@csearfarf.dev
  → support@gmail.com

Pattern: sales-*@csearfarf.dev
  → sales@gmail.com

Pattern: *@csearfarf.dev
  → group7bot@gmail.com (catch-all)
```

### Email Workers (Advanced)

Use Cloudflare Workers to pre-process emails:

```javascript
addEventListener("email", event => {
  event.message.setReject("Spam detected");
  // Or transform message before forwarding
});
```

### Rate Limiting

Prevent abuse by limiting emails per sender:

1. Email > Routing > Rate limiting
2. Configure limits:
   - Max emails per hour: 100
   - Max emails per day: 1000

---

## Cost Information

### Cloudflare Email Routing

- **Free Plan**: Up to 100 recipients
- **Pro Plan**: Unlimited recipients
- **No Additional Cost**: Email routing is included

### Gmail

- **Free**: 15 GB storage (shared with Drive, Photos)
- **Google Workspace**: Paid plans for business use

---

## Related Documentation

- [DynamoDB Setup Guide](../aws/dynamodb/SETUP_GUIDE.md)
- [S3 Setup Guide](../aws/s3/SETUP_GUIDE.md)
- [Lambda Functions Setup](../aws/lambda-functions/)
- [API Gateway Setup](../aws/api-gateway/SETUP_GUIDE.md)
- [Architecture Overview](../ARCHITECTURE.md)

---

## Next Steps

After setting up Cloudflare Email Routing:

1. ✅ Verify email forwarding works
2. ✅ Test Gmail IMAP connection
3. ✅ Store credentials in AWS
4. → Deploy [Email Fetcher Lambda](../aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
5. → Deploy [Email Processor Lambda](../aws/lambda-functions/email-processor/SETUP_GUIDE.md)

---

## Additional Resources

- [Cloudflare Email Routing Docs](https://developers.cloudflare.com/email-routing/)
- [Gmail IMAP Setup](https://support.google.com/mail/answer/7126229)
- [SPF/DKIM/DMARC Guide](https://dmarc.org/overview/)
- [MXToolbox](https://mxtoolbox.com/) - Test email configuration
