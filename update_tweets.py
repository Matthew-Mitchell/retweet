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

from datetime import datetime
print "### Updating tweets at %s"%datetime.now()

accounts = ['@donlemon', '@kanyewest', '@realDonaldTrump', '@JusticeWillett', '@IAmSteveHarvey', '@juliaioffe',
            '@ForecasterEnten', '@pmarca', '@wikileaks', '@joerogan', '@BenedictEvans', '@pescami', '@TheFix',
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

from harvester import TwitterUser
for username in accounts:
    user = TwitterUser(username, api, db)
    user.update_tweetsat(max_tweets_update)
    user.update_tweets(max_tweets_update)
client.close()
print 'Done updating'