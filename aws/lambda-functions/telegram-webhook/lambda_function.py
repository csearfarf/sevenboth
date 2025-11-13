# lambda_function.py
import os
import json
import base64
import logging
import random
import string
from datetime import datetime

import boto3
import requests

# ----- logging -----
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ----- aws resources -----
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TelegramUsers')

# ----- env -----
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']  # must be set in Lambda env

# =========================
# Entry
# =========================
def lambda_handler(event, context):
    try:
        logger.info(f"RAW EVENT: {json.dumps(event)[:2000]}")

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

        message = body.get('message')
        if not message:
            # Ignore non-message updates (callbacks, edited_message, etc.)
            logger.info("No 'message' in update; returning 200.")
            return _ok()

        chat_id = str(message.get('chat', {}).get('id'))
        text = (message.get('text') or '').strip()

        logger.info(f"Received message from {chat_id}: {text}")

        if text.startswith('/'):
            response_text = handle_command(text, chat_id)
        else:
            response_text = "Use /start to see available commands."

        if response_text and chat_id:
            send_response(chat_id, response_text)

        return _ok()

    except Exception as e:
        logger.exception(f"Webhook error: {e}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}


def _ok():
    return {'statusCode': 200, 'body': 'OK'}

# =========================
# Commands
# =========================
def handle_command(command, chat_id):
    cmd = command.lower().strip()
    if cmd == '/start':
        return handle_start_command(chat_id)
    if cmd == '/register':
        return handle_register_command(chat_id)
    if cmd == '/status':
        return handle_status_command(chat_id)
    if cmd == '/deactivate':
        return handle_deactivate_command(chat_id)
    if cmd == '/help':
        return handle_help_command()
    return "Unknown command. Use /help."

def handle_start_command(chat_id):
    return (
        "Welcome to Email Summary Bot!\n\n"
        "Commands:\n"
        "/register – Create your unique email address\n"
        "/status – Check your email address and status\n"
        "/deactivate – Disable email forwarding\n"
        "/help – Show help\n\n"
        "Flow:\n"
        "1) /register to get an address\n"
        "2) Use that address anywhere\n"
        "3) Summaries arrive here"
    )

def handle_register_command(chat_id):
    try:
        resp = table.get_item(Key={'telegram_user_id': chat_id})
        if 'Item' in resp and resp['Item'].get('status') == 'active':
            return f"You already have an active email: {resp['Item']['email_address']}"

        email_address = generate_email_address(chat_id)
        table.put_item(Item={
            'telegram_user_id': chat_id,
            'email_address': email_address,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_email_received': None
        })

        return (
            "Email created.\n\n"
            f"Your address: {email_address}\n\n"
            "Give this address to services you want summarized.\n"
            "Use /status to view details."
        )

    except Exception as e:
        logger.error(f"/register error for {chat_id}: {e}")
        return "Error creating email. Try again later."

def handle_status_command(chat_id):
    try:
        resp = table.get_item(Key={'telegram_user_id': chat_id})
        if 'Item' not in resp:
            return "You don't have an email yet. Use /register."

        u = resp['Item']
        created = (u.get('created_at') or 'Unknown')[:19]
        last = u.get('last_email_received') or 'Never'
        if last and last != 'Never':
            last = last[:19]

        return (
            "Your Email Status\n\n"
            f"Email: {u['email_address']}\n"
            f"Status: {u['status'].title()}\n"
            f"Created: {created}\n"
            f"Last Email: {last}"
        )

    except Exception as e:
        logger.error(f"/status error for {chat_id}: {e}")
        return "Error retrieving status. Try again later."

def handle_deactivate_command(chat_id):
    try:
        resp = table.get_item(Key={'telegram_user_id': chat_id})
        if 'Item' not in resp:
            return "No email to deactivate."

        table.update_item(
            Key={'telegram_user_id': chat_id},
            UpdateExpression='SET #s = :inactive',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':inactive': 'inactive'}
        )
        return "Email deactivated. Use /register to reactivate."

    except Exception as e:
        logger.error(f"/deactivate error for {chat_id}: {e}")
        return "Error deactivating email. Try again later."

def handle_help_command():
    return "Commands: /start /register /status /deactivate /help"

# =========================
# Helpers
# =========================
def generate_email_address(telegram_user_id):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"user_{telegram_user_id}_{suffix}@csearfarf.dev"

def send_response(chat_id, text):
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
