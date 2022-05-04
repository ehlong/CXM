import json

import pymongo
from flask import Flask
from flask import request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from main import train_model_cv, preprocess_unclass_data, unpickle_models
import Database_Api
import CrossValidator

# Globals
can_train = True

# Grab hook to database
collection = Database_Api.get_database_collection()

# Unpickle persisted models for inference
models = unpickle_models()

# Set up scrape scheduler
scheduler = BackgroundScheduler()
trigger = IntervalTrigger(hours=24)
scheduler.add_job(Database_Api.scrape_new_tweets_from_twitter, trigger=trigger)
scheduler.start()

app = Flask(__name__)


@app.route('/unclassified/<int:num>/', methods=['GET'])
def retrieve_unclassified(num):
    """
    Function representing the /unclassified_tweets/ endpoint.
    Pulls tweets from the database using the Database_API
    :return:
    dictionary mapping 'id' to
        dictionary mapping
            'text' to tweet contents ('text')
            'date' to tweet time data ('date')
    (this is converted into a json string with the same mappings when sent by Flask)
    """

    unclass_tweets = Database_Api.fetch_batch_of_unclassified_tweets(collection, num)
    processed_data_map = preprocess_unclass_data(unclass_tweets)

    for tweet in processed_data_map:
        matching_unclass_tweet = next(filter(lambda x: x['id'] == tweet['id'], unclass_tweets))
        matching_unclass_tweet['class'] = []
        for predictor in models.values():
            if predictor.model.predict(tweet['text'].reshape(1, -1)):
                matching_unclass_tweet['class'].append(predictor.label)

    ret_val = {}
    for tweet in unclass_tweets:
        clazz = tweet['class'][0] if len(tweet['class']) != 0 else 'junk'
        ret_val[tweet['id']] = {'text': tweet['text'], 'date': tweet['date'], 'class': clazz}
    return ret_val

@app.route('/unclassified/<int:num>/', methods=['PUT'])
def put_unclassified(num):
    # get the ids
    ids = [int(val) for val in request.json]
    print(ids)
    query = {'id': {'$in': ids}}
    # get the tweets matching those ids
    tweets = list(collection.find(query).sort('id', pymongo.ASCENDING))

    for tweet in tweets:
        tweet['class'] = request.json.get(str(tweet['id']))

    Database_Api.update_collection(collection, tweets)

    tweets = Database_Api.fetch_batch_of_unclassified_tweets(collection, num)
    ret_val = {}
    for tweet in tweets:
        ret_val[tweet['id']] = {'text': tweet['text'], 'date': tweet['date']}
    return ret_val


@app.route('/classified/')
def retrieve_classified():
    tweets = Database_Api.fetch_all_classified_tweets()
    ret_val = {}
    for tweet in tweets:
        ret_val[tweet['id']] = {'text': tweet['text'], 'date': tweet['date'], 'class': tweet['class']}
    return ret_val

@app.route('/retrain/', methods=['POST'])
def retrain():
    global can_train
    if can_train:
        can_train = False
        train_model_cv()
        can_train = True
        return {'training': False}
    else:
        return {'training': True}

@app.route('/infer/', methods=['POST'])
def infer_tweets():

    unprocessed_tweets = json.loads(request.data)
    processed_data_map = preprocess_unclass_data(unprocessed_tweets)

    for tweet in processed_data_map:
        tweet['class'] = []
        for predictor in models.values():
            if predictor.model.predict(tweet['text'].reshape(1, -1)):
                tweet['class'].append(predictor.label)

    return json.dumps([{'id': tweet['id'], 'class': tweet['class']} for tweet in processed_data_map])


if __name__ == '__main__':
    # this should be modified with host='0.0.0.0' to make the server publicly available
    app.run()


