from textcleaning import *
import pandas as pd
import sys
import nltk

nltk.download('stopwords')

filenames = []
if len(sys.argv) == 1:
    print("please enter a tweet csv file name")
    exit()
else:
    filenames = sys.argv[1:]

# open each csv as a pandas data frame
for path in filenames:
    tweetFile = pd.read_csv(path, encoding = 'utf-8')
    tweets = tweetFile["text"]
    #cleanTweets(tweets)
    #print(tweets)
    # remove unwanted columns
    tweetFile.drop(["username", "date", "retweets", "favorites", "geo", "mentions", "hashtags", "permalink"], axis=1, inplace=True)
    for i, row in tweetFile.iterrows():
        # if no emojis in tweet, delete it
        print(row["emoji"])
        if len(row["emoji"]) < 1:
            tweetFile.drop(i, axis=0, inplace=True)
        else:
            # otherwise, clean the tweet
            row["text"] = cleanTweet(row["text"])

    oldFname = path.split(".")[0]
    tweetFile.to_csv(oldFname + "_cleaned.csv", index=False)
    #print(tweetFile)