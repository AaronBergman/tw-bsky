import json
from atproto import Client as BlueskyClient
import tweepy
import os

# Set up Bluesky and Twitter clients
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

bluesky_client = setup_bluesky()
twitter_client = setup_twitter()

def handler(event, context):
    # Parse incoming message
    body = json.loads(event['body'])
    message = body.get('message', '')

    if not message:
        return {"statusCode": 400, "body": json.dumps({"error": "Message cannot be empty."})}

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

    return {"statusCode": 200, "body": json.dumps(response)}
