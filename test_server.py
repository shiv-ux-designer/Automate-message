#!/usr/bin/env python3
"""
Test script for the webhook server
Run this to test if your webhook server is working correctly
"""

import requests
import json

# Server configuration
SERVER_URL = "http://localhost:5000"

def test_home_endpoint():
    """Test the home endpoint"""
    print("Testing home endpoint...")
    try:
        response = requests.get(f"{SERVER_URL}/")
        if response.status_code == 200:
            print("✅ Home endpoint working!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing home endpoint: {e}")

def test_webhook_verification():
    """Test webhook verification endpoint"""
    print("\nTesting webhook verification...")
    try:
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'my_webhook_verify_token_123',
            'hub.challenge': 'test_challenge'
        }
        response = requests.get(f"{SERVER_URL}/webhook", params=params)
        if response.status_code == 200:
            print("✅ Webhook verification working!")
            print(f"Challenge response: {response.text}")
        else:
            print(f"❌ Webhook verification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing webhook verification: {e}")

def test_message_processing():
    """Test message processing endpoint"""
    print("\nTesting message processing...")
    try:
        # Simulate Facebook webhook payload
        test_data = {
            "object": "page",
            "entry": [
                {
                    "id": "test_page_id",
                    "time": 1234567890,
                    "messaging": [
                        {
                            "sender": {"id": "test_user_id"},
                            "recipient": {"id": "test_page_id"},
                            "timestamp": 1234567890,
                            "message": {
                                "mid": "test_message_id",
                                "text": "Hello, I want to order a red shirt"
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            f"{SERVER_URL}/webhook",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Message processing working!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Message processing failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error testing message processing: {e}")

def test_test_endpoint():
    """Test the test endpoint"""
    print("\nTesting test endpoint...")
    try:
        test_data = {
            "message": "Hello, I want to order a red shirt",
            "user_id": "test_user_123"
        }
        
        response = requests.post(
            f"{SERVER_URL}/test",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test endpoint working!")
            print(f"Input: {result.get('input')}")
            print(f"Output: {result.get('output')}")
            print(f"User ID: {result.get('user_id')}")
        else:
            print(f"❌ Test endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error testing test endpoint: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting webhook server tests...")
    print(f"Server URL: {SERVER_URL}")
    print("=" * 50)
    
    test_home_endpoint()
    test_webhook_verification()
    test_message_processing()
    test_test_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Make sure your Langflow server is running")
    print("2. Update the workflow ID in app.py")
    print("3. Get Facebook page access token")
    print("4. Deploy to a hosting service like Render")

if __name__ == "__main__":
    main() 