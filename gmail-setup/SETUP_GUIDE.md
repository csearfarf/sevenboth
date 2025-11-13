# Gmail Setup Guide for SevenBot

## Overview

This guide covers setting up a Gmail account specifically for SevenBot email processing. Gmail serves as the intermediate email inbox where Cloudflare forwards emails before they're fetched by the Lambda function via IMAP.

## Prerequisites

- Google Account (or create a new one)
- Access to Google Security settings
- Ability to enable 2-Step Verification
- Basic understanding of IMAP protocol

## Architecture Flow

```
Cloudflare Email Routing
         ↓
  Forwards to Gmail
         ↓
   Gmail IMAP Inbox
         ↓
  Email Fetcher Lambda
  (Connects via IMAP)
         ↓
   Stores in S3
```

---

## Step 1: Create Gmail Account (If Needed)

### Option A: Use Existing Gmail

If you already have a Gmail account you want to use:
- **Recommended:** Create a dedicated account for better organization
- **Acceptable:** Use existing account if you prefer

### Option B: Create New Gmail Account

1. **Go to Gmail**
   - Visit [https://accounts.google.com/signup](https://accounts.google.com/signup)

2. **Enter Account Details**
   | Field | Recommended Value |
   |-------|-------------------|
   | First Name | Seven |
   | Last Name | Bot |
   | Username | `group7bot` (or similar) |
   | Password | Strong password (20+ characters) |

3. **Complete Setup**
   - Add phone number (required for 2FA)
   - Add recovery email
   - Accept terms

4. **Verify Account**
   - Enter phone verification code
   - Complete setup

**Created Account Example:** `group7bot@gmail.com`

---

## Step 2: Enable IMAP Access

### Navigate to Gmail Settings

1. **Open Gmail**
   - Go to [gmail.com](https://gmail.com)
   - Sign in to your SevenBot Gmail account

2. **Access Settings**
   - Click the ⚙️ (gear icon) in top-right
   - Click "See all settings"

### Enable IMAP

1. **Go to "Forwarding and POP/IMAP" Tab**
   - Click on the tab at the top

2. **IMAP Access Section**
   - Find "IMAP access" section
   - Select: ✅ **Enable IMAP**

3. **Configure IMAP Settings** (Optional)
   | Setting | Recommended Value |
   |---------|-------------------|
   | Folder size limits | Do not limit |
   | When messages are marked as deleted | Auto-Expunge off |
   | Maximum number of messages | Unlimited |

4. **Save Changes**
   - Scroll to bottom
   - Click "Save Changes"

### Verify IMAP is Enabled

```python
# Test IMAP connection (run locally, not in Lambda yet)
import imaplib

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    print("✅ Successfully connected to Gmail IMAP server")
    mail.logout()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## Step 3: Enable 2-Step Verification

App passwords require 2-Step Verification to be enabled.

### Enable 2FA

1. **Go to Google Account Security**
   - Visit [myaccount.google.com/security](https://myaccount.google.com/security)
   - Or: Gmail > Profile icon > Manage your Google Account > Security

2. **Find "Signing in to Google"**
   - Look for "2-Step Verification"
   - Click on it

3. **Get Started**
   - Click "Get Started"
   - Enter your password if prompted

4. **Add Phone Number**
   - Enter your phone number
   - Choose: **Text message (SMS)** or **Phone call**
   - Click "Next"

5. **Verify Phone**
   - Enter the 6-digit code you received
   - Click "Next"

6. **Turn On 2-Step Verification**
   - Click "Turn On"
   - Confirmation: "2-Step Verification is on"

### Backup Options (Recommended)

1. **Add Backup Phone**
   - Click "Add a second phone number"
   - Enter another phone for backup

2. **Add Backup Codes**
   - Click "Backup codes"
   - Generate 10 backup codes
   - **Save these securely** (password manager recommended)

3. **Add Security Key (Optional)**
   - For enhanced security
   - Use hardware key like YubiKey

---

## Step 4: Generate App Password

App passwords allow Lambda to connect without your main Google password.

### Create App Password

1. **Navigate to App Passwords**
   - Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Or: Security > 2-Step Verification > App passwords (at bottom)

2. **Enter Password**
   - Google may ask you to sign in again
   - Enter your Gmail password

3. **Select App and Device**
   | Field | Value |
   |-------|-------|
   | Select app | **Mail** |
   | Select device | **Other (Custom name)** |
   | Custom name | `SevenBot Lambda` or `Email Fetcher` |

4. **Generate**
   - Click "Generate"
   - A 16-character password appears (e.g., `abcd efgh ijkl mnop`)

5. **Save Password Securely**
   - **CRITICAL:** Copy this password immediately
   - **You won't see it again**
   - Store in password manager
   - Do NOT commit to code repository

### App Password Format

```
Generated: abcd efgh ijkl mnop
For Use:   abcdefghijklmnop (remove spaces)
```

**Note:** When using in Lambda, remove the spaces.

---

## Step 5: Configure Gmail Filters (Optional but Recommended)

Organize incoming emails to keep your inbox clean.

### Create Label for SevenBot Emails

1. **Create Label**
   - Gmail > Settings > Labels
   - Scroll to "Labels" section
   - Click "Create new label"
   - Name: `SevenBot Emails` or `Bot Processed`
   - Click "Create"

### Create Filter

1. **Create Filter**
   - Gmail > Settings > Filters and Blocked Addresses
   - Click "Create a new filter"

2. **Filter Criteria**
   | Field | Value |
   |-------|-------|
   | To | `group7bot@gmail.com` |
   | Has the words | `to:(@csearfarf.dev)` |

3. **Filter Actions**
   - ✅ **Skip the Inbox (Archive it)**
   - ✅ **Apply the label:** SevenBot Emails
   - ✅ **Mark as read**
   - ⬜ Never send it to Spam (optional)

4. **Create Filter**
   - Click "Create filter"

**Why?** This keeps processed emails out of your main inbox while still accessible for debugging.

### Alternative: Folder-Based Organization

```
Gmail Labels:
├── SevenBot Emails
│   ├── Processed     (emails Lambda has read)
│   ├── Errors        (emails that failed processing)
│   └── Archived      (old emails)
```

---

## Step 6: Configure Storage Settings

### Check Storage Quota

1. **View Storage**
   - Go to [google.com/settings/storage](https://google.com/settings/storage)
   - Check available space (free: 15 GB shared across Gmail, Drive, Photos)

### Set Up Storage Management

1. **Gmail Settings > General**
   - Scroll to "Maximum page size"
   - Recommended: 50 conversations per page

2. **Enable Auto-Delete (Optional)**
   - Settings > Filters
   - Create filter: Older than 30 days
   - Action: Delete automatically

### Storage Best Practices

| Emails/Day | Storage/Month | Recommendation |
|------------|---------------|----------------|
| 10-50 | ~10 MB | No action needed |
| 50-200 | ~50 MB | Auto-delete after 30 days |
| 200+ | ~200 MB | Auto-delete after 7 days |

---

## Step 7: Test IMAP Connection

### Test Locally (Before Lambda)

Create `test_gmail_imap.py`:

```python
#!/usr/bin/env python3
import imaplib
import sys

# Configuration
GMAIL_USER = "group7bot@gmail.com"
GMAIL_PASS = "abcdefghijklmnop"  # Your 16-char app password

def test_imap_connection():
    print("Testing Gmail IMAP connection...")
    
    try:
        # Connect to Gmail
        print("1. Connecting to imap.gmail.com:993...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        print("   ✅ Connected")
        
        # Login
        print(f"2. Logging in as {GMAIL_USER}...")
        mail.login(GMAIL_USER, GMAIL_PASS)
        print("   ✅ Logged in")
        
        # Select inbox
        print("3. Selecting INBOX...")
        status, messages = mail.select('INBOX')
        if status == 'OK':
            message_count = messages[0].decode()
            print(f"   ✅ INBOX selected ({message_count} messages)")
        
        # List folders
        print("4. Listing folders...")
        status, folders = mail.list()
        if status == 'OK':
            print(f"   ✅ Found {len(folders)} folders")
            for folder in folders[:5]:  # Show first 5
                print(f"      - {folder.decode()}")
        
        # Search for emails
        print("5. Searching for unread emails...")
        status, messages = mail.search(None, 'UNSEEN')
        if status == 'OK':
            unread_count = len(messages[0].split()) if messages[0] else 0
            print(f"   ✅ Found {unread_count} unread emails")
        
        # Logout
        print("6. Logging out...")
        mail.logout()
        print("   ✅ Logged out")
        
        print("\n🎉 All tests passed! Gmail IMAP is working correctly.")
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"\n❌ IMAP Error: {e}")
        print("\nPossible issues:")
        print("  - IMAP not enabled (check Gmail settings)")
        print("  - Incorrect app password")
        print("  - 2-Step Verification not enabled")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imap_connection()
    sys.exit(0 if success else 1)
```

**Run test:**

```bash
python test_gmail_imap.py
```

**Expected output:**

```
Testing Gmail IMAP connection...
1. Connecting to imap.gmail.com:993...
   ✅ Connected
2. Logging in as group7bot@gmail.com...
   ✅ Logged in
3. Selecting INBOX...
   ✅ INBOX selected (5 messages)
4. Listing folders...
   ✅ Found 8 folders
      - (\HasNoChildren) "/" "INBOX"
      - (\HasNoChildren) "/" "[Gmail]/All Mail"
      ...
5. Searching for unread emails...
   ✅ Found 2 unread emails
6. Logging out...
   ✅ Logged out

🎉 All tests passed! Gmail IMAP is working correctly.
```

---

## Step 8: Store Credentials Securely

### Option A: AWS Secrets Manager (Recommended)

```bash
# Create secret
aws secretsmanager create-secret \
    --name sevenbot/gmail-credentials \
    --description "Gmail IMAP credentials for SevenBot" \
    --secret-string '{
        "email": "group7bot@gmail.com",
        "password": "abcdefghijklmnop"
    }' \
    --region us-east-1

# Retrieve secret (to verify)
aws secretsmanager get-secret-value \
    --secret-id sevenbot/gmail-credentials \
    --region us-east-1
```

**Update Lambda to use Secrets Manager:**

```python
import boto3
import json

def get_gmail_credentials():
    secret_name = "sevenbot/gmail-credentials"
    region_name = "us-east-1"
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    
    return secret['email'], secret['password']

# Usage in Lambda
gmail_user, gmail_pass = get_gmail_credentials()
```

### Option B: AWS Systems Manager Parameter Store

```bash
# Store credentials
aws ssm put-parameter \
    --name /sevenbot/gmail/email \
    --value "group7bot@gmail.com" \
    --type String \
    --region us-east-1

aws ssm put-parameter \
    --name /sevenbot/gmail/password \
    --value "abcdefghijklmnop" \
    --type SecureString \
    --region us-east-1

# Retrieve (to verify)
aws ssm get-parameter \
    --name /sevenbot/gmail/email \
    --region us-east-1

aws ssm get-parameter \
    --name /sevenbot/gmail/password \
    --with-decryption \
    --region us-east-1
```

### Option C: Environment Variables (Least Secure)

```bash
# Update Lambda environment variables
aws lambda update-function-configuration \
    --function-name email-fetcher \
    --environment Variables="{
        GMAIL_USER=group7bot@gmail.com,
        GMAIL_PASS=abcdefghijklmnop,
        S3_BUCKET_NAME=sevenbot-emails-123456789
    }" \
    --region us-east-1
