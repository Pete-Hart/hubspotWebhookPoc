from flask import Flask, request, jsonify, redirect, session
import requests
import time
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Load environment variables
load_dotenv()

APP_ID = os.getenv('APP_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'

# In-memory storage for tokens (Replace this with persistent storage in a production app)
token_store = {}

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/webhook', methods=['POST'])
def hubspot_webhook():
    data = request.json
    # Process the webhook data here
    print(data)  # For debugging purposes - remove in prod
    return jsonify({'status': 'success'}), 200


@app.route('/oauth-callback', methods=['GET'])
def oauth_callback():
    authorization_code = request.args.get('code')

    if not authorization_code:
        return 'Authorization code not provided', 400

    form_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': authorization_code
    }

    try:
        response = requests.post(TOKEN_URL, data=form_data)
        response.raise_for_status()
        token_data = response.json()

        # Store the tokens and their expiry
        token_store['access_token'] = token_data.get('access_token')
        token_store['refresh_token'] = token_data.get('refresh_token')
        token_store['expires_at'] = time.time() + token_data.get('expires_in', 1800)

        return jsonify({
            'access_token': token_store['access_token'],
            'refresh_token': token_store['refresh_token'],
            'expires_in': token_data.get('expires_in')
        })

    except requests.RequestException as e:
        return f'Error during token exchange: {str(e)}', 500


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in token_store:
        return 'No refresh token available', 400

    refresh_token = token_store['refresh_token']
    form_data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token
    }

    try:
        response = requests.post(TOKEN_URL, data=form_data)
        response.raise_for_status()
        token_data = response.json()

        # Update tokens and expiry
        token_store['access_token'] = token_data.get('access_token')
        token_store['expires_at'] = time.time() + token_data.get('expires_in', 1800)

        return jsonify({
            'access_token': token_store['access_token'],
            'expires_in': token_data.get('expires_in')
        })

    except requests.RequestException as e:
        return f'Error during token refresh: {str(e)}', 500


