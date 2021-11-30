from flask import Flask

import Database_Api

app = Flask(__name__)


@app.route('/unclassified/<int:num>/')
def retrieve_unclassified(num):
    """
    Function representing the /unclassified_tweets/ endpoint.
    Pulls tweets from the database using the Database_API
    :return:
    dictionary mapping 'id' to
        dictionary mapping
            'text' to tweet contents ('text')
            'date' to tweet time data ('date')
    (this is converted into a json string with the same mappings when sent by Flask)
    """
    # Goober error checking
    try:
        collection = Database_Api.get_database_collection()
    except FileNotFoundError:
        return "Unable to open database key."

    tweets = Database_Api.fetch_batch_of_unclassified_tweets(collection, num)
    ret_val = {}
    for i, tweet in enumerate(tweets):
        ret_val[tweet['id']] = {'text': tweet['text'], 'date': tweet['date']}
    return ret_val


if __name__ == '__main__':
    # this should be modified with host='0.0.0.0' to make the server publicly available
    app.run()