```

**⚠️ Warning:** Environment variables are visible in Lambda console. Use Secrets Manager for production.

---

## Step 9: Security Best Practices

### Account Security

1. **Use Dedicated Account**
   - Don't use personal Gmail
   - Create `projectname-bot@gmail.com` pattern

2. **Enable All Security Features**
   - ✅ 2-Step Verification
   - ✅ Backup codes saved
   - ✅ Recovery email added
   - ✅ Recovery phone added
   - ✅ Security checkup reviewed

3. **App Password Management**
   - Create separate app password per service
   - Revoke unused app passwords
   - Rotate app passwords quarterly

4. **Monitor Account Activity**
   - Check [myaccount.google.com/security](https://myaccount.google.com/security)
   - Review "Recent security events"
   - Set up alerts for suspicious activity

### IMAP Security

1. **Connection Security**
   - Always use `IMAP4_SSL` (port 993)
   - Never use plain IMAP (port 143)

2. **Credential Security**
   - Never commit credentials to git
   - Use AWS Secrets Manager
   - Rotate app passwords regularly

3. **Access Control**
   - Limit Lambda IAM permissions
   - Use VPC for Lambda (optional, extra security)
   - Monitor CloudWatch logs for suspicious activity

---

## Step 10: Troubleshooting

### Issue: "Authentication failed"

**Solutions:**

1. **Check IMAP is Enabled**
   - Gmail > Settings > Forwarding and POP/IMAP
   - Ensure "Enable IMAP" is selected

2. **Verify 2FA is Enabled**
   - Go to Security settings
   - Confirm "2-Step Verification: On"

3. **Regenerate App Password**
   - Delete old app password
   - Create new one
   - Update Lambda environment variable

4. **Check Password Format**
   - Remove spaces: `abcd efgh ijkl mnop` → `abcdefghijklmnop`
   - Check for typos

### Issue: "Too many login attempts"

**Solution:** Gmail rate limits IMAP connections.

```python
# Add exponential backoff
import time
import random

