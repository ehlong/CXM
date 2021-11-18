# tool to classify tweets with command line
import Database_Api

CATEGORIES = {
    1: 'positive',
    2: 'bugs/glitches',
    3: 'security',
    4: 'store',
    5: 'wants',
    6: 'junk'
}


def manually_classify():
    """
    Query the database for unclassified tweets
    Add manual classifications and insert back into database
    """
    # connect to the database, grab the collection
    collection = Database_Api.get_database_collection()

    # loop until Q or q key kit
    while True:
        print('Classify 25 tweets at a time')
        response = input('Press Q to exit or enter to continue: ')
        if response.lower() in ['q', 'exit', 'quit', 'please make it stop']:
            exit(0)

        print('Input the number of the class category after each tweet')
        for key, val in CATEGORIES.items():
            print(f'{key}: {val}')

        tweets = Database_Api.fetch_batch_of_unclassified_tweets(collection, 25)

        i = 0
        while i < len(tweets):
            response = input(f'{i}: {tweets[i]["text"]}: ')

            try:
                response = int(response)
            except ValueError:
                print('\nNot a valid category integer\n')
                continue

            if response not in CATEGORIES.keys():
                print('\nNot a valid category integer\n')
                continue

            tweets[i]['class'] = CATEGORIES[response]

            i += 1

        result = Database_Api.update_collection(collection, tweets)
        print(f'Successfully updated {result.modified_count} tweets\n')


manually_classify()
