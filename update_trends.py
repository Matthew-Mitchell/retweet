import cnfg
import twitter
config = cnfg.load(".twitter_config_whosyodata")

auth = twitter.oauth.OAuth(config["access_token"], config["access_token_secret"],
                           config["consumer_key"], config["consumer_secret"])


# Set up database access
from pymongo import MongoClient
client = MongoClient()
db = client.retweets

WORLD_WOE_ID = 1
US_WOE_ID = 23424977
twitter_api = twitter.Twitter(auth=auth)
world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)[0]
us_trends = twitter_api.trends.place(_id=US_WOE_ID)[0]

db.us_trends.insert_one(us_trends)
db.world_trends.insert_one(world_trends)