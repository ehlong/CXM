import yaml
import json
from twython import Twython
import pandas as pd
import numpy as np
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

# change these to change tweet range to classify
START = 0
STOP = 100

categories = {
    1: 'negative',
    2: 'praise',
    3: 'error',
    4: 'wants',
    5: 'misc'
}

# allow printing full width in console
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# connect to twitter api. returns Twython object
def connect():
    with open('../config/key.yaml') as file:
        api_key = yaml.safe_load(file)

    twitter = Twython(api_key['key'], api_key['secret'], oauth_version=2)

    # TODO: move this access token into db? recommended by twython library. Same as committing key tho?
    ACCESS_TOKEN = twitter.obtain_access_token()

    twitter = Twython(api_key['key'], access_token=ACCESS_TOKEN)
    return twitter

# fetch the latest batch of tweets
def fetch_tweets():
    twitter = connect()
    tweets = {'statuses': []}
    for i in range(10):
        tweets['statuses'].extend(twitter.search(q='to:EpicGames', count=100)['statuses'])

    with open('../data/raw_response.json', 'w') as raw:
        json.dump(tweets, raw, indent=2)

# tool to classify tweets with command line
def manually_classify(fetch_new=False):
    if fetch_new:
        fetch_tweets()

    with open('../data/raw_response.json') as file:
        tweets = json.load(file)

    output = {'tweets': []}

    print('Input the number of the class category after each tweet')
    for key, val in categories.items():
        print(f'{key}: {val}')

    for tweet in tweets['statuses'][START:STOP]:

        # skip retweets
        if tweet['text'][:2] == "RT":
            continue

        response = input(tweet['text'] + ': ')
        try:
            response = int(response)
        except ValueError:
            print('Not a valid string')
            continue

        if response not in categories.keys():
            continue

        tweet_obj = {
            'text': tweet['text'],
            'id': tweet['id'],
            'date': tweet['created_at'],
            'class': categories[response]
        }

        output['tweets'].append(tweet_obj)

    with open('../data/manually_classified_tweets.json', 'w') as outfile:
        json.dump(output, outfile, indent=2)

# remove mentions and links from the tweet
def strip(tweet):
    blacklist = ['@', 'http']
    stripped = ' '.join(word for word in tweet.split() if not any(x in word for x in blacklist))
    return stripped

# grab data from json file and get ready for model
def preprocess_data():
    with open('../data/manually_classified_tweets.json') as file:
        data = json.load(file)['tweets']

    df = pd.DataFrame(data)

    # turn text into bag of words vectors
    # TODO: remove punctuation for conjuctions
    df['text'] = df['text'].transform(strip)
    vectorizer = CountVectorizer(stop_words='english')
    x = vectorizer.fit_transform(df['text']).toarray()

    # turn class into one-hot array
    label = LabelEncoder()
    one_hot = OneHotEncoder(sparse=False)
    labels = label.fit_transform(df['class'])
    y = one_hot.fit_transform(labels.reshape(-1, 1))

    # print out the number of times each word appears
    df = pd.DataFrame(data=x, columns=vectorizer.get_feature_names())
    print(df.sum().sort_values(ascending=False))

    return x, y, vectorizer


def build_model():
    x, y, vectorizer = preprocess_data()


with open('../data/raw_response.json') as file:
    data = json.load(file)['statuses']
# manually_classify()
build_model()
