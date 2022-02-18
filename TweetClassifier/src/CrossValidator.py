import os
import pickle
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.metrics import classification_report, PrecisionRecallDisplay


class CrossValidator:
    def __init__(self, label, model=None):
        self.label = label
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.y_pred = None
        self.y_prob = None
        self.feature_names = None
        if model is None:
            self.model = LogisticRegression(class_weight='balanced')
        else:
            self.model = model

    def fit_predict(self):
        cv = KFold(n_splits=5)
        grid = GridSearchCV(self.model, dict(), scoring='f1', n_jobs=-1, cv=cv,
                            refit=True)
        results = grid.fit(self.x_train, self.y_train)
        self.model = results.best_estimator_
        self.y_pred = self.model.predict(self.x_train)

    def print_classification_report(self):
        print(f'Classification report for {self.label} binary classifier')
        y_test_pred = self.model.predict(self.x_test)
        print(classification_report(self.y_test, y_test_pred, zero_division=0))

    def print_top_ten(self):
        print(f'Top 10 keywords for {self.label} are:')
        print(self.feature_names[np.argsort(self.model.coef_)[-10:]])

    def graph_pr_curve(self):
        y_score = self.model.predict_proba(self.x_test)[:, 1]
        PrecisionRecallDisplay.from_predictions(self.y_test, y_score)
        plt.title(f'PR curve for {self.label} cv-d binary classifier')
        plt.show()

    # TODO: work with this refit to make it do the thing
    def refit(self):
        cv = KFold(n_splits=5)
        grid = GridSearchCV(self.model(warm_start=True), dict(), scoring='f1', n_jobs=-1, cv=cv,
                            refit=True)
        results = grid.fit(self.x_train, self.y_train)
        self.model = results.best_estimator_
        self.y_pred = self.model.predict(self.x_train)

    def predict(self):
        self.y_prob = self.model.predict_proba(self.x_test)

    def cucumber(self):
        cucumber = {
            'label': self.label,
            'model': self.model,
        }

        return cucumber
