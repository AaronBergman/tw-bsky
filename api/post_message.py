from http.server import BaseHTTPRequestHandler
import json
from atproto import Client as BlueskyClient
import tweepy
import os

def setup_bluesky():
    client = BlueskyClient()
    client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_PASSWORD'))
    return client

def setup_twitter():
    return tweepy.Client(
        consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
        consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
    )

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get content length and read the body
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        try:
            # Parse the body
            data = json.loads(body)
            message = data.get('message', '')

            if not message:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Message cannot be empty."}).encode())
                return

            # Initialize clients for each request
            bluesky_client = setup_bluesky()
            twitter_client = setup_twitter()

            # Post message to platforms
            response = {"bluesky": False, "twitter": False}

            try:
                if bluesky_client:
                    bluesky_client.send_post(text=message)
                    response["bluesky"] = True
            except Exception as e:
                response["bluesky_error"] = str(e)

            try:
                if twitter_client:
                    twitter_response = twitter_client.create_tweet(text=message)
                    response["twitter"] = True
                    response["twitter_link"] = f"https://twitter.com/user/status/{twitter_response.data['id']}"
            except Exception as e:
                response["twitter_error"] = str(e)

            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            # Handle any unexpected errors
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