def connect_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(username, password)
            return mail
        except imaplib.IMAP4.error as e:
            if "too many" in str(e).lower():
                wait_time = (2 ** attempt) + random.random()
                print(f"Rate limited. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

### Issue: "No emails found" (but inbox has emails)

**Solutions:**

1. **Check Search Criteria**
   ```python
   # Try different search criteria
   status, messages = mail.search(None, 'ALL')  # All emails
   status, messages = mail.search(None, 'UNSEEN')  # Unread only
   status, messages = mail.search(None, 'SINCE', '01-Jan-2024')  # Date-based
   ```

2. **Select Different Folder**
   ```python
   mail.select('[Gmail]/All Mail')  # All emails including archived
   ```

3. **Check Labels/Filters**
   - Email might be auto-archived by filter
   - Check Gmail filters settings

### Issue: App Password Not Working

**Solution:**

1. **Verify 2FA is properly enabled**
2. **Wait 15 minutes after generating app password**
3. **Try generating from different browser**
4. **Check Google Account security notifications**

---

## Maintenance

### Monthly Tasks

- [ ] Review Gmail storage usage
- [ ] Check for unusual login activity
- [ ] Verify IMAP connection still works
- [ ] Review and clean up old emails
- [ ] Check CloudWatch logs for errors

### Quarterly Tasks

- [ ] Rotate app password
- [ ] Review Gmail filters
- [ ] Update backup codes
- [ ] Review security settings
- [ ] Test disaster recovery

### Annual Tasks

- [ ] Full security audit
- [ ] Consider migrating to Google Workspace (if scaling)
- [ ] Review and update documentation

---

## Gmail Limits and Quotas

| Limit | Value | Impact |
|-------|-------|--------|
| IMAP connections | 15 simultaneous | Lambda concurrency should be ≤ 15 |
| Emails per day | 500 (free), 2000 (Workspace) | Affects Lambda schedule |
| Storage | 15 GB (free), 30 GB+ (paid) | Need cleanup strategy |
| IMAP download | ~2.5 GB/day | Monitor bandwidth |

**Recommendation:** Set Lambda concurrency to 1 to avoid hitting connection limit.

---

## Alternative Email Providers

If Gmail doesn't meet your needs:

| Provider | IMAP Support | Free Tier | Notes |
|----------|--------------|-----------|-------|
| **Gmail** | ✅ Yes | 15 GB | Best integration, most reliable |
| **Outlook** | ✅ Yes | 15 GB | Good alternative |
| **ProtonMail** | ⚠️ Paid | 500 MB | Privacy-focused, requires Bridge |
| **Zoho Mail** | ✅ Yes | 5 GB | Business-oriented |
| **AWS WorkMail** | ✅ Yes | Paid | Native AWS integration |

---

## Related Documentation

- [Email Fetcher Lambda Setup](../aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
- [Cloudflare Email Routing Setup](../cloudflare-setup/SETUP_GUIDE.md)
- [EventBridge Schedule Setup](../aws/eventbridge/SETUP_GUIDE.md)
- [Architecture Overview](../ARCHITECTURE.md)

---

## Next Steps

After Gmail setup:

1. ✅ Verify IMAP connection works locally
2. ✅ Store credentials in AWS Secrets Manager
3. → Configure [Cloudflare Email Routing](../cloudflare-setup/SETUP_GUIDE.md)
4. → Deploy [Email Fetcher Lambda](../aws/lambda-functions/email-fetcher/SETUP_GUIDE.md)
5. → Set up [EventBridge schedule](../aws/eventbridge/SETUP_GUIDE.md)
6. → Test end-to-end email flow

---

## Quick Reference

```bash
# Test IMAP connection
python test_gmail_imap.py

# Store in Secrets Manager
aws secretsmanager create-secret \
  --name sevenbot/gmail-credentials \
  --secret-string '{"email":"group7bot@gmail.com","password":"APP_PASSWORD"}'

# Update Lambda
aws lambda update-function-configuration \
  --function-name email-fetcher \
  --environment Variables="{GMAIL_USER=group7bot@gmail.com,GMAIL_PASS=APP_PASSWORD}"
```

---

## Additional Resources

- [Gmail IMAP Settings](https://support.google.com/mail/answer/7126229)
- [App Passwords Help](https://support.google.com/accounts/answer/185833)
- [Python imaplib Documentation](https://docs.python.org/3/library/imaplib.html)
- [Gmail API Limits](https://developers.google.com/gmail/api/reference/quota)
