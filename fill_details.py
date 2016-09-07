# Set up function to get the text of a tweet

import re
import urllib2
from newspaper import Article

# Set up database access
from pymongo import MongoClient
#uri = 'mongodb://52.33.180.219'
#client = MongoClient(host=uri)
client = MongoClient()
db = client.retweets
db.donlemon_retweets.count()

re_urls = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
status_url = re.compile('http[s]?://twitter\.com/.*/status/(\d*)')

import cnfg
import tweepy
import time

config = cnfg.load(".twitter_config")
auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
auth.set_access_token(config["access_token"], config["access_token_secret"])
api=tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_delay=5*60, retry_count=5)

def get_status(ids):
    return api.statuses_lookup(ids)


def follow_links(text, depth=0, followed=set()):
    # Make sure we're not on a wild goose chase
    if depth > MAX_DEPTH:
        print 'MAX DEPTH REACHED'
        print text
        return ''

    urls = re.findall(re_urls, text)
    for url in urls:
        text = text.replace(url, '')
    if not urls:
        return text
    else:
        link_texts = []
        for url in urls:
            if 't.co' in urls[0]:
                url = urllib2.urlopen(urls[0]).url
            # print url
            if re.match(status_url, url):
                status_id = long(re.match(status_url, url).groups()[0])

                # Stop if you've already been here
                if status_id in followed:
                    return ''
                followed.update([status_id])

                # print 'Found link to status %s'%status_id
                retrieved_status = get_status([status_id])[0]
                link_text = retrieved_status.text
                link_text = follow_links(link_text, depth + 1, followed)
                link_texts.append(link_text)
            else:
                a = Article(url)
                a.download()
                a.parse()
                link_text = a.title
                link_texts.append(link_text)
                # print 'found link: %s'%link_text
        texts = [text] + link_texts
        return [t for t in texts if t]


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

reporters = ['@donlemon', '@juliaioffe', '@ForecasterEnten', '@pescami', '@TheFix', '@ggreenwald',
                 '@ezraklein', '@mattyglesias', '@brianstelter', '@thegarance', '@DianeSawyer', '@jbarro']

MAX_TO_DO = 100


reporter_retweets = []
reporter_retweet_mentions = []
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
MAX_DEPTH = 10
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
            text_expanded = follow_links(text)
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