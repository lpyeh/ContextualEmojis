def toLowercase(text):
    return text.lower()


def removeLinks(text):
    import re
    # remove links starting with http/https
    text = re.sub(r"http\S+", "", text)
    # remove other links
    text = re.sub(r"[-a-zA-Z0–9@:%._\+~#=]+\.[^\s\.]\S+", "", text)
    return text

def removeMentions(text):
    import re
    return re.sub(r"@(\w+)", ' ', text, flags=re.MULTILINE)

def removeHashtags(text):
    import re
    return re.sub(r"#(\w+)", ' ', tweet, flags=re.MULTILINE)

def removePunctuation(text):
    import string
    import re
    text =  text.translate(str.maketrans('', '', string.punctuation))
    text = text.replace("…", "")
    return text


# use NLTK to remove stop words
def removeStopWords(text):
    import nltk
    from nltk.corpus import stopwords
    text = text.split(" ")
    stopWords = set(stopwords.words('english'))
    filtered = []
    for word in text:
        if word not in stopWords:
            filtered.append(word)
    return ' '.join(filtered)

# use each of the other functions to 
# remove mentions and links, convert to lowercase and remove punctuation from a list of tweets
def cleanTweets(tweets):
    for i, tweet in enumerate(tweets):
        tweet = removeMentions(tweet)
        tweet = removeLinks(tweet)
        tweet = removePunctuation(tweet)
        tweet = toLowercase(tweet)
        tweet = removeStopWords(tweet)
        tweets[i] = tweet

# remove mentions, links, punctuation and stopwords and convert to lowercase from 1 tweet
def cleanTweet(tweet):
    tweet = removeMentions(tweet)
    tweet = removeLinks(tweet)
    tweet = removePunctuation(tweet)
    tweet = toLowercase(tweet)
    tweet = removeStopWords(tweet)
    return tweet