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
table = dynamodb.Table('TelegramUsers')

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
    try:
        local_part = (email_address or '').split('@')[0]
        parts = local_part.split('_')
        if len(parts) >= 2 and parts[0] == 'user':
            return parts[1]
    except Exception:
        pass
    return None

def get_user_data(telegram_user_id):
    try:
        resp = table.get_item(Key={'telegram_user_id': telegram_user_id})
        return resp.get('Item')
    except Exception as e:
        logger.error(f"Error getting user data: {str(e)}")
        return None

def generate_email_summary(subject, body):
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
        r = requests.post('https://openai.is238.upou.io/v1/chat/completions', headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
        logger.error(f"OpenAI API error: {r.status_code} {r.text}")
        return f"Summary: {subject}"
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"Summary: {subject}"

def send_telegram_message(user_id, message):
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
    try:
        table.update_item(
            Key={'telegram_user_id': telegram_user_id},
            UpdateExpression='SET last_email_received = :ts',
            ExpressionAttributeValues={':ts': datetime.now().isoformat()}
        )
    except Exception as e:
        logger.error(f"Error updating user timestamp: {str(e)}")
