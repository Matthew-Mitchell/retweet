
from pymongo import MongoClient
from urlparse import urlparse
import re

# Set up database access
#uri = 'mongodb://52.33.180.219'
#client = MongoClient(host=uri)
client = MongoClient()
db = client.retweets

accounts = ['@donlemon', '@kanyewest', '@realDonaldTrump', '@JusticeWillett', '@IAmSteveHarvey', '@juliaioffe',
            '@ForecasterEnten', '@wikileaks', '@pescami', '@TheFix',
            '@ggreenwald', '@ezraklein', '@mattyglesias', '@brianstelter', '@thegarance', '@DianeSawyer', '@jbarro',
            '@jaketapper', '@sullydish', '@camanpour', '@nycjim', '@mikeallen', '@chriscuomo', '@lawrence',
            '@donnabrazile', '@bretbaier', '@tuckercarlson', '@wolfblitzer', '@jmartnyt', '@markos', '@anamariecox',
            '@glennbeck', '@morningmika', '@secupp', '@brithume', '@thereval', '@nytimeskrugman', '@dylanbyers',
            '@maddow', '@mitchellreports', '@ariannahuff', '@norahodonnell', '@howardkurtz', '@jonkarl',
            '@markhalperin', '@jeffreygoldberg', '@ahmalcolm', '@costareports', '@larrysabato',
            '@teamcavuto', '@natesilver538', '@buzzfeedben', '@samsteinhp', '@billkeller2014', '@krauthammer',
            '@daveweigel', '@stephenfhayes', '@mollyesque', '@joenbc', '@joshtpm', '@jdickerson', '@davidcorndc',
            '@williegeist', '@andersoncooper', '@drudge', '@jonahnro', '@anncoulter', '@greta', '@monicacrowley',
            '@greggutfeld', '@mkhammer', '@edhenry', '@dloesch', '@michellemalkin', '@kirstenpowers', '@davidfrum',
            '@megynkelly', '@dleonhardt', '@rbreich', '@rickklein', '@charlesmblow', '@marcambinder',
            '@peggynoonannyc', '@katrinanation', '@anncurry', '@nickkristof', '@borowitzreport', '@tomfriedman',
            '@mharrisperry', '@ktumulty', '@markleibovich', '@markknoller', '@danaperino', '@blakehounshell',
            '@nickconfessore', '@ericbolling', '@mtaibbi', '@judgenap', '@seanhannity', '@fareedzakaria',
            '@kimguilfoyle', '@ryanlizza', '@ewerickson', '@hardball_chris', '@politicalwire', '@maggienyt',
            '@chucktodd', '@chrislhayes', '@gstephanopoulos', '@richlowry', '@majorcbs', '@oreillyfactor']

accounts1 = ['@morningmika', '@secupp', '@brithume', '@thereval', '@nytimeskrugman', '@dylanbyers',
            '@maddow', '@mitchellreports', '@ariannahuff', '@norahodonnell', '@howardkurtz', '@jonkarl',
            '@markhalperin', '@jeffreygoldberg', '@ahmalcolm', '@costareports', '@larrysabato',
            '@teamcavuto', '@natesilver538', '@buzzfeedben', '@samsteinhp', '@billkeller2014', '@krauthammer',
            '@daveweigel', '@stephenfhayes', '@mollyesque', '@joenbc', '@joshtpm', '@jdickerson', '@davidcorndc',
            '@williegeist', '@andersoncooper', '@drudge', '@jonahnro', '@anncoulter', '@greta', '@monicacrowley',
            '@greggutfeld', '@mkhammer', '@edhenry', '@dloesch', '@michellemalkin', '@kirstenpowers', '@davidfrum',
            '@megynkelly', '@dleonhardt', '@rbreich', '@rickklein', '@charlesmblow', '@marcambinder',
            '@peggynoonannyc', '@katrinanation', '@anncurry', '@nickkristof', '@borowitzreport', '@tomfriedman',
            '@mharrisperry', '@ktumulty', '@markleibovich', '@markknoller', '@danaperino', '@blakehounshell',
            '@nickconfessore', '@ericbolling', '@mtaibbi', '@judgenap', '@seanhannity', '@fareedzakaria',
            '@kimguilfoyle', '@ryanlizza', '@ewerickson', '@hardball_chris', '@politicalwire', '@maggienyt',
            '@chucktodd', '@chrislhayes', '@gstephanopoulos', '@richlowry', '@majorcbs', '@oreillyfactor']


