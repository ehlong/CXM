import pymongo
import json
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split as Split
from BinaryClassifier import BinaryClassifier
import spacy
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords

# allow printing full width in console
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

STOP_WORDS = set(stopwords.words('english'))
STOP_WORDS.add('@EpicGames')

CATEGORIES = {
    1: 'positive',
    2: 'bugs/glitches',
    3: 'security',
    4: 'store',
    5: 'wants',
    6: 'junk'
}

BINARY_CLASSIFIERS = {}
for classification in CATEGORIES.values():
    BINARY_CLASSIFIERS[classification] = BinaryClassifier(classification)

TESTING_DATA_PERCENTAGE=0.4


def strip_links(tweet):
    return ' '.join(word for word in tweet.split() if 'http' not in word)


def strip_punctuation(word):
    return re.sub('[?!\'\".,\-#/]+', '', word.lower())


def lemmatize(tweet, tokenizer):
    # TODO: Refactor to make cleaner and more canonical
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
    tweets = df['text'].to_numpy()
    tokenizer = spacy.load('en_core_web_sm')
    # print tweets before processing
    print('Tweets before and after processing: ')
    print(f'Before: \n{tweets[:5]}\n')
    tweets = np.vectorize(strip_links)(tweets)
    tweets = np.array([lemmatize(t, tokenizer) for t in tweets])
    print(f'After: \n{tweets[:5]}\n')
    vectorizer = CountVectorizer(ngram_range=(1, 1))
    x = vectorizer.fit_transform(tweets).toarray()

    y = df['class'].to_numpy()

    # print out the number of times each word appears
    df = pd.DataFrame(data=x, columns=vectorizer.get_feature_names_out())
    print("The 10 most common words are: ")
    print(df.sum().sort_values(ascending=False)[:10])

    # split and stratify so that train/test have similar target distribution
    x_train, x_test, y_train, y_test = Split(x, y, stratify=y, test_size=TESTING_DATA_PERCENTAGE)
    feature_names = np.array(vectorizer.get_feature_names_out())

    return (x_train, y_train), (x_test, y_test), feature_names


# map the y values for each classification category to make them binary
def split_data_by_class(train, test, feature_names):
    x_train, y_train = train[0], train[1]
    x_test, y_test = test[0], test[1]

    for label in CATEGORIES.values():
        BINARY_CLASSIFIERS[label].feature_names = feature_names
        BINARY_CLASSIFIERS[label].x_train = x_train
        BINARY_CLASSIFIERS[label].x_test = x_test
        BINARY_CLASSIFIERS[label].y_train = list(map(lambda y: 1 if y == label else 0, y_train))
        BINARY_CLASSIFIERS[label].y_test = list(map(lambda y: 1 if y == label else 0, y_test))


def train_model():
    train, test, feature_names = preprocess_data()
    split_data_by_class(train, test, feature_names)  # modifies the global BINARY_CLASSIFIERS dict

    for label in CATEGORIES.values():
        BINARY_CLASSIFIERS[label].fit_predict()
        BINARY_CLASSIFIERS[label].print_top_ten()
        BINARY_CLASSIFIERS[label].print_classification_report()
        BINARY_CLASSIFIERS[label].graph_pr_curve()


# manually_classify()
train_model()
