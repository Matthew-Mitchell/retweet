'''Update tweets and tweetsat database for each user'''

# Set up twitter access
# pip install tweepy
import cnfg
import tweepy
config = cnfg.load(".twitter_config")
auth = tweepy.OAuthHandler(config["consumer_key"],
                           config["consumer_secret"])
auth.set_access_token(config["access_token"],
                      config["access_token_secret"])
api=tweepy.API(auth)

# Set up database
from pymongo import MongoClient
client = MongoClient()
db = client.retweets

# Set max tweets for initialization and update
max_tweets_update=100

accounts = ['@donlemon', '@kanyewest', '@realDonaldTrump', '@JusticeWillett', '@IAmSteveHarvey', '@juliaioffe',
            '@ForecasterEnten', '@pmarca', '@wikileaks', '@joerogan', '@BenedictEvans']

from harvester import TwitterUser
for username in accounts:
    user = TwitterUser(username, api, db)
    user.update_tweetsat(max_tweets_update)
    user.update_tweets(max_tweets_update)
print 'Done updating'


