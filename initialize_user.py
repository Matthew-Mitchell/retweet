'''Initialize tweets database for each user'''

# Set up twitter access
# pip install tweepy
import cnfg
import tweepy
config = cnfg.load(".twitter_config_old")
auth = tweepy.OAuthHandler(config["consumer_key"],
                           config["consumer_secret"])
auth.set_access_token(config["access_token"],
                      config["access_token_secret"])
api=tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_delay=3*60, retry_count=6)

# Set up database
from pymongo import MongoClient
client = MongoClient()
db = client.retweets

# Set max tweets for initialization and update
max_tweets_init=5000
max_tweetsat_init=200

# List of twitter accounts to track
accounts = ['@andreatantaros']


from datetime import datetime
print "### Initialising users %s \nat %s"%(str(accounts), datetime.now())


# Clear db if it exists
for username in accounts:
    # Tweets
    collection_name = username[1:] + '_tweets'
    if collection_name in db.collection_names():
        print "Found collection %s.  Deleting..."%collection_name
        db[collection_name].drop()

    # Tweets at
    collection_name = username[1:] + '_tweetsat'
    if collection_name in db.collection_names():
        print "Found collection %s.  Deleting..." % collection_name
        db[collection_name].drop()

# Initialize for each user
from harvester import TwitterUser
for username in accounts:
    user = TwitterUser(username, api, db)
    user.update_tweets(max_tweets_init)
    user.update_tweetsat(max_tweetsat_init)
client.close()
print 'Done initializing'

