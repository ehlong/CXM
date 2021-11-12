import pymongo
from pymongo.collection import Collection
from pymongo.results import BulkWriteResult
import tweepy
import yaml


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


def fetch_all_recent_tweets(latest_id: str) -> [dict]:
    """
    Returns a list of all tweets newer than 7 days that occurred after latest_id

    :param latest_id: The most recent (highest number) id in the database collection
    :return: a list of tweets, each a dictionary of values
    """
    client = connect()

    tweets = []
    next_token = 'first_loop'
    while next_token is not None:

        if next_token == 'first_loop':
            result = client.search_recent_tweets(query='to:EpicGames', max_results=100,
                                                 since_id=latest_id, tweet_fields=['created_at'])
        else:
            result = client.search_recent_tweets(query='to:EpicGames', max_results=100, since_id=latest_id,
                                                 tweet_fields=['created_at'], next_token=next_token)

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


def fetch_batch_of_unclassified_tweets(collection: Collection, num: int) -> [dict]:
    """
    Search the database for unclassified tweets
    return num tweets, starting at lowest Id

    :param collection: A mongodb collection object
    :param num: Number of tweets to fetch
    :return: A list of tweets
    """
    query = {'class': {'$exists': False}}
    tweets = list(collection.find(query).sort('id', pymongo.ASCENDING).limit(num))
    return tweets


def delete_retweets(collection: Collection) -> BulkWriteResult:
    """
    Purge the database of any retweets
    :param collection:
    :return: result from bulk write. Query for number deleted
    """
    commands = []

    query = {'text': {'$regex': '^RT\\s'}}
    documents = list(collection.find(query))
    for document in documents:
        commands.append(pymongo.DeleteOne({'id': document['id']}))

    result = collection.bulk_write(commands, ordered=False)
    return result


"""Neither of the below comment blocks should remain after UI linkage"""

""" Use this to delete retweets"""
# collection = get_database_collection()
# result = delete_retweets(collection)
# print(f'Deleted {result.deleted_count} retweets from the database')

""" Use this to perform normal tweet fetch"""
# collection = get_database_collection()
# latest_id = fetch_latest_id(collection)
# result = update_collection(collection, fetch_all_recent_tweets(latest_id))
# print(f'Inserted {result.upserted_count} new documents into the collection')
