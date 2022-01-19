import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from sklearn_crfsuite.metrics import flat_classification_report
from sklearn.metrics import classification_report

class CRF():
    
    def __init__(self, counting, tag2index, word2index):
        self.model = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=100,
            all_possible_transitions=True)
        
        self.counting = counting
        self.tag2index = tag2index
        self.word2index = word2index
        
    


    def training(self, x_train, y_train, x_test, y_test):
            self.model.fit(x_train, y_train)

            y_pred = self.model.predict(x_test)
            # y_pred_mar = self.model.predict_marginals(x_test)

            labels = list(self.model.classes_)
            _labels = labels.remove('O')
            _labels = [label for label in labels if label != 'O']

            f1score = metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=_labels)
            # print(flat_classification_report(y_pred = y_pred, y_true = y_test, labels=_labels))
            return y_pred, f1score



        