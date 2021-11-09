# tool to classify tweets with command line
import pymongo


CATEGORIES = {
    1: 'positive',
    2: 'bugs/glitches',
    3: 'security',
    4: 'store',
    5: 'wants',
    6: 'junk'
}

# change these to change tweet range to classify
START = 330
STOP = 470

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
    for key, val in CATEGORIES.items():
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

        if response not in CATEGORIES.keys():
            continue

        tweet_obj = {
            'text': tweet['text'],
            'id': tweet['id'],
            'date': tweet['date'],
            'class': CATEGORIES[response]
        }

        output['tweets'].append(tweet_obj)

    with open('../data/manually_classified_tweets.json', 'w+') as outfile:
        json.dump(output, outfile, indent=2)