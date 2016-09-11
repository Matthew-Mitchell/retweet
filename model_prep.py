# Handle Emoji if necessary
#from unidecode import unidecode

import re


# Helper functions

def get_status_data(tweet):
    if 'quoted_status' in tweet['retweet']:
        tweeter_data = tweet['retweet']['quoted_status']['user']
        status_data = tweet['retweet']['quoted_status']
        rt_type = 'quoted'
    elif 'retweeted_status' in tweet['retweet']:
        tweeter_data = tweet['retweet']['retweeted_status']['user']
        status_data = tweet['retweet']['retweeted_status']
        rt_type = 'retweeted'
    else:
        print "PROBLEM IN get_status_data"
        print tweet['retweet']
    # print '%s %s: %s'%(rt_type, tweet['tweeter'], text)
    return status_data

# Get data about user
def get_user_data_vars(user_data):
    entry = dict()

    # Things that should NOT get included in the model
    entry['user_id_str'] = user_data['id_str']
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
    entry['has_extended_profile'] = user_data['has_extended_profile']
    entry['protected'] = user_data['protected']
    entry['utc_offset'] = user_data['utc_offset']
    entry['lang'] = user_data['lang']

    return entry


def is_surrogate_pair(s,i):
    if 0xD800 <= ord(s[i]) <= 0xDBFF:
        try:
            l = s[i+1]
        except IndexError:
            return False
        if 0xDC00 <= ord(l) <= 0xDFFF:
            return True
        else:
            raise ValueError("Illegal UTF-16 sequence: %r" % s[i:i+2])
    else:
        return False
def find_emoji(s):
    if type(s)==str:
        s = s.decode('UTF-8', 'ignore')
    # s = unidecode(s)
    return [s[i:i+2] for i in range(len(s)-1) if is_surrogate_pair(s, i)]

def rm_emoji(s, emoji):
    for e in emoji:
        s = s.replace(e.encode('UTF-8'), '')
    return s

def space_emoji(s, emoji):
    for e in emoji:
        e = e.encode('UTF-8')
        s = re.sub(e, " %s ".encode('UTF-8')%e, s)
    return s

def separate_emoji(s):
    return ' '.decode('UTF-8').join( [rm_emoji(s, emoji).decode('UTF-8')] + emoji)

def despace(s):
    return re.sub('\s+',' ', s)

punct_space = '.,!$%\^&\*:;=_`~\?'
punct_lspace = '@#'
punct_rem = '{}()\/'
def format_punct(s):
    s = re.sub("([%s])"%punct_rem, ' ', s)
    s = re.sub("([%s])"%punct_lspace, r' \1', s)
    s = re.sub("([%s])"%punct_space, r' \1 ', s)
    s = re.sub('\s{2,}', ' ', s)
    return s

def format_tweet(t):
    emoji = find_emoji(t)
    t = space_emoji(t, emoji)
    t = format_punct(t)
    t = despace(t)
    t = t.lower()
    return t

def process_expanded(expanded_tuples):
    return " ".join([t[1] for t in expanded_tuples])

print format_tweet('(Hey@donlemon, the #agelesswonder#omgwtfbbq http://www.lemon.com/twitter.html)')
expanded_tuples = [[u'TWEET', u'Wait. Just wait. Did @donlemon just nonchalantly say Ali was "very fertile" during his sign off/eulogy? Kind of inappropriate...', 0]]
print process_expanded(expanded_tuples)
print format_tweet(process_expanded(expanded_tuples))