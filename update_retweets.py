'''Populate retweets database for each user'''
from harvester import Retweet

# Set up twitter
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


accounts = ['@donlemon', '@kanyewest', '@realDonaldTrump', '@JusticeWillett', '@IAmSteveHarvey', '@juliaioffe',
            '@ForecasterEnten', '@pmarca']

for user in accounts:
    tweets_collection = db[user[1:] + '_tweets']
    succ_count = 0
    fail_count = 0
    for tweet in tweets_collection.find():
        if tweet['is_quote_status']:
            if tweets_collection.find({'id': tweet['id']}).count():
                print 'Tweet already in DB'
                continue
            try:
                rt = Retweet(tweet)
                rt.get_friendship(api)
                rt.get_history(api, 100)
                rt.save(db)
                succ_count += 1
            except:
                fail_count += 1
    print "%s: %d WIN!, %d fail, %d total" % (user, succ_count, fail_count, tweets_collection.count())