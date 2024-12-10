from dotenv import load_dotenv
import os
from datetime import datetime
import requests
import json

load_dotenv("keys.env")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

def get_tweet_details(tweet_id):
    """Fetch the details of a single tweet."""
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    params = {
        "tweet.fields": "conversation_id,author_id,created_at",
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    tweet_data = response.json()
    if "data" not in tweet_data:
        raise ValueError("Failed to fetch tweet details. Please check the Tweet ID or API permissions.")
    return tweet_data

def fetch_replies(conversation_id, next_token=None):
    """Fetch replies to a conversation ID with pagination."""
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": f"conversation_id:{conversation_id}",
        "tweet.fields": "conversation_id,author_id,created_at,in_reply_to_user_id,text",
        "max_results": 100, #maximum allowed
    }
    if next_token:
        params["next_token"] = next_token

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def get_conversation_tree(tweet_id):
    """
    Retrieve the original tweet and replies,
    iterating through paginated results if necessary.
    """
    # Fetch original tweet
    original_tweet = get_tweet_details(tweet_id)
    conversation_id = original_tweet["data"]["conversation_id"]

    # Initialize tree structure
    conversation_tree = {
        "tweet": original_tweet["data"],
        "replies": []
    }

    # Fetch all replies
    next_token = None
    while True:
        replies = fetch_replies(conversation_id, next_token)
        if "data" in replies:
            conversation_tree["replies"].extend(replies["data"])
        next_token = replies.get("meta", {}).get("next_token")
        if not next_token:
            break

    return conversation_tree

def save_to_file(data, tweet_id):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{tweet_id}_{timestamp}.json"
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)
    print(f"Conversation saved to {filename}")


if __name__ == "__main__":
    tweet_id = "1865087597145362656"
    conversation = get_conversation_tree(tweet_id)
    print(json.dumps(conversation, indent=2))
    save_to_file(conversation, tweet_id)