class Tweet:
    def __init__(self, tweet, source='', source_id=''):
        self.meta = {'id_str': tweet['id_str'], 'created_at': tweet['created_at']}
        self.source = {'collection': source, 'id': source_id}
        self.get_type(tweet)
        self.get_contents(tweet)
        self.original = None

    # Find out what kind of tweet it is
    def get_type(self, tweet):
        tweet_type = 'bad'
        if tweet['is_quote_status']:
            if 'quoted_status' in tweet:
                tweet_type = 'quote'
            elif 'retweeted_status' in tweet:
                tweet_type = 'retweet'
        elif tweet['in_reply_to_status_id']:
            tweet_type = 'reply'
        else:
            if tweet['entities']['user_mentions']:
                tweet_type = 'tweetat'
            else:
                tweet_type = 'tweet'
        self.type = tweet_type

    def get_original(self, tweet):
        if self.type == 'quote':
            self.original = Tweet(tweet['quoted_status']).__dict__
        elif self.type == 'retweet':
            self.original = Tweet(tweet['retweeted_status']).__dict__
        elif self.type == 'reply':
            orig_id = tweet['in_reply_to_status_id_str']
            self.original = orig_id

    def get_contents(self, tweet):
        # Content is stored in 'entities'
        entities = tweet['entities']

        # Initialize text
        text = {'original': tweet['text'], 'processed': tweet['text']}

        # Handle Hashtags
        hashtags = [h['text'] for h in entities['hashtags']]

        # Handle user_mentions
        user_mentions = entities['user_mentions']

        # Handle Media
        if 'media' in entities:
            media = entities['media']
            for m in media:
                text['processed'] = text['processed'].replace(m['url'], ' ')
        else:
            media = []

        # get user data
        user = get_user(tweet)

        # Handle URLS
        # url = urllib2.urlopen(url).url
        links = []
        for url_orig in entities['urls']:
            raw_url = url_orig['expanded_url']
            link = {'url': raw_url}
            text['processed'] = text['processed'].replace(url_orig['url'], ' ')
            url_parts = urlparse(raw_url)
            if url_parts.hostname == 'twitter.com':
                continue
            elif url_parts.hostname == 't.co':
                print "t.co link found.  it shouldn't be here."
                continue
            else:
                link['domain'] = url_parts.hostname
                links.append(link)
            link_path = url_parts.path

        # Do final formatting
        text['processed'] = re.sub('\s+', ' ', text['processed']).strip()

        # Save results
        self.contents = {'text': text, 'links': links, 'media': media, 'user_mentions': user_mentions,
                         'hashtags': hashtags, 'user': user}

        # Format text for easy tokenization


punct_space = '.,%\^&\*:;=`~\?'
punct_lspace = '@#'
punct_rem = '{}()\/'


def text_format(text):
    # Special case: ampersand
    s = text.replace('&amp;', '&')

    # Handle punctuation
    s = re.sub("([%s])" % punct_rem, ' ', s)
    s = re.sub("([%s])" % punct_lspace, r' \1', s)
    s = re.sub("([%s])" % punct_space, r' \1 ', s)
    # s = re.sub('\s{2,}', ' ', s) # another way to remove spaces

    # Special case: ...
    s = s.replace('.  .', '..')
    s = s.replace('.  .', '..')

    # get rid of extra whitespace
    s = re.sub('\s+', ' ', s).strip()

    return s


# Get data about user
def get_user(tweet):
    user_data = tweet['user']
    entry = dict()

    # Things that should NOT get included in the model
    entry['id_str'] = user_data['id_str']
    entry['screen_name'] = user_data['screen_name']

    # Things that should be important
    entry['statuses_count'] = user_data['statuses_count']
    entry['verified'] = user_data['verified']
    entry['followers_count'] = user_data['followers_count']
    entry['friends_count'] = user_data['friends_count']
    entry['favourites_count'] = user_data['favourites_count']
    entry['default_profile'] = user_data['default_profile']
    entry['default_profile_image'] = user_data['default_profile_image']

    # Things that I'm including for the hell of it
    entry['geo_enabled'] = user_data['geo_enabled']
    # entry['has_extended_profile'] = user_data['has_extended_profile']
    entry['protected'] = user_data['protected']
    entry['utc_offset'] = user_data['utc_offset']
    entry['lang'] = user_data['lang']

    # Description
    (entry['profile_words'], entry['profile_hashtags'], entry['profile_handles']) = analyze_description(
        user_data['description'])

    return entry


def analyze_description(desc):
    nwords = len(desc.split())
    nhash = len(re.findall('#\w+', desc))
    nhand = len(re.findall('@\w+', desc))
    return (nwords, nhash, nhand)


def process_all_tweets(ctype, accounts):
    print "processing %s" % (ctype)

    print '_'.join([ctype, 'processed'])
    target_collection = db['_'.join([ctype, 'processed'])]
    # target_collection.drop()

    total_count = 0
    num_stored = 0
    num_bad = 0
    for screen_name in accounts:
        num_user_stored = 0

        # Access collection
        cname = '_'.join([screen_name[1:], ctype])
        coll = db[cname]

        for tweet in coll.find():
            # Get tweet data
            proc_tweet = Tweet(tweet, source=cname, source_id=tweet['_id'])
            # Skip bad tweets
            if proc_tweet.type == 'bad':
                num_bad += 1
                continue
            # Get original if this is a response tweet
            proc_tweet.get_original(tweet)

            # Store result
            tostore = proc_tweet.__dict__
            # if not target_collection.find({'meta.id_str': tostore['meta']['id_str']}).count():
            target_collection.insert_one(tostore)
            num_user_stored += 1
        print "%-18s: %d stored" % (screen_name, num_user_stored)
        num_stored += num_user_stored
        total_count += coll.count()

    print "Total number of tweets: %d" % (total_count)
    print "%d Stored, %d bad" % (num_stored, num_bad)
    print "Total %d stored" % target_collection.count()


process_all_tweets('tweets', accounts1)
print ''
process_all_tweets('tweetsat', accounts)
print ''
