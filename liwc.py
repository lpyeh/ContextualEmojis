import re
import pandas as pd
import numpy as np
import json
from scipy import sparse
from scipy.sparse import lil_matrix
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV

remove = re.compile(r'(?:@[^s]+|http[^s]+)')
LIWC_PATH = '../Project/liwc_2015.json'
DATA_PATH = '../Project/twitter_83k_bert_emo.csv'
SPARSE = True
TARGETS = ['joy', 'anger', 'disgust', 'fear', 'sad', 'surprise']

grid = {'C': [0.01, 0.1, 0.3, 0.5],
        'loss': ['squared_hinge', 'hinge'],
        'max_iter': [1, 10, 100],
        'class_weight': [{0: a, 1: (1. - a)} for a in np.arange(0.01, 0.3, 0.05)]}

def clean(text):
    try:
        return remove.sub('', text).lower()
    except TypeError:
        print(text)

def df_to_sparse(df):
    arr = lil_matrix(df.shape, dtype=np.float32)
    for i, col in enumerate(df.columns):
        ix = df[col] != 0
        arr[np.where(ix), i] = 1
    return arr.tocsr()

# Written by Brendan Kennedy, adapted by Leigh Yeh 
# for the purposes of this project

# load the liwc dictionary, develop regex to match all values
# of each key in liwc
def load_dictionary():
    print("loading dictionary...")
    rgxs = dict()
    with open(LIWC_PATH, 'r') as fo:
        loaded = json.load(fo)
    words, stems = dict(), dict()
    all_words = list()
    for cat in loaded:
        words[cat] = list()
        stems[cat] = list()
        for word in loaded[cat]:
            if word.endswith('*'):
                stems[cat].append(word.replace('*', ''))
                all_words.append(word.replace('*', ''))
            else:
                words[cat].append(word)
                all_words.append(word)
    for cat in loaded:
        name = "{}.{}".format('liwc',cat)
        if len(stems[cat]) == 0:
            regex_str = r'\b(?:{})\b'.format("|".join(words[cat]))
        else:
            unformatted = r'(?:\b(?:{})\b|\b(?:{})[a-zA-Z]*\b)'
            regex_str = unformatted.format("|".join(words[cat]),
                    "|".join(stems[cat]))
        rgxs[name] = re.compile(regex_str)
    return rgxs, words, stems, list(loaded.keys())

# Counter based on regex matching of words in liwc
def counter(string, rgxs, norm=False):
    if norm:
        try:
            length = len(string.split())
            counts = {c: len(rgx.findall(string))/length for c, rgx in rgxs.items()}
        except ZeroDivisionError:
            print(string)
            return
    else:
        counts = {c: len(rgx.findall(string)) for c, rgx in rgxs.items()}
    return pd.Series(counts)

# Get counts of each word in liwc, in data text col
def count(text_col, norm=True):
    rgxs, _, _, words = load_dictionary()
    # This was changed from "tokenized" to "Text"
    features = text_col.apply(lambda x:
            counter(x, rgxs, norm=norm))
    return features, words

def liwc(data):
    data['text'] = [clean(x) for x in data['text']]
    data.dropna(subset=['text'], inplace=True)
    print("Final length of text column: ", len(data))
    return count(data['text'], norm=False)


def run():
    data = pd.read_csv(DATA_PATH, index_col=0)
    print("Original length of text column: ", len(data['text']))
    features, words = liwc(data)
    # pd.DataFrame(features).to_csv('liwc_loadings.csv', index=0)
    print("Saved feature dataframe")
    results = pd.DataFrame()
    results.index = words
    scores = list()
    if SPARSE:
        X = sparse.csr_matrix(df_to_sparse(features))
        # pd.DataFrame(X).to_csv('liwc_sparse_matrix.csv')
        print("Saved sparse matrix")
    print("Training...")
    for target in TARGETS:
        y_all = list()
        ids_all = list()
        text_all = list()
        print("TARGET: ", target)
        y = data[target].values
        svm = LinearSVC(random_state=123)
        searcher = GridSearchCV(svm, param_grid=grid, cv=5, iid=True, scoring=['f1', 'precision', 'recall', 'accuracy'], refit='f1', verbose=5).fit(X, y)
        rank_index = np.argmin(searcher.cv_results_["rank_test_f1"])
        row = dict(target=target,
                   F1=searcher.best_score_,
                   precision=searcher.cv_results_['mean_test_precision'][rank_index],
                   recall=searcher.cv_results_['mean_test_recall'][rank_index],
                   accuracy=searcher.cv_results_['mean_test_accuracy'][rank_index],
                   F1_std=searcher.cv_results_['std_test_f1'][rank_index],
                   precision_std=searcher.cv_results_['std_test_precision'][rank_index],
                   recall_std=searcher.cv_results_['std_test_recall'][rank_index],
                   accuracy_std=searcher.cv_results_['std_test_accuracy'][rank_index])

        for param, value in searcher.best_params_.items():
            if type(value) == dict:
                row["pos_class_ratio"] = value[1]
            else:
                row[param] = value
        try:
            scores.append(row)
        except TypeError:
            print(type(scores))
            scores = scores.append(row, ignore_index=True)
        results[target] = list(searcher.best_estimator_.coef_[0])

    results.to_csv('liwc_coefficients.csv', index=False)
    scores = pd.DataFrame(scores)
    scores.to_csv("liwc_svm_results.csv", index=False)

if __name__=='__main__':
    run()

