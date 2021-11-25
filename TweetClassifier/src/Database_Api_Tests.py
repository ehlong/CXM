import unittest
import mongomock
import Database_Api
from operator import itemgetter

unclassified = [
    {
        'id': 0,
        'text': 'jkl',
        'date': "Sun Oct 17 15:06:16 +0000 2021",
    },
    {
        'id': 1,
        'text': 'ghi',
        'date': "Sun Oct 17 17:28:55 +0000 2021",
    },
    {
        'id': 2,
        'text': 'def',
        'date': "Sun Oct 17 20:09:42 +0000 2021",
    },
    {
        'id': 3,
        'text': 'abc',
        'date': 'Sun Oct 17 20:09:50 +0000 2021'
    },
]


class TestFetchLatestId(unittest.TestCase):
    """
    Unit tests for fetch_latest_id method
    """
    collection = mongomock.MongoClient().db.collection

    def setUp(self):
        self.collection.create_index('id', unique=True)
        self.collection.insert_many(unclassified)

    def tearDown(self):
        self.collection.delete_many({})

    def test_fetch_latest_id_returns_maximum_id(self):
        latest_id = Database_Api.fetch_latest_id(self.collection)
        self.assertEqual(latest_id, max([_['id'] for _ in unclassified]),
                         msg='Id fetched was not the maximum Id')

    def test_latest_id_matches_latest_date(self):
        latest_id = Database_Api.fetch_latest_id(self.collection)

        tweet_with_latest_date = [x for x in unclassified if x['date'] == max(x['date'] for x in unclassified)]
        tweet_with_latest_id = [x for x in unclassified if x['id'] == latest_id]

        self.assertEqual(tweet_with_latest_date, tweet_with_latest_id,
                         msg='The latest Id is not the most recent date')


class TestUpdateCollection(unittest.TestCase):
    """
    Unit tests for update_collection method
    """
    # add classes to tweets
    classified = [x.copy() for x in unclassified]
    classified[0]['class'] = 'wants'
    classified[1]['class'] = 'junk'
    classified[2]['class'] = 'store'
    classified[3]['class'] = 'security'

    # create mock mongo database
    collection = mongomock.MongoClient().db.collection

    # Insert values into collection before each test
    def setUp(self):
        self.collection.create_index('id', unique=True)

    # Remove all values from collection after each test
    def tearDown(self):
        self.collection.delete_many({})

    def test_database_should_be_empty_before_inserts(self):
        database_contents = list(self.collection.find({}))
        self.assertEqual(len(database_contents), 0,
                         msg='Database not empty before insert')

    # no assertion, but will fail if exception is thrown
    def test_does_not_error_on_duplicate_id(self):
        self.collection.insert_many(unclassified)
        Database_Api.update_collection(self.collection, unclassified)

    def test_update_documents_with_added_classes_does_not_change_database_length(self):
        self.collection.insert_many(unclassified)
        with_classes = self.classified[0:2]  # only inserting 2 updated fields

        Database_Api.update_collection(self.collection, with_classes)

        database_contents = list(self.collection.find({}))
        self.assertEqual(len(database_contents), len(unclassified),
                         msg='Number of documents in collection changed')

    def test_update_documents_with_added_classes_changes_modifies_documents_correctly(self):
        self.collection.insert_many(unclassified)
        with_classes = self.classified[0:2]

        Database_Api.update_collection(self.collection, with_classes)

        database_contents = list(self.collection.find({}))
        database_contents = sorted(database_contents, key=itemgetter('id'))

        for i, content in enumerate(database_contents):
            if i == 0 or i == 1:
                self.assertEqual(content['class'], self.classified[i]['class'],
                                 msg='Document update failed - Class not added properly')
            else:
                self.assertEqual('class' in content, False,
                                 msg='Document update failed - Added class to wrong documents')

    def test_insert_new_bulk_documents_inserts_correct_number(self):
        Database_Api.update_collection(self.collection, unclassified)

        database_contents = list(self.collection.find({}))
        self.assertEqual(len(database_contents), len(unclassified),
                         msg='Database insert failed - Wrong collection length')

    def test_insert_new_bulk_documents_inserts_correct_data(self):
        Database_Api.update_collection(self.collection, unclassified)

        database_contents = list(self.collection.find({}))
        database_contents = sorted(database_contents, key=itemgetter('id'))
        for i, document in enumerate(database_contents):
            self.assertEqual(document['id'], unclassified[i]['id'],
                             msg='Document id does not match documents inserted')
            self.assertEqual(document['text'], unclassified[i]['text'],
                             msg='Document text does not match documents inserted')
            self.assertEqual(document['date'], unclassified[i]['date'],
                             msg='Document date does not match documents inserted')


