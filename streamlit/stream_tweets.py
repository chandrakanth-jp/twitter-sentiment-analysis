"""
enables access to real-time tweets using Twitter API
"""
import json
import time
import tweepy
import pymongo
from decouple import config 
from kafka import KafkaProducer

def auth():
    """Autheticate user's Twitter API keys"""
    try:
        oauth = tweepy.OAuthHandler(config("API_KEY"), config("API_SEC"))
        oauth.set_access_token(config("ACS_TOK"), config("ACS_TOK_SEC"))
        api = tweepy.API(oauth, wait_on_rate_limit=True)
    except tweepy.TweepError:
        print("API authentication error!")
    
    return api


class MyStreamListener(tweepy.StreamListener):
    """
    Class for streaming tweets and sending to Kafka broker.

    Attributes
    ----------
    keywords: str
            list of keywords to search
    database: MongoClient instance

    collection: str
            name of collection
    """

    def __init__(self, keywords, collection, bootstrap_server):
        self.msg_key = keywords+':'+collection
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server, key_serializer=lambda x: x.encode(), value_serializer=lambda x: json.dumps(x).encode('utf-8'))
        
        super().__init__()

    def on_data(self, data):
        #text = json.loads(data).encode('utf-8')
        try:
            self.producer.send('tweets', value=data, key=self.msg_key)
            #self.producer.send('tweets', value=data)
        except Exception as e:
            print('Kafka producer exception', e)
            raise 

    def on_error(self, status_code):
        if status_code == 420:
            print('Limit reached, closing stream!')
            time.sleep(5)
            return
        print('Streaming error, status code {})'.format(status_code))
    