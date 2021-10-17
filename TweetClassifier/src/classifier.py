import pymongo
import yaml
import json
from twython import Twython
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split as Split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from spacy.lang.en import English
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

# change these to change tweet range to classify
START = 25
STOP = 50

STOP_WORDS = set(stopwords.words('english'))
STOP_WORDS.add('@EpicGames')

categories = {
    1: 'positive',
    2: 'bugs/glitches',
    3: 'security',
    4: 'store',
    5: 'wants',
    6: 'junk'
}

# allow printing full width in console
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# tool to classify tweets with command line
def manually_classify():

    # connect to the database, grab the collection
    client = pymongo.MongoClient(
        "mongodb+srv://jboothby:420teamchan@cluster0.dxunx.mongodb.net/data?retryWrites=true&w=majority")
    db = client.get_default_database()
    collection = db['tweets']
    cursor = collection.find({})
    tweets = [x for x in cursor]

    output = {'tweets': []}

    print('Input the number of the class category after each tweet')
    for key, val in categories.items():
        print(f'{key}: {val}')

    for tweet in tweets[START:STOP]:

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
            'date': tweet['date'],
            'class': categories[response]
        }

        output['tweets'].append(tweet_obj)

    with open('../data/manually_classified_tweets.json', 'w+') as outfile:
        json.dump(output, outfile, indent=2)


def strip_links(tweet):
    return ' '.join(word for word in tweet.split() if 'http' not in word)

def strip_punctuation(word):
    return re.sub('[?!\'\".,\-#/]+', '', word.lower())

def lemmatize(tweet, tokenizer):
    tokens = tokenizer(str(tweet))

    lemma_list = []
    for token in tokens:
        if str(token) not in STOP_WORDS and str(token.lemma_) != '-PRON-':
            lemma_list.append(strip_punctuation(str(token.lemma_)))

    return ' '.join(lemma_list)


# grab data from json file and get ready for model
def preprocess_data():
    with open('../data/manually_classified_tweets.json') as file:
        data = json.load(file)['tweets']

    df = pd.DataFrame(data)

    # turn text into bag of words vectors
    # TODO: Move vectorizer after split when data set is bigger
    nlp = English()
    tokenizer = nlp.Defaults.create_tokenizer(nlp)
    tweets = df['text'].to_numpy()

    # print tweets before processing
    print('Tweets before and after processing: ')
    print(f'Before: \n{tweets[:5]}\n')
    tweets = np.vectorize(strip_links)(tweets)
    tweets = np.array([lemmatize(t, tokenizer) for t in tweets])
    print(f'After: \n{tweets[:5]}\n')

    vectorizer = CountVectorizer(ngram_range=(1,1))
    x = vectorizer.fit_transform(tweets).toarray()

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

    # extract categories and sort. Classifier coef are in this order
    target_names = list(categories.values())
    target_names.sort()

    classifier = LogisticRegression(random_state=0).fit(train[0], train[1])
    pred = classifier.predict(test[0])

    print(classification_report(y_true=test[1], y_pred=pred, labels=target_names))

    print(f'Top 10 keywords per class: ')
    for i, label in enumerate(target_names):
        top10 = np.argsort(classifier.coef_[i])[-10:]
        print(f'\nLabel: {label}\nWords:{" ,".join(feature_names[top10])}')

    return classifier


manually_classify()
# train_model()