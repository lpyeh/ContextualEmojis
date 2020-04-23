from textcleaning import *
import pandas as pd
import sys
import nltk
import math
import numpy as np

emotionMap = {'😊': "happiness", 'U+1F602' : "happiness", 'U+1F603' : "happiness", 'U+1F604' : "happiness", 'U+1F606': "happiness"}
emotionMap = {'😀' : "happiness", '😂' : "happiness", '😃' : "happiness", '😄' : "happiness", '😆' : "happiness", '😇' : "happiness", '😉' : "happiness", '😊' : "happiness",
'😋' : "happiness", '😌' : "happiness", '😍' : "happiness", '😎' : "happiness", '😏' : "happiness", '🌞' : "happiness", '☺' : "happiness", '😘' : "happiness",
'😜' : "happiness", '😝' : "happiness", '😛' : "happiness", '😺' : "happiness", '😸' : "happiness", '😹' : "happiness", '😻' : "happiness", '😼' : "happiness",
'❤' : "happiness", '💖' : "happiness", '💕' : "happiness", '😁' : "happiness", '♥' : "happiness", '😬' : "anger", '😠' : "anger", '😐' : "anger", '😑' : "anger", '😠' : "anger", '😡' : "anger", '😖' : "anger", '😤' : "anger",
'😾' : "anger", '💩': "disgust", '😅' : "fear", '😦' : "fear", '😧' : "fear", '😱' : "fear", '😨' : "fear", '😰' : "fear", '🙀' : "fear", 
'😔' : "sadness", '😕' : "sadness", '☹' : "sadness", '😫' : "sadness", '😩' : "sadness", '😢' : "sadness", '😥' : "sadness", '😪' : "sadness", '😓' : "sadness", '😭' : "sadness", '😿' : "sadness", '💔' : "sadness",
'😳' : "surprise", '😯' : "surprise", '😵' : "surprise", '😲' : "surprise"}

# return which emotion the emojis are associated with
def getEmojiLabel(emojiList, i, df):
    for emoji in emojiList:
        if emoji in emotionMap:
            # get the emotion associated with the emoji
            emotion = emotionMap[emoji]
            # set the emotion for this tweet
            tweetFile[emotion][i] = 1

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
    # remove unwanted columns
    tweetFile.drop(["username", "date", "retweets", "favorites", "geo", "mentions", "hashtags", "permalink"], axis=1, inplace=True)

    # add columns for each emotion
    emotions = ["anger", "disgust", "fear", "happiness", "sadness", "surprise"]
    for emotion in emotions:
        tweetFile[emotion] = 0
    
    for i, row in tweetFile.iterrows():
        # if no emojis in tweet, delete it
        if pd.isnull(row["emoji"]):
            tweetFile.drop(i, axis=0, inplace=True)
        else:
            # otherwise, clean the tweet
            cleaned = cleanTweet(row["text"])
            # if the tweet is now empty, remove it
            if cleaned == "":
                tweetFile.drop(i, axis=0, inplace=True)
            else:
                getEmojiLabel(row["emoji"], i, tweetFile)
                tweetFile["text"][i] = cleanTweet(row["text"])

    # write out a new cleaned csv with fname: originalFname_cleaned.csv
    oldFname = path.split(".")[0]
    tweetFile.to_csv(oldFname + "_cleaned.csv", index=False)
