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


if __name__ == '__main__':
    unittest.main(verbosity=2)