class TestFetchUnclassifiedTweets(unittest.TestCase):
    # create mock mongo database
    collection = mongomock.MongoClient().db.collection

    # Insert values into collection before each test
    def setUp(self):
        self.collection.create_index('id', unique=True)

    # Remove all values from collection after each test
    def tearDown(self):
        self.collection.delete_many({})

    def test_returns_empty_list_if_no_tweets_are_unclassifed(self):
        self.collection.insert_one({'id': 3, 'class': 'junk'})
        fetched = Database_Api.fetch_batch_of_unclassified_tweets(self.collection, 25)
        self.assertEqual(fetched, [])

    def test_only_returns_unclassified_tweets(self):
        self.collection.insert_many(unclassified)
        self.collection.insert_many([{'id': 10, 'class': 'junk'}, {'id': 20, 'class': 'store'}])
        fetched = Database_Api.fetch_batch_of_unclassified_tweets(self.collection, 25)
        self.assertEqual(len(fetched), len(unclassified))

    def test_returns_correct_number_of_tweets_when_limited(self):
        self.collection.insert_many(unclassified)
        fetched = Database_Api.fetch_batch_of_unclassified_tweets(self.collection, 2)
        self.assertEqual(len(fetched), 2)

    def test_returns_all_tweets_when_all_flag_is_true(self):
        self.collection.insert_many(unclassified)
        fetched = Database_Api.fetch_batch_of_unclassified_tweets(self.collection, all=True)
        self.assertEqual(fetched.__len__(), unclassified.__len__())

    def test_returns_lowest_number_ids_first(self):
        self.collection.insert_many(unclassified.__reversed__())
        expected = sorted(unclassified, key=itemgetter('id'))[:2]
        fetched = Database_Api.fetch_batch_of_unclassified_tweets(self.collection, 2)
        self.assertEqual(expected, fetched)


class TestFetchManualClassify(unittest.TestCase):
    collection = mongomock.MongoClient().db.collection

    # Insert values into collection before each test
    def setUp(self):
        self.collection.create_index('id', unique=True)
        self.collection.insert_many(unclassified)

    # Remove all values from collection after each test
    def tearDown(self):
        self.collection.delete_many({})

    def test_fetches_correct_number_of_tweets(self):
        fetched = Database_Api.fetch_for_manual_classify(self.collection, 2)
        self.assertEqual(fetched.__len__(), 2)

    def test_inserts_placeholder_class(self):
        fetched = Database_Api.fetch_for_manual_classify(self.collection, unclassified.__len__())
        tweets_with_temp_classes = list(self.collection.find({'class': 'being classified'}))
        self.assertEqual(tweets_with_temp_classes.__len__(), unclassified.__len__())

    def test_update_still_works_after_placeholder_classes(self):
        fetched = Database_Api.fetch_for_manual_classify(self.collection, unclassified.__len__())
        for tweet in fetched:
            tweet['class'] = 'new class'
        results = Database_Api.update_collection(self.collection, fetched)
        self.assertEqual(results.modified_count, unclassified.__len__())

        new_db_contents = list(self.collection.find({}))
        for tweet in new_db_contents:
            self.assertEqual(tweet['class'], 'new class')



class TestDeleteRetweets(unittest.TestCase):
    collection = mongomock.MongoClient().db.collection

    mockTweets = [
        {'id': 10, 'text': 'RT @ pokemon'},              # Actual retweet
        {'id': 11, 'text': 'RT elonMusk'},              # Actual retweet
        {'id': 12, 'text': 'R is not a retweet'},       # Not Retweet
        {'id': 13, 'text': 'R T is not a retweet'},     # Not Retweet
        {'id': 14, 'text': 'In the RT middle'}          # Not retweet
    ]

    # Insert values into collection before each test
    def setUp(self):
        self.collection.create_index('id', unique=True)

    # Remove all values from collection after each test
    def tearDown(self):
        self.collection.delete_many({})

    def test_only_deletes_retweets(self):
        self.collection.insert_many(self.mockTweets)

        result = Database_Api.delete_retweets(self.collection)
        contents = list(self.collection.find({}))

        self.assertEqual(result.deleted_count, 2)
        self.assertEqual(contents, self.mockTweets[2:])

class TestDeleteTemporaryClassification(unittest.TestCase):
    collection = mongomock.MongoClient().db.collection

    mockTweets = [
        {'id': 1, 'text': 'a'},
        {'id': 2, 'text': 'c', 'class': 'being classified'},
        {'id': 3, 'text': 'b', 'class': 'junk'},
        {'id': 4, 'text': 'd', 'class': 'being classified'},
    ]

    # Insert values into collection before each test
    def setUp(self):
        self.collection.create_index('id', unique=True)
        self.collection.insert_many(self.mockTweets)

    # Remove all values from collection after each test
    def tearDown(self):
        self.collection.delete_many({})

    def test_only_deletes_temporary_classifications(self):
        results = Database_Api.delete_temporary_classifications(self.collection)

        # this strips the _id field that mongo adds as a unique index
        db_contents = self.collection.find({})
        stripped = [{k:v for k, v in document.items() if k != '_id'} for document in db_contents]

        expected = [
            {'id': 1, 'text': 'a'},
            {'id': 2, 'text': 'c'},
            {'id': 3, 'text': 'b', 'class': 'junk'},
            {'id': 4, 'text': 'd'},
        ]

        self.assertEqual(results.modified_count, 2)
        self.assertEqual(stripped, expected)

if __name__ == '__main__':
    unittest.main(verbosity=2)
