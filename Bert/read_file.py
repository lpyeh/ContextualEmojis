import pandas as pd
import re

emo = {"joy": 0,
        "sadness": 1,
        "fear": 2,
        "anger": 3,
        "surprise": 4,
        "disgust": 5}

if __name__ == "__main__":
    df = {"text": list(),
          "emotion": list(),
          "tweet_id": list()}

    for line in open("twitter_emotion.txt", "r"):
        toks = line.split("\t")
        print(toks)
        df["text"].append(toks[1])
        df["tweet_id"].append(toks[0][:-1])
        df["emotion"].append(emo[re.findall("[a-zA-Z]+", toks[2])[0]])

    pd.DataFrame.from_dict(df).to_csv("emotion.csv", index=False)