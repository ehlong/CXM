import math

import pymongo
from pandas.io import json
from twython import Twython
import yaml
from datetime import datetime

twitter_date_format = "%a %b %d %H:%M:%S %z %Y"


# connect to twitter api. returns Twython object
def connect():
    with open('../config/key.yaml') as file:
        api_key = yaml.safe_load(file)

    twitter = Twython(api_key['key'], api_key['secret'], oauth_version=2)

    # TODO: move this access token into db? recommended by twython library. Same as committing key tho?
    ACCESS_TOKEN = twitter.obtain_access_token()

    twitter = Twython(api_key['key'], access_token=ACCESS_TOKEN)
    return twitter


# fetch the latest batch of tweets, round up to nearest hundred
def fetch_tweets_by_num(num):
    twitter = connect()
    tweets = []
    for i in range(0, num):
        print(len(tweets))

        if (len(tweets) >= num):
            break

        # ----------------------------------------------------------------#
        # STEP 1: Query Twitter
        # STEP 2: Save the returned tweets
        # STEP 3: Get the next max_id
        # ----------------------------------------------------------------#

        # STEP 1: Query Twitter
        if (0 == i):
            # Query twitter for data.
            results = twitter.search(q="to:EpicGames", count='100')
        else:
            # After the first call we should have max_id from result of previous call. Pass it in query.
            results = twitter.search(q="to:EpicGames", count='100', max_id=next_max_id)

        print(json.dumps(results['search_metadata'], indent=2))

        tweets.extend(
            {
                'id': x['id'],
                'text': x['text'],
                'date': x['created_at']
            } for x in results['statuses']
        )

        try:
            # Parse the data returned to get max_id to be passed in consequent call.
            next_results_url_params = results['search_metadata']['next_results']
            next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
        except:
            # No more next pages
            break

    return tweets


def fetch_tweets_since_id(id):
    twitter = connect()
    tweets = []
    while len(temp := twitter.search(q='to:EpicGames', since_id=id, count=100)['statuses']) > 0:
        tweets.extend(
            {
                'id': x['id'],
                'text': x['text'],
                'date': x['created_at']
            } for x in temp
        )
        id = tweets[-1]['id']

    return tweets


# fetch new tweets by number or since a given id
def insert_raw_into_db(key, search_type=None):
    assert search_type == 'num' or 'id'
    if search_type == 'num':
        tweets = fetch_tweets_by_num(key)
    elif search_type == 'id':
        tweets = fetch_tweets_since_id(key)
        print(f'There are {len(tweets)} new tweets since given id')
        if len(tweets) == 0:
            print('No new tweets since given id')
            return

    print(f'Fetched {len(tweets)} tweets')

    # connect to the database, grab the collection
    client = pymongo.MongoClient(
        "mongodb+srv://jboothby:420teamchan@cluster0.dxunx.mongodb.net/data?retryWrites=true&w=majority")
    db = client.get_default_database()
    collection = db['tweets']
    collection.create_index('id', unique=True)

    ids = None
    #try:
    ids = collection.insert_many(tweets)
    #except pymongo.errors.BulkWriteError as e:
        # filter out duplicate value errors (code 11000), keep rest
    #    actual_errors = filter(lambda x: x['code'] != 11000, e.details['writeErrors'])
    #    print(actual_errors)

    # insert_many returns the _id index of each value successfuly inserted
    if ids is not None:
        print(f'Successfully inserted {len(ids.inserted_ids)}/{len(tweets)} values')
    else:
        print(f'No new values inserted')

    collection.find_one(tweets[-1]['id'])
    print(f'The last id inserted is {collection.find().sort("date", pymongo.DESCENDING).limit(1)[0]}')



insert_raw_into_db(5000, search_type='num')
#insert_raw_into_db(1447315031708872708, search_type='id')
