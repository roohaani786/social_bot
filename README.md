# social_bot
A Telegram Bot capable of posting and pushing your posts to Reddit, Twitter (Threads or Normal) and Facebook smoothly using a Telegram Group

pip install python-telegram-bot==20.7
pip install praw==7.7.1
pip install facebook-sdk
pip install dotenv


## Set up Telegram Bot

* Go to BotFather (Search on Telegram search) and create a new Bot
* Now Set Bot group privacy to disable using BotFather
* Add that Bot to your Group and make it as an admin

## Creating your Telegram Application

https://core.telegram.org/api/obtaining_api_id

## Set up Reddit Config and create an App

https://old.reddit.com/prefs/apps/

## Set up Facebook app

Create an app on https://developers.facebook.com/
Give this app the Facebook Page permission 'pages_read_engagement,pages_manage_posts'
Also Add the facebook Login Product to this app

### Graph API explorer for testing the app & also generating SHORT_LIVED_TOKEN

But Use a Long Lived Token on the script( Use a Page AccessToken to test the Graph API)

https://developers.facebook.com/tools/explorer

def exchange_for_long_lived_token(short_lived_token, app_id, app_secret):
    # Make a request to the Facebook Graph API to exchange the token
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_lived_token,
    }

Then use this long token if you don't want the token to expire frequently to outlive token to as long as 60 Days

# Use python3 telegram_to_reddit.py to run the script

### Create an Issue on the repo if there are any issues or you need help :)

