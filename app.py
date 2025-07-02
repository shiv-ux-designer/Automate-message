from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import json
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
LANGFLOW_API_URL = os.getenv('LANGFLOW_API_URL', 'http://localhost:3000')
LANGFLOW_WORKFLOW_ID = os.getenv('LANGFLOW_WORKFLOW_ID', '')
LANGFLOW_API_TOKEN = os.getenv('LANGFLOW_API_TOKEN', '')
FACEBOOK_VERIFY_TOKEN = os.getenv('FACEBOOK_VERIFY_TOKEN', 'your_verify_token')
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', '')
INSTAGRAM_PAGE_ACCESS_TOKEN = os.getenv('INSTAGRAM_PAGE_ACCESS_TOKEN', '')

@app.route('/')
def home():
    return jsonify({
        "status": "Webhook server is running!",
        "message": "Facebook/Instagram webhook server for Langflow integration"
    })

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    logger.info(f"Webhook verification request - Mode: {mode}, Token: {token}")
    if mode and token:
        if mode == 'subscribe' and token == FACEBOOK_VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return challenge
        else:
            logger.error("Webhook verification failed!")
            return 'Forbidden', 403
    return 'Bad Request', 400

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")

        # Facebook Messenger
        if 'object' in data and data['object'] == 'page':
            for entry in data['entry']:
                for messaging_event in entry['messaging']:
                    if 'message' in messaging_event:
                        if 'is_echo' in messaging_event['message'] and messaging_event['message']['is_echo']:
                            logger.info("Skipping echo message.")
                            continue
                        sender_id = messaging_event['sender']['id']
                        message_text = messaging_event['message'].get('text', '')
                        logger.info(f"Processing Messenger message from {sender_id}: {message_text}")
                        response = process_message_with_langflow(sender_id, message_text)
                        send_response_to_facebook(sender_id, response)

        # Instagram
        elif 'object' in data and data['object'] == 'instagram':
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change['field'] == 'messages':
                        value = change['value']
                        sender_id = value['from']['id']
                        message_text = value.get('message', '')
                        logger.info(f"Processing Instagram message from {sender_id}: {message_text}")
                        response = process_message_with_langflow(sender_id, message_text)
                        # Instagram API for automated replies is restricted; log the response
                        logger.info(f"Langflow response for Instagram: {response}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

def process_message_with_langflow(sender_id, message_text):
    try:
        langflow_data = {
            "input_value": message_text,
            "output_type": "chat",
            "input_type": "chat"
        }
        logger.info(f"Sending to Langflow: {langflow_data}")
        url = f"{LANGFLOW_API_URL}/api/v1/run/{LANGFLOW_WORKFLOW_ID}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LANGFLOW_API_TOKEN}'
        }
        response = requests.post(
            url,
            json=langflow_data,
            headers=headers,
            timeout=50
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Langflow response: {result}")
            try:
                ai_message = result['outputs'][0]['outputs'][0]['results']['message']['text']
                return ai_message
            except Exception as e:
                logger.error(f"Error extracting AI message: {e}")
                return "Sorry, I could not process your request."
        else:
            logger.error(f"Langflow API error: {response.status_code} - {response.text}")
            return "Sorry, I'm having trouble processing your request right now."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Langflow failed: {str(e)}")
        return "Sorry, I'm temporarily unavailable. Please try again later."
    except Exception as e:
        logger.error(f"Error processing with Langflow: {str(e)}")
        return "Sorry, something went wrong. Please try again."

def send_response_to_facebook(recipient_id, message_text):
    try:
        url = f"https://graph.facebook.com/v18.0/me/messages"
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "access_token": FACEBOOK_PAGE_ACCESS_TOKEN
        }
        response = requests.post(url, json=data, headers=headers, params=params)
        if response.status_code == 200:
            logger.info(f"Message sent successfully to {recipient_id}")
        else:
            logger.error(f"Failed to send message to Facebook: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error sending message to Facebook: {str(e)}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 
