import os
import time
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import pymongo
from decouple import config 
from transformers import pipeline

def connect_to_database():
        """connect to MongoDB database"""
        client=pymongo.MongoClient(config('MONGO_ATLAS'))
        return client

db = connect_to_database()[config('DB_NAME')]

class StreamConsumer():
    """
    Collect and preprocess tweets using Kafka Consumer
    """
    def __init__(self, topic):
        self.topic = topic
        self.consumer = KafkaConsumer(self.topic, bootstrap_servers=config('BOOTSTRAP_SERVER'), key_deserializer=lambda x: x.decode(), value_deserializer=lambda x: json.loads(x.decode('utf-8')))
        self.tweet_analyser = pipeline("sentiment-analysis",model="cardiffnlp/twitter-roberta-base-sentiment")

    def trace_keyword(self, message, text):
        """check if keyword is present in the tweet text
        
        Attributes
        ----------
        message: json
            message received from Kafka Producer
        """
        keywords = message.key.split(':')[0].split(',')
        collection =  message.key.split(':')[-1]

        for keyword in keywords:
            if any(word.upper() in text.upper() for word in keyword.split(' ')):
                #print(keyword)
                return keyword, collection
        return None, None 
    
    def preprocess(self,text):
        new_text = []    
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            t = 'http' if t.startswith('http') else t
            new_text.append(t)
        return " ".join(new_text)


    def consume_tweets(self):
        for message in self.consumer:
            tweets = json.loads(message.value)
            if 'user' not in tweets or 'retweeted_status' in tweets:
                continue

            if tweets['truncated']:
                tweet_text = tweets['extended_tweet']['full_text']
            else:
                tweet_text = tweets['text']
            
            processed_text = self.preprocess(tweet_text)

            subject, collection = self.trace_keyword(message, tweet_text)
            if not subject:
                continue

            if tweets['geo']:
                location = tweets['geo']
            else:
                 location = tweets['user']['location']

            created_at = tweets['created_at']  
            userid = tweets['user']['id_str'] 
            followers = tweets['user']['followers_count']
            sentiment = self.tweet_analyser(processed_text)[0]
            tweet_dict = {"id":userid,"created_at":created_at,"text":tweet_text,"location":location,'followers':followers,'subject':subject, 'sentiment':sentiment}
            db[collection].insert_one(tweet_dict)


if __name__ == '__main__':
    topic_name = config('KAFKA_TOPIC')

    admin_client = KafkaAdminClient(bootstrap_servers=config('BOOTSTRAP_SERVER'))

    if not admin_client.list_topics():
        topic_list = []
        topic_list.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))
        admin_client.create_topics(new_topics=topic_list, validate_only=False)

    tweet_consumer = StreamConsumer(topic=topic_name)
    tweet_consumer.consume_tweets()
