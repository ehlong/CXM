import unittest
import os
import pickle
from CrossValidator import CrossValidator

MODELS_DIR = "../models"

CROSS_VALIDATORS = {}


def load_latest_models():
    for file in os.listdir(MODELS_DIR):
        model = pickle.load(open(os.path.join(MODELS_DIR, file), 'rb'))
        CROSS_VALIDATORS[model['label']] = CrossValidator(model['label'], model['model'])


# class MyTestCase(unittest.TestCase):
#     pass


if __name__ == '__main__':
    load_latest_models()
    print(CROSS_VALIDATORS)
    # unittest.main()
