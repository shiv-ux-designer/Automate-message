# Facebook/Instagram Webhook Server for Langflow

This is a Flask-based webhook server that bridges Facebook/Instagram Messenger with your Langflow AI workflows.

## Features

- ✅ Receives messages from Facebook/Instagram
- ✅ Sends messages to Langflow for AI processing
- ✅ Returns AI responses back to users
- ✅ Webhook verification for Facebook/Instagram setup
- ✅ Error handling and logging
- ✅ Test endpoints for development

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:
- `LANGFLOW_API_URL`: Your Langflow server URL
- `FACEBOOK_VERIFY_TOKEN`: A secret token for webhook verification
- `FACEBOOK_PAGE_ACCESS_TOKEN`: Your Facebook page access token

### 3. Run the Server

**For Development:**
```bash
python app.py
```

**For Production:**
```bash
gunicorn app:app
```

The server will run on `http://localhost:5000`

## API Endpoints

### 1. Home Page
- **URL:** `GET /`
- **Purpose:** Check if server is running
- **Response:** Server status message

### 2. Webhook Verification
- **URL:** `GET /webhook`
- **Purpose:** Facebook/Instagram webhook verification
- **Parameters:** `hub.mode`, `hub.verify_token`, `hub.challenge`

### 3. Message Processing
- **URL:** `POST /webhook`
- **Purpose:** Receive and process messages from Facebook/Instagram
- **Body:** Facebook/Instagram webhook payload

### 4. Test Endpoint
- **URL:** `POST /test`
- **Purpose:** Test message processing without Facebook
- **Body:** `{"message": "Hello", "user_id": "test_user"}`

## Facebook/Instagram Setup

### 1. Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Messenger product to your app

### 2. Configure Webhook
1. In your Facebook app, go to Messenger > Settings
2. Add your webhook URL: `https://your-domain.com/webhook`
3. Set verify token (same as `FACEBOOK_VERIFY_TOKEN` in .env)
4. Subscribe to `messages` events

### 3. Get Page Access Token
1. Create a Facebook page
2. Generate page access token
3. Add to `FACEBOOK_PAGE_ACCESS_TOKEN` in .env

## Langflow Integration

### 1. Create Langflow Workflow
1. Build your AI workflow in Langflow
2. Note your workflow ID
3. Update `your-workflow-id` in `app.py` line 89

### 2. Test Integration
Use the `/test` endpoint to test your Langflow integration:

```bash
curl -X POST http://localhost:5000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I want to order a shirt", "user_id": "test_user"}'
```

## Deployment

### Render (Recommended)
1. Push code to GitHub
2. Connect GitHub to Render
3. Set environment variables in Render dashboard
4. Deploy

### Other Platforms
- Heroku
- Railway
- DigitalOcean
- AWS

## Troubleshooting

### Common Issues

1. **Webhook verification fails**
   - Check `FACEBOOK_VERIFY_TOKEN` matches Facebook app settings
   - Ensure webhook URL is accessible

2. **Messages not received**
   - Verify page access token is correct
   - Check webhook subscription settings
   - Review server logs

3. **Langflow integration fails**
   - Verify `LANGFLOW_API_URL` is correct
   - Check workflow ID in code
   - Ensure Langflow server is running

### Logs
Check server logs for detailed error information:
```bash
tail -f logs/webhook.log
```

## Security Notes

- Keep your access tokens secure
- Use HTTPS in production
- Validate all incoming webhook data
- Implement rate limiting for production use

## Support

For issues or questions, check the logs and ensure all environment variables are correctly set. 