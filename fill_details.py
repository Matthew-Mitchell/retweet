# Set up function to get the text of a tweet

# Set up database access
from pymongo import MongoClient
#uri = 'mongodb://52.33.180.219'
#client = MongoClient(host=uri)
client = MongoClient()
db = client.retweets
db.donlemon_retweets.count()


import cnfg
import tweepy
from tweet_content import get_content

config = cnfg.load(".twitter_config")
auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
auth.set_access_token(config["access_token"], config["access_token_secret"])
api=tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_delay=5*60, retry_count=5)


def get_status_data(tweet):
    if 'quoted_status' in tweet['retweet']:
        tweeter_data = tweet['retweet']['quoted_status']['user']
        status_data = tweet['retweet']['quoted_status']
        rt_type = 'quoted'
    else:
        tweeter_data = tweet['retweet']['retweeted_status']['user']
        status_data = tweet['retweet']['retweeted_status']
        rt_type = 'retweeted'
    # print '%s %s: %s'%(rt_type, tweet['tweeter'], text)
    return status_data


collection = db['tweets_formatted']
# collection.drop()


print "Collecting set of tweets"
reporters = ['@donlemon', '@juliaioffe', '@ForecasterEnten', '@pescami', '@TheFix', '@ggreenwald',
                 '@ezraklein', '@mattyglesias', '@brianstelter', '@thegarance', '@DianeSawyer', '@jbarro']

MAX_TO_DO = 150

reporter_retweets = []
for user in reporters:
    retweets = [rt for rt in db[user[1:] + '_retweets'].find() if 'is_quote_status' in rt['retweet']]
    retweets = [s for s in retweets if s['retweet']['is_quote_status']]
    retweets = [rt for rt in retweets if not collection.find({'id': get_status_data(rt)['id']}).count()]
    reporter_retweets += retweets

    if len(reporter_retweets) >= MAX_TO_DO:
        break

reporter_retweets = reporter_retweets[:MAX_TO_DO]
print "Filling in %d tweets"%len(reporter_retweets)

# Fill in the tweets
tweets_expanded = []
tweets_formatted = []
succ = 0
done = 0
fail = 0

for tweet in reporter_retweets:
    status_data = get_status_data(tweet)
    text = status_data['text']

    if not collection.find({'id': status_data['id']}).count():
        try:
            text_expanded = get_content(api, text)
        except:
            entry = {'id': status_data['id'], 'failed': 1}
            collection.insert_one(entry)
            fail += 1
            continue
        tweets_expanded.append(text_expanded)
        entry = {'id': status_data['id'], 'original': text, 'expanded': text_expanded}
        collection.insert_one(entry)
        succ += 1
    else:
        done += 1
print "(%d / %d / %d)" % (succ, fail, collection.count())


# status_data.keys()