import os
import sys
import logging
from telegram.ext import Application, MessageHandler, CommandHandler, filters
import praw
import facebook
import requests
import tweepy
from textwrap import wrap
from dotenv import load_dotenv  # Add this import for managing environment variables

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API keys and tokens from environment variables
API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TEST_TELEGRAM_CHAT_ID = os.getenv("TEST_TELEGRAM_CHAT_ID")
REDDIT_SUBREDDIT = os.getenv("REDDIT_SUBREDDIT")
FACEBOOK_PERMISSIONS = os.getenv("FACEBOOK_PERMISSIONS")

# Use the access token directly
short_lived_token = os.getenv("SHORT_LIVED_TOKEN")

# Flag to control polling state
is_polling = True

# ... Rest of your code remains unchanged ...

# Set up Reddit instance
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent=REDDIT_USER_AGENT,
)

def exchange_for_long_lived_token(short_lived_token, app_id, app_secret):
    # Make a request to the Facebook Graph API to exchange the token
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_lived_token,
    }

    response = requests.get('https://graph.facebook.com/v13.0/oauth/access_token', params=params)
    data = response.json()

    if 'access_token' in data:
        long_lived_token = data['access_token']
        print(f'Long-Lived Token: {long_lived_token}')
        return long_lived_token
    else:
        print(f'Failed to exchange token. Error: {data.get("error", "Unknown error")}')
        return None

# Function to post a message to the specified subreddit
async def post_to_subreddit(subreddit_name, title, content):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit(title, selftext=content)
        print(f"Successfully posted to r/{subreddit_name}: {submission.url}")
        return submission.url
    except Exception as e:
        print(f"An error occurred while posting to Reddit: {e}")
        return None

# Function to post a message to the specified Facebook page
async def post_to_facebook(message):
    try:
        # Use the App ID, App Secret, and Page ID to obtain a page access token
        # graph = facebook.GraphAPI(access_token=f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}")
        graph = facebook.GraphAPI(access_token= f"{short_lived_token}")

        # zootoken = exchange_for_long_lived_token(short_lived_token, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
        
        # Post to the Facebook page
        graph.put_object(FACEBOOK_PAGE_ID, "feed", message=message)
        print("Successfully posted to Facebook.")
    except Exception as e:
        print(f"An error occurred while posting to Facebook: {e}")

def split_content(content, max_words):
    # Split content into chunks based on max_words
    words = content.split()
    content_chunks = [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
    return content_chunks

# Function to post content on Twitter
def post_to_twitter(content):
    try:
        # Authenticate to Twitter
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET_KEY,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        # auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        # auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        # api = tweepy.API(auth, wait_on_rate_limit=True)

        # Check if content length exceeds 25 words
        if len(content.split()) > 100:
            # Split content into threads
            threads = [content[i:i + 100] for i in range(0, len(content.split()), 100)]
            # Initialize variable to store the original tweet ID
            # Post each thread as a reply to the previous tweet
            previous_tweet_id = None

            for i, thread in enumerate(threads, start=1):
                tweet = f"{thread} ({i}/{len(threads)})\n#dailydeals #amazonsale #offersplox"
                
                # If it's the first tweet in the thread, create a new tweet
                if i == 1:
                    tweet_response = client.create_tweet(text=tweet)
                    previous_tweet_id = tweet_response.data['id']
                else:
                    # If it's not the first tweet, reply to the previous tweet
                    tweet_response = client.create_tweet(text=tweet, in_reply_to_tweet_id=previous_tweet_id)
                    previous_tweet_id = tweet_response.data['id']
                
                # Extract the ID from the response
                new_tweet_id = tweet_response.data['id']

                print(f"Tweet posted: {tweet}, Tweet ID: {new_tweet_id}")

        else:
            # Post entire content as a single tweet
            tweet = f"{content}\n\n#dailydeals #amazonsale #offersplox"
            client.create_tweet(text=tweet)
            print(f"Tweet posted: {tweet}")

        print("Successfully posted to Twitter.")
    except Exception as e:
        print(f"An error occurred while posting to Twitter: {e}")
# Set up Telegram application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Define the handler function for incoming messages
async def handle_messages(update, context):
    try:
        print("In try")
        message = update.message
        chat_id = message.chat_id
        print(chat_id)

        # Check if the message has any media attachments
        if message.photo or message.document or message.video or message.audio or message.voice:
            # Ignore messages with media attachments
            print(f"Ignored message with media in chat: {chat_id}")
            return

        # Check if the message is from the specified chat
        if is_polling:
            if chat_id != TEST_TELEGRAM_CHAT_ID:
                # Get the message text
                msg_text = message.text

                # Do something with the message text (in this case, print it)
                print(f"Received message: {msg_text}")

                # Post the message to the specified subreddit
                subreddit_name = REDDIT_SUBREDDIT
                title = 'Deal of the hour'


                # Post Twitter thread
                post_to_twitter(msg_text)

                submission_url = await post_to_subreddit(subreddit_name, title, msg_text)
                await post_to_facebook(msg_text)
            

                # Send a response to the Telegram chat
                if submission_url:
                    response_text = f"Message posted to Reddit! Submission URL: {submission_url}, Twitter And also to Facebook"
                else:
                    print(submission_url)
                    response_text = "Failed to post message to Reddit."

                # await context.bot.send_message(chat_id, text=response_text)

    except Exception as e:
        # Handle exceptions and log them
        logging.error(f"An error occurred: {e}")
        await context.bot.send_message(chat_id, text="An error occurred while processing the message.")

# Register the message handler for handling typing actions
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typing))
# Register the message handler
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))



# Define the command to start polling
async def start_polling(update, context):
    global is_polling
    if not is_polling:
        is_polling = True
        await context.bot.send_message(update.message.chat_id, text="Polling started.")

        await application.run_polling()

        # Schedule the polling to stop after 10 seconds
        await asyncio.sleep(5)
        context.bot_data["restart"] = True
        context.application.stop_running()

# Register the command handler to start polling
# application.add_handler(CommandHandler("startpolling", start_polling))

# Define the command to stop polling
async def stop_polling(update, context):
    global is_polling
    if is_polling:
        is_polling = False
        await context.bot.send_message(update.message.chat_id, text="Polling stopped.")
        context.bot_data["restart"] = True
        context.application.stop_running()

# Register the command handler to stop polling
# application.add_handler(CommandHandler("stoppolling", stop_polling))


# Start the bot without running the event loop here
if __name__ == "__main__":
    application.run_polling()
# Start the bot
# application.bot_data["restart"] = False
# application.run_polling()
# if application.bot_data["restart"]:
#     os.execl(sys.executable, sys.executable, *sys.argv)


