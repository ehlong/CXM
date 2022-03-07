import os
import pickle

from Database_Api import fetch_all_classified_tweets as fetch, \
    fetch_all_unclassified_tweets as fetch_un
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split as Split
from CrossValidator import CrossValidator
import spacy
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords

# TODO: Change preprocess_data_train_test_split for binClass to work
# Below allows full printing within the console
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

CROSS_VALIDATORS = {}
for classification in CATEGORIES.values():
    CROSS_VALIDATORS[classification] = CrossValidator(classification)

TEST_X_VALUES = []
TEST_Y_VALUES = []

TESTING_DATA_PERCENTAGE = 0.30


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


def preprocess_data_train_test_split():
    x, y, feature_names = preprocess_data()

    # split and stratify so that train/test have similar target distribution
    x_train, x_test, y_train, y_test = Split(x, y, stratify=y, test_size=TESTING_DATA_PERCENTAGE)
    return (x_train, y_train), (x_test, y_test), feature_names


def preprocess_data():
    data = fetch()
    df = pd.DataFrame(data)
    # turn text into bag of words vectors
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

    ### Testing
    filename = "vectorizer.pickle"
    location = os.path.join("..", "models", filename)
    pickle.dump(vectorizer, open(location, 'wb+'))

    ### Testing
    y = df['class'].to_numpy()
    # print out the number of times each word appears
    df = pd.DataFrame(data=x, columns=vectorizer.get_feature_names_out())
    print("The 10 most common words are: ")
    print(df.sum().sort_values(ascending=False)[:10])

    # split and stratify so that train/test have similar target distribution
    feature_names = np.array(vectorizer.get_feature_names_out())
    # return x, y
    return x, y, feature_names


# Fetch data from database unless supplied
def preprocess_unclass_data(data=None):
    filename = "vectorizer.pickle"
    location = os.path.join("..", "models", filename)
    vectorizer = pickle.load(open(location, 'rb'))
    vectorizer.set_params(vocabulary=vectorizer.get_feature_names_out())
    if data is None:
        data = fetch_un()
    df = pd.DataFrame(data)
    # turn text into bag of words vectors
    tweets = df['text'].to_numpy()
    tokenizer = spacy.load('en_core_web_sm')
    tweets = np.vectorize(strip_links)(tweets)
    tweets = np.array([lemmatize(t, tokenizer) for t in tweets])

    # vectorizer = CountVectorizer(ngram_range=(1, 1))
    x = vectorizer.fit_transform(tweets).toarray()

    processed_tweet_map = [{'id': row['id'],'text': x[i]} for i, row in df.iterrows()]

    # return x, y
    return processed_tweet_map


def split_data_by_class_cv(train, test, feature_names):
    x_train, y_train = train[0], train[1]
    x_test, y_test = test[0], test[1]

    for label in CATEGORIES.values():
        CROSS_VALIDATORS[label].feature_names = feature_names
        CROSS_VALIDATORS[label].x_train = x_train
        CROSS_VALIDATORS[label].x_test = x_test
        CROSS_VALIDATORS[label].y_test = list(map(lambda z: 1 if z == label else 0, y_test))
        CROSS_VALIDATORS[label].y_train = list(map(lambda z: 1 if z == label else 0, y_train))


def train_model_cv():  # -> tuple[any, any, any]:
    train, test, feature_names = preprocess_data_train_test_split()
    split_data_by_class_cv(train, test, feature_names)  # modifies the global BINARY_CLASSIFIERS dict

    for label in CATEGORIES.values():
        CROSS_VALIDATORS[label].fit_predict()
        CROSS_VALIDATORS[label].print_top_ten()
        CROSS_VALIDATORS[label].print_classification_report()
        CROSS_VALIDATORS[label].graph_pr_curve()

    return test[0], test[1], feature_names


def pickle_models(x_test, y_test, feature_names):
    print('Storing models...')
    pickle_jar = {'x_test': x_test, 'y_test': y_test, 'feature_names': feature_names}
    for model in CROSS_VALIDATORS.values():
        cucumber = model.cucumber()
        pickle_jar[cucumber['label']] = cucumber
    filename = "models.pickle"
    location = os.path.join("..", "models", filename)
    pickle.dump(pickle_jar, open(location, 'wb+'))
    print('Models stored successfully')


def unpickle_models_for_testing():
    filename = "models.pickle"
    location = os.path.join("..", "models", filename)
    pickle_jar = pickle.load(open(location, 'rb'))
    for label in CATEGORIES.values():
        model = pickle_jar[label]
        CROSS_VALIDATORS[label] = CrossValidator(model['label'], model['model'])
        CROSS_VALIDATORS[label].x_test = pickle_jar['x_test']
        CROSS_VALIDATORS[label].y_test = list(map(lambda z: 1 if z == label else 0, pickle_jar['y_test']))
        CROSS_VALIDATORS[label].feature_names = pickle_jar['feature_names']

        CROSS_VALIDATORS[label].print_classification_report()
        CROSS_VALIDATORS[label].graph_pr_curve()


# TODO: make this assign stuff to tweets
def unpickle_models():
    filename = "models.pickle"
    location = os.path.join("..", "models", filename)
    pickle_jar = pickle.load(open(location, 'rb'))
    model_map: dict[str: CrossValidator] = {}
    for label in CATEGORIES.values():
        model = pickle_jar[label]
        model_map[label] = CrossValidator(model['label'], model['model'])

    return model_map


if __name__ == '__main__':
    # x_test, y_test, feature_names = train_model_cv()
    # pickle_models(x_test, y_test, feature_names)
    pass

    # bert_experiment.predict_bert(["@epicgames my account got hacked please help"])
