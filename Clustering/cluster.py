import sys
import pandas as pd
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("please enter a tweet csv file name")
        exit(1)

    filename = sys.argv[1:]
    emo = ["joy", "sad", "fear", "anger", "disgust", "surprise"]
    X = pd.read_csv(filename[0])[emo]
    X["sum"] = X[emo].sum(axis=1)
    T = X.loc[X['sum'] > 1][emo]
    K = range(2, 10)
    distortions = []
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=0).fit(T)
        distortions.append(sum(
            np.min(pairwise_distances(X=T, Y= kmeans.cluster_centers_,
                                      metric='euclidean'),
                   axis=1)) / X.shape[0])

    diffs = [distortions[i] - distortions[i + 1] for i in range(len(distortions) - 1)]
    best = np.argmax(diffs)
    print("Best number of clusters:", best)

    plt.plot(K, distortions, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Distortion')
    plt.title('The Elbow Method showing the optimal k')
    plt.show()

    kmeans = KMeans(n_clusters=6, random_state=0).fit(X=T)
    print(kmeans.cluster_centers_)
    pd.DataFrame(data=kmeans.cluster_centers_, columns=emo).to_csv("clusters.csv", index=False)

