import re
import pandas as pd
import numpy as np
import json
from scipy import sparse
from scipy.sparse import lil_matrix

remove = re.compile(r'(?:@[^s]+|http[^s]+)')
LIWC_PATH = 'liwc_2015.json'
DATA_PATH = 'tweets.csv'
SPARSE = True

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
    rgxs = dict()
    with open(LIWC_PATH, 'r') as fo:
        loaded = json.load(fo)
    words, stems = dict(), dict()
    for cat in loaded:
        words[cat] = list()
        stems[cat] = list()
        for word in loaded[cat]:
            if word.endswith('*'):
                stems[cat].append(word.replace('*', ''))
            else:
                words[cat].append(word)
    for cat in loaded:
        name = "{}.{}".format('liwc',cat)
        if len(stems[cat]) == 0:
            regex_str = r'\b(?:{})\b'.format("|".join(words[cat]))
        else:
            unformatted = r'(?:\b(?:{})\b|\b(?:{})[a-zA-Z]*\b)'
            regex_str = unformatted.format("|".join(words[cat]),
                    "|".join(stems[cat]))
        rgxs[name] = re.compile(regex_str)
    return rgxs, words, stems

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
    rgxs, _, _ = load_dictionary()
    # This was changed from "tokenized" to "Text"
    features = text_col.apply(lambda x:
            counter(x, rgxs, norm=norm))
    return features

def liwc(data):
    data['text'] = [clean(x) for x in data['text']]
    data.dropna(subset=['text'], inplace=True)
    print("Final length of text column: ", len(data))
    return count(data['text'], norm=False)

def run():
    data = pd.read_csv(DATA_PATH)
    print("Original length of text column: ", len(data['text']))
    features = liwc(data)
    pd.DataFrame(features).to_csv('liwc_loadings.csv', index=0)
    print("Saved feature dataframe")
    if SPARSE:
        X = sparse.csr_matrix(df_to_sparse(features))
        pd.DataFrame(X).to_csv('liwc_sparse_matrix.csv')
        print("Saved sparse matrix")


if __name__=='__main__':
    run()

