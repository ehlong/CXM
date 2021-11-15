from flask import Flask

import Database_Api

app = Flask(__name__)


@app.route('/unclassified_tweets/')
def retrieve_unclassified():
    # Goober error checking
    try:
        collection = Database_Api.get_database_collection()
    except FileNotFoundError:
        return "Unable to open database key."

    # there are none right now -_-
    # tweets = Database_Api.fetch_batch_of_unclassified_tweets(collection, 0, 9)
    generated_tweets = ["This tweet came from REST, #" + str(i) for i in range(9)]
    ret_val = {}
    for i, tweet in enumerate(generated_tweets):
        ret_val[i] = tweet
    return ret_val


if __name__ == '__main__':
    # this should be modified with host='0.0.0.0' to make the server puvblicly available
    app.run()
