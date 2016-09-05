'''Populate retweets database for each user'''
from harvester import Retweet

# Set up twitter
import cnfg
import tweepy
config = cnfg.load(".twitter_config_whosyodata")
auth = tweepy.OAuthHandler(config["consumer_key"],
                           config["consumer_secret"])
auth.set_access_token(config["access_token"],
                      config["access_token_secret"])
api=tweepy.API(auth)

# Set up database
from pymongo import MongoClient
client = MongoClient()
db = client.retweets


from datetime import datetime
print "### Updating retweets at %s"%datetime.now()

accounts = ['@donlemon', '@kanyewest', '@realDonaldTrump', '@JusticeWillett', '@IAmSteveHarvey', '@juliaioffe',
            '@ForecasterEnten', '@pmarca', '@wikileaks', '@joerogan', '@BenedictEvans', '@pescami', '@TheFix',
            '@ggreenwald', '@ezraklein', '@mattyglesias', '@brianstelter', '@thegarance', '@DianeSawyer', '@jbarro']

MAX_RETWEETS = 500

for user in accounts:
    tweets_collection = db[user[1:] + '_tweets']
    retweets_collection = db[user[1:] + '_retweets']
    succ_count = 0
    fail_count = 0
    done_count = 0
    for tweet in tweets_collection.find():
        if tweet['is_quote_status']:
            if retweets_collection.find({'retweet.id': tweet['id']}).count():
                done_count += 1
                continue
            try:
                rt = Retweet(tweet)
                rt.get_friendship(api)
                rt.get_history(api, 100)
                rt.save(db)
                succ_count += 1
            except:
                fail_count += 1
        if succ_count >= MAX_RETWEETS:
            break
    number_stored = retweets_collection.find().count()
    print "%s: %d WIN!, %d fail, %d duplicates, %d in db" % (user, succ_count, fail_count, done_count, number_stored)

client.close()