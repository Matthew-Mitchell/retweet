# Set up function to get the text of a tweet

# Set up database access
from pymongo import MongoClient
#uri = 'mongodb://52.37.177.102'
#client = MongoClient(host=uri)
client = MongoClient()
dbp = client.processed
dbr = client.retweets
from newspaper import Article

import sys
sys.path.insert(1,'/Users/alanschoen/PycharmProjects/RetweetRegression')
import cnfg
import time
import pandas as pd

accounts = ['@donlemon', '@juliaioffe',
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

# Create target set
dbm = client.model

# ntarget = 0
# for screen_name in accounts:
#     coll1 = dbp[screen_name[1:] + '_tweets']
#     for tweet in coll1.find({'original': {'$ne': None}, 'original.contents.user_mentions': {'$ne': []}}):
#         if screen_name[1:].lower() in [m['screen_name'].lower() for m in
#                                        tweet['original']['contents']['user_mentions']]:
#             if (not tweet['original']['contents']['user']['verified']) and (
#                 tweet['original']['contents']['user']['followers_count'] < 1000):
#                 ntarget += 1
#             dbm.target.insert_one(tweet)
# print ntarget


# create baseline set.  haven't run yet.

ntarget = 0
for screen_name in accounts:
    coll1 = dbp[screen_name[1:] + '_tweetsat']
    for tweet in coll1.find({'contents': {'$exists': 1}, 'contents.user_mentions': {'$ne': []}}):
        if screen_name[1:].lower() in [m['screen_name'].lower() for m in tweet['contents']['user_mentions']]:
            if  (not tweet['contents']['user']['verified']) and (tweet['contents']['user']['followers_count'] < 1000):
                ntarget += 1
            #dbm.baseline.insert_one(tweet)
print ntarget