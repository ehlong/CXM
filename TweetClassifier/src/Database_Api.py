import json
import pymongo
from pymongo.collection import Collection
from pymongo.results import BulkWriteResult
import tweepy
import yaml
from datetime import datetime


def connect() -> tweepy.Client:
    """
    Connects to the twitter API, returns the client object

    :rtype: tweepy.Client
    """
    with open('../config/twitter_key.yaml') as file:
        api_key = yaml.safe_load(file)

    twitter = tweepy.Client(api_key['bearer'], api_key['key'], api_key['secret'])
    return twitter


def get_database_collection() -> Collection:
    """
    Connects to the Mongo db atlas cluster, returns the collection object

    :rtype: Collection
    """
    with open('../config/db_key.yaml') as file:
        db_key = yaml.safe_load(file)

    # connect to the database, grab the collection
    client = pymongo.MongoClient(
        f"mongodb+srv://{db_key['user']}:{db_key['password']}"
        f"@cluster0.dxunx.mongodb.net/data?retryWrites=true&w=majority")
    db = client.get_default_database()
    collection = db['tweets']

    return collection


def fetch_all_recent_tweets_from_twitter(latest_id: str) -> [dict]:
    """
    Returns a list of all tweets newer than 7 days that occurred after latest_id

    :param latest_id: The most recent (highest number) id in the database collection
    :return: a list of tweets, each a dictionary of values
    """
    client = connect()

    tweets = []
    next_token = 'first_loop'
    while next_token is not None:
        query = 'to:EpicGames'

        try:
            if next_token == 'first_loop':
                result = client.search_recent_tweets(query=query, max_results=100,
                                                     since_id=latest_id, tweet_fields=['created_at'])
            else:
                result = client.search_recent_tweets(query=query, max_results=100, since_id=latest_id,
                                                     tweet_fields=['created_at'], next_token=next_token)
        except tweepy.errors.BadRequest:
            if next_token == 'first_loop':
                print('Last tweet in DB is from more than 7 days ago, searching last 7 days instead')
                result = client.search_recent_tweets(query=query, max_results=100, tweet_fields=['created_at'])
            else:
                result = client.search_recent_tweets(query=query, max_results=100, tweet_fields=['created_at'],
                                                     next_token=next_token)

        tweets.extend(
            {
                'id': _['id'],
                'text': _['text'],
                'date': _['created_at']
            } for _ in result.data if _['text'][:2] != "RT"
        )

        if 'next_token' in result.meta:
            next_token = result.meta['next_token']
        else:
            next_token = None

    return tweets


def fetch_latest_id(collection: Collection) -> str:
    """
    Returns the most recent (highest number) id in the database collection

    :rtype: str
    :param collection: The mongodb collection object
    :return: an id as a string
    """
    return collection.find().sort("id", pymongo.DESCENDING).limit(1)[0]['id']


def update_collection(collection: Collection, new_values: [dict]) -> BulkWriteResult:
    """
    Updated the given collection with each value in new_values
    This will create a new document in the collection if the document doesn't already exist
    If the document is already in the database, it will update it

    DO NOT EDIT THIS FUNCTION. RISK TO DATABASE INTEGRITY
    BE VERY CAREFUL WHAT YOU PASS TO THIS FUNCTION. IT WILL OVERWRITE DATABASE CONTENTS
    :param collection: A mongodb collection object
    :param new_values: A list of tweets to insert
    :rtype: BulkWriteResult
    :return: A BulkWriteResult object. Contains information about documents upserted, inserted, modified
    """
    requests = []

    # create a new request command for each document in the array
    for document in new_values:
        fields = {
            '$set': {
                'id': document['id'],
                'text': document['text'],
                'date': document['date'],
            }
        }
        if 'class' in document:
            fields['$set']['class'] = document['class']

        requests.append(pymongo.UpdateOne({'id': document['id']}, fields, upsert=True))

    result = collection.bulk_write(requests, ordered=False)
    return result


def fetch_batch_of_unclassified_tweets(collection: Collection, num: int = 0, all: bool = False) -> [dict]:
    """
    Search the database for unclassified tweets
    return num tweets, starting at lowest Id

    :param all: If true, return every unclassified tweet
    :param collection: A mongodb collection object
    :param num: Number of tweets to fetch
    :return: A list of tweets
    """
    query = {'class': {'$exists': False}}
    if all:
        tweets = list(collection.find(query).sort('id', pymongo.ASCENDING))
    else:
        tweets = list(collection.find(query).sort('id', pymongo.ASCENDING).limit(num))
    return tweets

def fetch_all_classified_tweets() -> [dict]:
     """
     Search the database for classified tweets
     return tweets

     :return: A list of tweets
     """
     collection = get_database_collection()
     query = {'class': {'$exists': True}}
     tweets = list(collection.find(query).sort('id', pymongo.ASCENDING))


     return tweets


def fetch_for_manual_classify(collection: Collection, num: int) -> [dict]:
    """
    Fetch num tweets from the collection to manually classify
    Insert a placeholder class for these tweets so that successive calls don't
    return the same tweets during concurrent classifying
    :param collection: A pymongo collection object
    :param num: Number of tweets to fetch
    :return: A list of num tweets
    """
    tweets = fetch_batch_of_unclassified_tweets(collection, num=num)

    # add placeholder class for each tweet
    updates = [x.copy() for x in tweets]
    for update in updates:
        update['class'] = 'being classified'
    update_collection(collection, updates)

    return tweets



def delete_retweets(collection: Collection) -> BulkWriteResult:
    """
    Purge the database of any retweets
    DO NOT EDIT THIS FUNCTION. RISK TO DATABASE INTEGRITY
    :param collection: a mongodb collection object
    :return: result from bulk write. Query for number deleted
    """
    commands = []

    query = {'text': {'$regex': '^RT\\s'}}
    documents = list(collection.find(query))
    for document in documents:
        commands.append(pymongo.DeleteOne({'id': document['id']}))

    result = collection.bulk_write(commands, ordered=False)
    return result

def delete_temporary_classifications(collection: Collection) -> BulkWriteResult:
    """
    Purge the database of any temporary classifications
    DO NOT EDIT THIS FUNCTION. RISK TO DATABASE INTEGRITY
    :param collection: a mongodb collection object
    :return: results from bulk write
    """
    commands = []

    query = {'class': 'being classified'}

    documents = list(collection.find(query))
    for document in documents:
        commands.append(pymongo.UpdateOne({'id': document['id']}, {'$unset': {'class': 'being classified'}}))

    result = collection.bulk_write(commands, ordered=False)
    return result

def download_database_backup(collection: Collection):
    """
    Downloads a new copy of the database and saves to the backups directory
    :param collection: A mongodb collection object
    """
    filename = f"backup_{str(datetime.now().date())}"

    results = list(collection.find({}))
    stringified = [{str(k): str(v) for k,v in document.items() if k != "_id"} for document in results]

    with open(f'../backups/{filename}', 'w') as outfile:
        json.dump(stringified, outfile, indent=2)



"""Neither of the below comment blocks should remain after UI linkage"""

""" Use this to delete retweets"""
# collection = get_database_collection()
# result = delete_retweets(collection)
# print(f'Deleted {result.deleted_count} retweets from the database')

""" Use this to perform normal tweet fetch"""
collection = get_database_collection()
latest_id = fetch_latest_id(collection)
result = update_collection(collection, fetch_all_recent_tweets_from_twitter(latest_id))
print(f'Inserted {result.upserted_count} new documents into the collection')

# collection = get_database_collection()
# download_database_backup(collection)
