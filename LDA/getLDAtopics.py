import pandas as pd
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score
import sys
import numpy as np
from collections import defaultdict
from sklearn.metrics import accuracy_score

# not sure how many to use
num_features = 5000
num_topics = 5
num_top_words = 10
num_top_documents = 0
# loop through this and get topics for each number provided
topic_nums = [20]

#def display_topics(model, feature_names, no_top_words):
#    for topic_idx, topic in enumerate(model.components_):
#        print("Topic %d:" % (topic_idx))
#        print(" ".join([feature_names[i] + ' ' +  str(topic[i])
#                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

#ef show_topics(vectorizer, lda_model, n_words, sums, topic_num):
#    keywords = np.array(vectorizer.get_feature_names())
#    topic_keywords = []
#    for topic_weights in lda_model.components_:
#        top_keyword_locs = (-topic_weights).argsort()[:n_words]
#        sum = 0
#        for loc in top_keyword_locs:
#            sum += topic_weights[loc]
#       sums[topic_num].append(sum)
#        topic_keywords.append(keywords.take(top_keyword_locs))
#    return topic_keywords

def runSVM(x, y):
    #clf = svm.SVC()
    clf = svm.SVC(decision_function_shape='ovo')
    clf.fit(x, y)
    SVC()

# returns f1 score
def multiClassSVM(vectors, df):
    emotions = ['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise']
    X_train, X_test, y_train, y_test= train_test_split(vectors, df, random_state=42, test_size=0.33, shuffle=True)
    print(X_train.shape)
    print(X_test.shape)
    SVC_pipeline = Pipeline([
                    #('tfidf', TfidfVectorizer(stop_words=stop_words)),
                    ('clf', OneVsRestClassifier(LinearSVC(), n_jobs=1)),
                ])
    accuracies = []
    predictions = []
    labels = []
    for emotion_label in emotions:
        print('... Processing {}'.format(emotion_label))
        # train the model using X_dtm & y
        SVC_pipeline.fit(X_train, y_train[emotion_label])
        # compute the testing accuracy
        prediction = SVC_pipeline.predict(X_test)
        current_emo_f1 = f1_score(y_true=y_test[emotion_label], y_pred=prediction, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn')
        print("%s f1 score: %f" %(emotion_label,current_emo_f1))
        
        # keep track of these to get total f1 score
        predictions.extend(prediction)
        labels.extend(y_test[emotion_label])
        accuracies.append(current_emo_f1)

    # return total f1 score
    accuracy = f1_score(y_true=labels, y_pred=predictions, labels=None, pos_label=1, average='binary', sample_weight=None, zero_division='warn')
    return accuracy

def display_topics(H, W, feature_names, documents, no_top_words, no_top_documents):
    for topic_idx, topic in enumerate(H):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]
        for doc_index in top_doc_indices:
            print(documents[doc_index])

if len(sys.argv) == 1:
    print("Please enter the name of data file.")
else:
    # run LDA for each file
    for fname in sys.argv[1:]:
        # create pandas dataframe of tweets
        f1_scores = []
        df = pd.read_csv(fname)
        num_top_documents = len(df)

        vectorizer = CountVectorizer()
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=num_features, stop_words='english')
        tf = tf_vectorizer.fit_transform(df["text"])
        tf_feature_names = tf_vectorizer.get_feature_names()

        # run LDA for each number of topics
        for num_topics in topic_nums:
            lda = LatentDirichletAllocation(n_components=num_topics, max_iter=50, learning_method='online', learning_offset=20.,random_state=0).fit(tf)
            no_top_words = 20
            lda_W = lda.transform(tf)
            f1_scores.append(multiClassSVM(lda_W, df))

        for i, f1_score in enumerate(f1_score):
            print("%d topics %f accuracy" %(topic_nums[i], f1_score))
            
