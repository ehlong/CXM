import yaml
import json
from twython import Twython
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split as Split
from sklearn.linear_model import LogisticRegression
from collections import OrderedDict
import sklearn.metrics as Metrics

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
    # TODO: consider TfidfVectorizer as well
    # TODO: Move vectorizer after split when data set is bigger
    df['text'] = df['text'].transform(strip)
    vectorizer = CountVectorizer(stop_words='english', ngram_range=(1,1))
    x = vectorizer.fit_transform(df['text']).toarray()

    y = df['class'].to_numpy()

    # print out the number of times each word appears
    df = pd.DataFrame(data=x, columns=vectorizer.get_feature_names())
    print("The 10 most common words are: ")
    print(df.sum().sort_values(ascending=False)[:10])

    # split and stratify so that train/test have similar target distribution
    x_train, x_test, y_train, y_test = Split(x, y, stratify=y)
    feature_names = np.array(vectorizer.get_feature_names())

    return (x_train, y_train), (x_test, y_test), feature_names


def train_model():
    train, test, feature_names = preprocess_data()

    # extract target names and preserve order. Classifier coef are in this order
    target_names = np.array(list(OrderedDict.fromkeys(train[1])))
    classifier = LogisticRegression(random_state=0).fit(train[0], train[1])
    pred = classifier.predict(test[0])
    score = Metrics.accuracy_score(test[1], pred)
    print(f'Classifier accuracy: {score}\n')

    print(f'Top 10 keywords per class: ')
    for i, label in enumerate(target_names):
        top10 = np.argsort(classifier.coef_[i])[-10:]
        print(f'Label: {label}\nWords:{" ,".join(feature_names[top10])}')

    return classifier


# manually_classify()
train_model()
