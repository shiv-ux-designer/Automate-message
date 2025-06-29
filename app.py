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

@app.route('/')
def home():
    """Home endpoint to check if server is running"""
    return jsonify({
        "status": "Webhook server is running!",
        "message": "Facebook/Instagram webhook server for Langflow integration"
    })

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for Facebook/Instagram setup"""
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
    """Handle incoming messages from Facebook/Instagram"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        # Extract message data
        if 'object' in data and data['object'] == 'page':
            for entry in data['entry']:
                for messaging_event in entry['messaging']:
                    if 'message' in messaging_event:
                        # Skip echo messages (sent by the page itself)
                        if 'is_echo' in messaging_event['message'] and messaging_event['message']['is_echo']:
                            logger.info("Skipping echo message.")
                            continue
                        sender_id = messaging_event['sender']['id']
                        message_text = messaging_event['message'].get('text', '')
                        
                        logger.info(f"Processing message from {sender_id}: {message_text}")
                        
                        # Send message to Langflow for processing
                        response = process_message_with_langflow(sender_id, message_text)
                        
                        # Send response back to Facebook
                        send_response_to_facebook(sender_id, response)
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

def process_message_with_langflow(sender_id, message_text):
    """Send message to Langflow and get AI response"""
    try:
        # Prepare data for Langflow
        langflow_data = {
            "input_value": message_text,
            "output_type": "chat",
            "input_type": "chat"
        }
        
        logger.info(f"Sending to Langflow: {langflow_data}")
        
        # Build the Langflow API URL
        url = f"{LANGFLOW_API_URL}/api/v1/run/{LANGFLOW_WORKFLOW_ID}"
        
        # Set headers with Authorization
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LANGFLOW_API_TOKEN}'
        }
        
        # Make request to Langflow API
        response = requests.post(
            url,
            json=langflow_data,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Langflow response: {result}")
            try:
                # Try to extract the AI message from the nested structure
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
    """Send response back to Facebook Messenger"""
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

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint to simulate message processing"""
    try:
        data = request.get_json()
        message = data.get('message', 'Hello!')
        user_id = data.get('user_id', 'test_user')
        
        logger.info(f"Test message: {message} from {user_id}")
        
        # Simulate Langflow processing
        response = f"Test response: I received your message '{message}'"
        
        return jsonify({
            "status": "success",
            "input": message,
            "output": response,
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 
