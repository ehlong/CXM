import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.metrics import classification_report, precision_recall_curve


class CrossValidator:
    def __init__(self, label):
        self.label = label
        self.model = LogisticRegression()
        self.x = None
        self.y = None
        self.y_pred = None
        self.precision = None
        self.recall = None
        self.thresholds = None
        self.feature_names = None

    def fit_predict(self):
        cv = KFold(n_splits=5)
        grid = GridSearchCV(self.model, dict(), scoring='f1',n_jobs=-1, cv=cv, refit=True)
        results = grid.fit(self.x, self.y)
        self.model = results.best_estimator_
        self.y_pred = self.model.predict(self.x)

    def print_classification_report(self):
        print(f'Classification report for {self.label} binary classifier')
        print(classification_report(self.y, self.y_pred, zero_division=0))

    def print_top_ten(self):
        print(f'Top 10 keywords for {self.label} are:')
        print(self.feature_names[np.argsort(self.model.coef_)[-10:]])

    def graph_pr_curve(self):
        y_score = self.model.predict_proba(self.x)[:,1]
        self.precision, self.recall, self.thresholds = precision_recall_curve(self.y, y_score)
        plt.plot(self.recall, self.precision)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'PR curve for {self.label} cv-d binary classifier')
        plt.show()