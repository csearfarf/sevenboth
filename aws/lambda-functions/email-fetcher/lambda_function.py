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
                key = f"emails/{now.year}/{now.month:02d}/{now.day:02d}/{email_hash}_{int(now.timestamp())}.json"

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
    """Extract text body from email message"""
    body = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get("Content-Disposition") or "")
            if "attachment" in cdisp:
                continue
            if ctype == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
            elif ctype == "text/html" and not body:
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
    return body[:5000]
