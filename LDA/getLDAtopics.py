import pandas as pd
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import sys
import numpy as np
from collections import defaultdict
from sklearn.metrics import accuracy_score

# not sure how many to use
num_features = 5000
num_topics = 5
num_top_words = 10
num_top_documents = 0
# keep track of the total sum of each number of topics
sums = defaultdict(list)

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

def multiClassSVM(vectors, df):
    categories = ['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise']
    X_train, X_test, y_train, y_test= train_test_split(vectors, df, random_state=42, test_size=0.33, shuffle=True)
    #X_train = train.vectors
    #X_test = test.vectors
    print(X_train.shape)
    print(X_test.shape)
    SVC_pipeline = Pipeline([
                    #('tfidf', TfidfVectorizer(stop_words=stop_words)),
                    ('clf', OneVsRestClassifier(LinearSVC(), n_jobs=1)),
                ])
    for category in categories:
        print('... Processing {}'.format(category))
        # train the model using X_dtm & y
        #print(X_train)
        SVC_pipeline.fit(X_train, y_train[category])
        # compute the testing accuracy
        prediction = SVC_pipeline.predict(X_test)
        print('Test accuracy is {}'.format(accuracy_score(y_test[category], prediction)))

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
        df = pd.read_csv(fname)
        num_top_documents = len(df)
        #tweet_vectors = np.ndarray(shape=(num_top_documents, num_topics), dtype=float, order='F')
        vectorizer = CountVectorizer()
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=num_features, stop_words='english')
        tf = tf_vectorizer.fit_transform(df["text"])
        tf_feature_names = tf_vectorizer.get_feature_names()
        lda = LatentDirichletAllocation(n_components=num_topics, max_iter=20, learning_method='online', learning_offset=20.,random_state=0).fit(tf)
        no_top_words = 20
        # H, W, feature_names, documents, no_top_words, no_top_documents
        lda_W = lda.transform(tf)
        tweet_vectors = lda_W
        vectors = []
        #for v in tweet_vectors:
        #    vectors.append((v))
        #print(tweet_vectors)
       # new_df = pd.DataFrame(vectors, columns = ['vectors'])
        #for emotion in ['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise']:
        #    new_df[emotion] = df[emotion]

        #runSVM(tweet_vectors, df[['anger', 'disgust', 'fear', 'happiness', 'sadness', 'surprise']] )
        #print(tweet_vectors)
        multiClassSVM(tweet_vectors, df)
        #print(tweet_vectors)
        #lda_H = lda.components_
        #topic_keywords = show_topics(tf_vectorizer, lda, 20, sums, num_topics)  
        #display_topics(lda_H, lda_W, tf_feature_names, df["text"], num_top_words, num_top_documents, tweet_vectors)
        #df_topic_keywords = pd.DataFrame(topic_keywords)
        #df_topic_keywords.columns = ['Word '+str(i) for i in range(df_topic_keywords.shape[1])]
        #df_topic_keywords.index = ['Topic '+str(i) for i in range(df_topic_keywords.shape[0])]
        #df_topic_keywords  
        #print(df_topic_keywords)
        #for key in sums:
        #   print("num topics %d" %(key))
            #df_topic_keywords.to_csv(fname + "_topics.csv", index=False)

        #display_topics(lda, tf_feature_names, no_top_words)
