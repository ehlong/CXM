import json
import pymongo
from pymongo.collection import Collection
from pymongo.results import BulkWriteResult
import tweepy
import yaml
from datetime import datetime
import dateutil.parser


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
    db_collection = db['tweets']

    return db_collection


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


def fetch_latest_id(db_collection: Collection) -> str:
    """
    Returns the most recent (highest number) id in the database collection

    :param db_collection: The mongodb collection object
    :return: an id as a string
    """
    return db_collection.find().sort("id", pymongo.DESCENDING).limit(1)[0]['id']


def update_collection(db_collection: Collection, new_values: [dict]) -> BulkWriteResult:
    """
    Updated the given collection with each value in new_values
    This will create a new document in the collection if the document doesn't already exist
    If the document is already in the database, it will update it

    DO NOT EDIT THIS FUNCTION. RISK TO DATABASE INTEGRITY
    BE VERY CAREFUL WHAT YOU PASS TO THIS FUNCTION. IT WILL OVERWRITE DATABASE CONTENTS
    :param db_collection: A mongodb collection object
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
                'date': document['date'] if type(document['date']) == datetime
                else dateutil.parser.parse(document['date'])
            }
        }
        if 'class' in document:
            # remove erroneous "bugs" classes
            if document['class'] == 'bugs':
                fields['$set']['class'] = 'bugs/glitches'
            else:
                fields['$set']['class'] = document['class']

        if 'trained' in document:
            fields['$set']['trained'] = document['trained']
        requests.append(pymongo.UpdateOne({'id': document['id']}, fields, upsert=True))

    result = db_collection.bulk_write(requests, ordered=False)
    return result


def fetch_batch_of_unclassified_tweets(db_collection: Collection, num: int = 0, total: bool = False) -> [dict]:
    """
    Search the database for unclassified tweets
    return num tweets, starting at lowest Id

    :param total: If true, return every unclassified tweet
    :param db_collection: A mongodb collection object
    :param num: Number of tweets to fetch
    :return: A list of tweets
    """
    query = {'class': {'$exists': False}}
    if total:
        tweets = list(db_collection.find(query).sort('id', pymongo.ASCENDING))
    else:
        tweets = list(db_collection.find(query).sort('id', pymongo.DESCENDING).limit(num))
    return tweets


def fetch_all_classified_tweets() -> [dict]:
    """
    Search the database for classified tweets
    return tweets
    :return: A list of tweets
    """
    db_collection = get_database_collection()
    query = {'class': {'$exists': True}}
    tweets = list(db_collection.find(query).sort('id', pymongo.DESCENDING))

    return tweets


def fetch_for_manual_classify(db_collection: Collection, num: int) -> [dict]:
    """
    Fetch num tweets from the collection to manually classify
    Insert a placeholder class for these tweets so that successive calls don't
    return the same tweets during concurrent classifying
    :param db_collection: A pymongo collection object
    :param num: Number of tweets to fetch
    :return: A list of num tweets
    """
    tweets = fetch_batch_of_unclassified_tweets(db_collection, num=num)

    # add placeholder class for each tweet
    updates = [x.copy() for x in tweets]
    for update in updates:
        update['class'] = 'being classified'
    update_collection(db_collection, updates)

    return tweets


def delete_retweets(db_collection: Collection) -> BulkWriteResult:
    """
    Purge the database of any retweets
    DO NOT EDIT THIS FUNCTION. RISK TO DATABASE INTEGRITY
    :param db_collection: a mongodb collection object
    :return: result from bulk write. Query for number deleted
    """
    commands = []

    query = {'text': {'$regex': '^RT\\s'}}
    documents = list(db_collection.find(query))
    for document in documents:
        commands.append(pymongo.DeleteOne({'id': document['id']}))

    validate = db_collection.bulk_write(commands, ordered=False)
    return validate


def delete_temporary_classifications(db_collection: Collection) -> BulkWriteResult:
    """
    Purge the database of any temporary classifications
    DO NOT EDIT THIS FUNCTION. RISK TO DATABASE INTEGRITY
    :param db_collection: a mongodb collection object
    :return: results from bulk write
    """
    commands = []

    query = {'class': 'being classified'}

    documents = list(db_collection.find(query))
    for document in documents:
        commands.append(pymongo.UpdateOne({'id': document['id']}, {'$unset': {'class': 'being classified'}}))

    validate = db_collection.bulk_write(commands, ordered=False)
    return validate


def download_database_backup(db_collection: Collection):
    """
    Downloads a new copy of the database and saves to the backups directory
    :param db_collection: A mongodb collection object
    """
    filename = f"backup_{str(datetime.now().date())}"

    results = list(db_collection.find({}))
    stringified = [{str(k): str(v) for k, v in document.items() if k != "_id"} for document in results]

    with open(f'../backups/{filename}', 'w') as outfile:
        json.dump(stringified, outfile, indent=2)


def update_entire_database_to_dates():
    collection = get_database_collection()
    tweets = list(collection.find({}))
    results = update_collection(collection, tweets)
    print(results.matched_count)
    print(results.modified_count)


"""Neither of the below comment blocks should remain after UI linkage"""

""" Use this to delete retweets"""
# collection = get_database_collection()
# result = delete_retweets(collection)
# print(f'Deleted {result.deleted_count} retweets from the database')

""" Use this to perform normal tweet fetch"""
# collection = get_database_collection()
# recent_id = fetch_latest_id(collection)
# collection_result = update_collection(collection, fetch_all_recent_tweets_from_twitter(recent_id))
# print(f'Inserted {collection_result.upserted_count} new documents into the collection')

# collection = get_database_collection()
# download_database_backup(collection)

