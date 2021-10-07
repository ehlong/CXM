import yaml
import json
from twython import Twython

# change these to change tweet range to classify
START = 0
STOP = 100

def connect():
    with open('../config/key.yaml') as file:
        api_key = yaml.safe_load(file)

    twitter = Twython(api_key['key'], api_key['secret'], oauth_version=2)

    #TODO: move this access token into db? recommended by twython library. Same as committing key tho?
    ACCESS_TOKEN = twitter.obtain_access_token()

    twitter = Twython(api_key['key'], access_token=ACCESS_TOKEN)
    return twitter

def fetch_tweets():
    twitter = connect()
    tweets = {'statuses': []}
    for i in range(10):
        tweets['statuses'].extend(twitter.search(q='to:EpicGames', count=100)['statuses'])

    with open('../data/raw_response.json', 'w') as raw:
        json.dump(tweets, raw, indent=2)

def manually_classify(fetch_new=False):

    if fetch_new:
        fetch_tweets()

    with open('../data/raw_response.json') as file:
        tweets = json.load(file)

    categories = {
        1: 'negative',
        2: 'praise',
        3: 'error',
        4: 'wants',
        5: 'misc'
    }

    output = {'tweets': []}

    print('Input the number of the class category after each tweet')
    for key, val in categories.items():
        print(f'{key}: {val}')

    for tweet in tweets['statuses'][START:STOP]:

        # skip retweets
        if tweet['text'][:2] == "RT":
            continue

        response = input(tweet['text']+': ')
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

manually_classify()







