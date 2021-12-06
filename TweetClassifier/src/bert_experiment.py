import pandas as pd
import torch.cuda
from Database_Api import fetch_all_classified_tweets as fetch, \
    update_collection, get_database_collection
from simpletransformers.classification import ClassificationModel, ClassificationArgs
from sklearn.model_selection import train_test_split as Split
import wandb

CATEGORIES = {
    1: 'positive',
    2: 'bugs/glitches',
    3: 'security',
    4: 'store',
    5: 'wants',
    6: 'junk'
}

labels_list = ['positive', 'bugs/glitches', 'security', 'store', 'wants', 'junk']


# TODO: Script wandb stuff
# TODO: Continue trying to fine-tune BERT.


def train_model_bert():
    db_contents = fetch()
    data = [[tweet['text'], tweet['class']] for tweet in db_contents]
    df = pd.DataFrame(data, columns=['text', 'labels'])

    train_df, eval_df = Split(df, test_size=0.1)

    labels_map = {v: int(k)-1 for k, v in CATEGORIES.items()}
    model_args = ClassificationArgs(
        num_train_epochs=4,
        evaluate_during_training=True,
        labels_map=labels_map,
        labels_list=labels_list,
        wandb_project="bert"
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
    collection = get_database_collection()
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
    result, model_outputs, wrong_prediction = model.eval_model(eval_df, wandb_log=True)

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
    print("Category == ", result)
    print("Outputs == ", model_outputs)

    print('all is good')
    pass
