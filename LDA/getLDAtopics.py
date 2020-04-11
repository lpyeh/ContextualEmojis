import pandas as pd
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import sys

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

if len(sys.argv) == 1:
    print("Please enter the name of data file.")
else:
    # run LDA for each file
    for fname in sys.argv[1:]:
        # create pandas dataframe of tweets
        df = pd.read_csv(fname)
        vectorizer = CountVectorizer()
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
        tf = tf_vectorizer.fit_transform(df["text"])
        tf_feature_names = tf_vectorizer.get_feature_names()

        lda = LatentDirichletAllocation(n_components=10, max_iter=10, learning_method='online', learning_offset=20.,random_state=0).fit(tf)
        no_top_words = 20
        display_topics(lda, tf_feature_names, no_top_words)
