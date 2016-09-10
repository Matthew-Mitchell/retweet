
# Set up function to get the text of a tweet

# Set up database access
from pymongo import MongoClient
#uri = 'mongodb://52.33.180.219'
#client = MongoClient(host=uri)
client = MongoClient()
db = client.retweets
print db.realDonalTrump_retweets.count()

import sys
sys.path.insert(1,'/Users/alanschoen/PycharmProjects/RetweetRegression')
import cnfg
import tweepy
import time
import datetime
from dateutil import parser
import pandas as pd
from scipy.interpolate import interp1d
from pytz import timezone

config = cnfg.load(".twitter_config_old")
auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
auth.set_access_token(config["access_token"], config["access_token_secret"])
api=tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_delay=5*60, retry_count=5)

dt_id = [ (parser.parse(t['created_at']), t['id']) for t in db['realDonaldTrump_tweetsat'].find()]


def store_tweets(cursor, db, collection_name):
    count = 0
    for tweet in cursor:
        tweet_dict = tweet._json
        target_colection = db[collection_name]
        if not target_colection.find({'id': tweet.id}).count():
            target_colection.insert_one(tweet_dict)
            count += 1
    return count

def get_ids():
    # I had to replicate all of this because of a mysterious error
    ct = datetime.datetime.now()
    ct_est = timezone('US/Eastern').localize(ct)
    ct_utc = ct_est.astimezone(timezone('UTC'))

    first = ct_est - datetime.timedelta(days=7) + datetime.timedelta(hours=3)
    begin =  datetime.datetime(year=first.year, month=first.month, day=first.day, hour=first.hour, minute=45, tzinfo=first.tzinfo)
    begin_utc = begin.astimezone(timezone('UTC'))
    #(begin - dt_id[0][0]).total_seconds()

    df = pd.DataFrame(dt_id, columns=['time', 'tweet_id'])
    time_since_beginning = map(lambda x: x.total_seconds(), df['time'] - begin_utc)
    tweet_ids = df['tweet_id'].astype(float)
    f = interp1d(time_since_beginning, tweet_ids, 'linear')

    loop_time = begin + datetime.timedelta(0)
    hours = 0

    tids = []
    while loop_time < ct_est:
        # Find closest tweet to tweet id
        first = ct_est - datetime.timedelta(days=7) + datetime.timedelta(hours=9 + hours)
        begin = datetime.datetime(year=first.year, month=first.month, day=first.day, hour=first.hour, minute=45,
                                  tzinfo=first.tzinfo)
        begin_utc = begin.astimezone(timezone('UTC'))
        # (begin - dt_id[0][0]).total_seconds()

        df = pd.DataFrame(dt_id, columns=['time', 'tweet_id'])
        time_since_beginning = map(lambda x: x.total_seconds(), df['time'] - begin_utc)
        tweet_ids = df['tweet_id'].astype(float)

        f = interp1d(time_since_beginning, tweet_ids, kind='linear')
        try:
            tweet_id = long(f(0))
        except:
            break

        tids.append(tweet_id)

        hours += 1
        loop_time = loop_time + datetime.timedelta(hours=1)
    return tids


def do_backfill(screen_name, tids):
    # Test it out

    collection_name = screen_name[1:] + '_tweetsat'
    last_id = None
    nstored = 0
    for tid in tids:
        # Retreive tweets
        tweets = api.search(q=screen_name, count=100, max_id=tid, since_id=last_id)
        last_id = max([t.id for t in tweets])
        nstored += store_tweets(tweets, db, collection_name)
    return nstored


print "Backfilling tweets"
tids = get_ids()

new_users = ['@jaketapper', '@sullydish', '@camanpour', '@nycjim', '@mikeallen', '@chriscuomo', '@lawrence', '@donnabrazile', '@bretbaier', '@tuckercarlson', '@wolfblitzer', '@jmartnyt', '@markos', '@anamariecox', '@glennbeck', '@morningmika', '@secupp', '@brithume', '@thereval', '@nytimeskrugman', '@dylanbyers', '@maddow', '@mitchellreports', '@ariannahuff', '@norahodonnell', '@howardkurtz', '@jonkarl', '@markhalperin', '@jeffreygoldberg', '@ahmalcolm', '@costareports', '@andreatantaros', '@larrysabato', '@teamcavuto', '@natesilver538', '@buzzfeedben', '@samsteinhp', '@billkeller2014', '@krauthammer', '@daveweigel', '@stephenfhayes', '@mollyesque', '@joenbc', '@joshtpm', '@jdickerson', '@davidcorndc', '@williegeist', '@andersoncooper', '@drudge', '@jonahnro', '@anncoulter', '@greta', '@monicacrowley', '@greggutfeld', '@mkhammer', '@edhenry', '@dloesch', '@michellemalkin', '@kirstenpowers', '@davidfrum', '@megynkelly', '@dleonhardt', '@rbreich', '@rickklein', '@charlesmblow', '@marcambinder', '@peggynoonannyc', '@katrinanation', '@anncurry', '@nickkristof', '@borowitzreport', '@tomfriedman', '@mharrisperry', '@ktumulty', '@markleibovich', '@markknoller', '@danaperino', '@blakehounshell', '@nickconfessore', '@ericbolling', '@mtaibbi', '@judgenap', '@seanhannity', '@fareedzakaria', '@kimguilfoyle', '@ryanlizza', '@ewerickson', '@hardball_chris', '@politicalwire', '@maggienyt', '@chucktodd', '@chrislhayes', '@gstephanopoulos', '@richlowry', '@majorcbs', '@oreillyfactor']

for screen_name in new_users:
    print "Starting %s"%screen_name
    nstored = do_backfill(screen_name, tids)
    print "%d stored"%nstored
