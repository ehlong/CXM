import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, PrecisionRecallDisplay


class BinaryClassifier:
    def __init__(self, label):
        self.label = label
        self.model = LogisticRegression()
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.y_pred = None
        self.feature_names = None

    def fit_predict(self):
        self.model.fit(self.x_train, self.y_train)
        self.y_pred = self.model.predict(self.x_test)

    def print_classification_report(self):
        print(f'Classification report for {self.label} binary classifier')
        print(classification_report(self.y_test, self.y_pred, zero_division=0))

    def print_top_ten(self):
        print(f'Top 10 keywords for {self.label} are:')
        print(self.feature_names[np.argsort(self.model.coef_)[-10:]])

    def graph_pr_curve(self):
        y_score = self.model.predict_proba(self.x_test)[:,1]
        PrecisionRecallDisplay.from_predictions(self.y_test, y_score)
        plt.title(f'PR curve for {self.label} cv-d binary classifier')
        plt.show()