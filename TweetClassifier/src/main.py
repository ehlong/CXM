import torch.cuda
from Database_Api import fetch_all_classified_tweets as fetch, \
    update_collection, get_database_collection
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split as Split
from BinaryClassifier import BinaryClassifier
from CrossValidator import CrossValidator
from simpletransformers.classification import ClassificationModel, ClassificationArgs
import spacy
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords

# TODO: Change preprocess_data_train_test_split for binClass to work
# TODO: Make a dedicated BERT file
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

CROSS_VALIDATORS = {}
for classification in CATEGORIES.values():
    CROSS_VALIDATORS[classification] = CrossValidator(classification)

TESTING_DATA_PERCENTAGE = 0.4


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

    y = df['class'].to_numpy()

    # print out the number of times each word appears
    df = pd.DataFrame(data=x, columns=vectorizer.get_feature_names_out())
    print("The 10 most common words are: ")
    print(df.sum().sort_values(ascending=False)[:10])

    # split and stratify so that train/test have similar target distribution
    feature_names = np.array(vectorizer.get_feature_names_out())
    # return x, y
    return x, y, feature_names


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


def split_data_by_class_cv(x, y, feature_names):
    # x = x
    # y = y
    for label in CATEGORIES.values():
        CROSS_VALIDATORS[label].feature_names = feature_names
        CROSS_VALIDATORS[label].x = x
        CROSS_VALIDATORS[label].y = list(map(lambda o: 1 if o == label else 0, y))


def train_model():
    train, test, feature_names = preprocess_data_train_test_split()
    split_data_by_class(train, test, feature_names)  # modifies the global BINARY_CLASSIFIERS dict

    for label in CATEGORIES.values():
        BINARY_CLASSIFIERS[label].fit_predict()
        BINARY_CLASSIFIERS[label].print_top_ten()
        BINARY_CLASSIFIERS[label].print_classification_report()
        BINARY_CLASSIFIERS[label].graph_pr_curve()


def train_model_cv():
    x, y, feature_names = preprocess_data()
    split_data_by_class_cv(x, y, feature_names)  # modifies the global BINARY_CLASSIFIERS dict

    for label in CATEGORIES.values():
        CROSS_VALIDATORS[label].fit_predict()
        CROSS_VALIDATORS[label].print_top_ten()
        CROSS_VALIDATORS[label].print_classification_report()
        CROSS_VALIDATORS[label].graph_pr_curve()


def train_model_bert():
    db_contents = fetch()
    data = [[tweet['text'], tweet['class']] for tweet in db_contents]
    df = pd.DataFrame(data, columns=['text', 'labels'])

    train_df, eval_df = Split(df, test_size=0.1)

    labels_map = {v: int(k)-1 for k, v in CATEGORIES.items()}
    model_args = ClassificationArgs(
        num_train_epochs=3,
        evaluate_during_training=True,
        labels_map=labels_map
    )

    cuda_available = torch.cuda.is_available()
    model = ClassificationModel(
        'bert',
        'bert-base-cased',
        args=model_args,
        use_cuda=cuda_available,
        num_labels=labels_map.keys().__len__()
    )

    global_step, training_details = model.train_model(
        train_df,
        eval_df=eval_df,
        multi_label=True,
    )
    result, model_outputs, wrong_prediction = model.eval_model(eval_df)

    print(f'Global step: {global_step}')
    print(f'training_details: {training_details}')
    print(result)
    print(model_outputs)
    print(wrong_prediction)

    # TODO: Create retrain function

def retrain_bert():
    # 1. Get un-trained classified data
    # 2. Retrieve BERT model
    # 3. Train




    db_contents = fetch()
    ### CHECK ###
    tweets = [x for x in db_contents if 'trained' not in x.keys()]
    ### TESTING BELOW ###
    for tweet in tweets:
        tweet['trained'] = 1
    collection = get_database_collection
    update_collection(collection, tweets)
    data = [[tweet['text'], tweet['class']] for tweet in db_contents]
    df = pd.DataFrame(data, columns=['text', 'labels'])

    train_df, eval_df = Split(df, test_size=0.1)


    cuda_available = torch.cuda.is_available()
    try:
        model = ClassificationModel(
            "bert", "outputs/best_model",
            use_cuda=cuda_available
        )
    except OSError as e:
        print('The model does not exist')
        return


    global_step, training_details = model.train_model(
        train_df,
        eval_df=eval_df,
        multi_label=True,
    )
    result, model_outputs, wrong_prediction = model.eval_model(eval_df)

    print(f'Global step: {global_step}')
    print(f'training_details: {training_details}')
    print(result)
    print(model_outputs)
    print(wrong_prediction)


def predict_bert(tweets: [str]):
    cuda_available = torch.cuda.is_available()
    try:
        model = ClassificationModel(
            "bert", "outputs/best_model",
            use_cuda=cuda_available
        )
    except OSError as e:
        print('The model does not exist')
        return

    result, model_outputs = model.predict(tweets)

    print('all is good')
    pass


if __name__ == '__main__':
    # train_model_cv()
    train_model_bert()
    predict_bert(["@epicgames my account got hacked please help"])
