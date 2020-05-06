import sys
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got

import emoji
# https://pypi.org/project/emoji/

# import UNICODE_EMOJI_ALIAS from unicode_codes
from emoji import unicode_codes


def main():
    def printTweet(descr, t):
        print(descr)
        print("Username: %s" % t.username)
        print("Retweets: %d" % t.retweets)
        print("Text: %s" % t.text)
        print("Mentions: %s" % t.mentions)
        print("Hashtags: %s\n" % t.hashtags)

    # for k in unicode_codes.EMOJI_UNICODE:
    #     print(k)
    # return

    # print (unicode_codes.UNICODE_EMOJI_ALIAS)
    # return

    # with open('emoji-codes.txt','r') as file:
    #     emojis = file.read().replace('\n', ' ')
    
    # emojis = emojis.split()
    # print(emoji.emojize('Python is :dizzy_face:'))
    # count = 0
    # for i in emojis:
    #     print(i)
    #     em = emoji.emojize(str(i))
    #     print(em)
    #     count+=1
    #     if count == 20:
    #         break
    # return

    desiredEmojis = '\U0001F600 \U0001F602 \U0001F603 \U0001F604 \U0001F606 \U0001F607 \U0001F609 \U0001F60A \U0001F60B \U0001F60C \U0001F60D \U0001F60E \U0001F60F \U0001F31E'
    desiredEmojis +=  '  \U0001F618 \U0001F61C \U0001F61D \U0001F61B \U0001F63A \U0001F638 \U0001F639 \U0001F63B \U0001F63C  \U0001F496 \U0001F495 \U0001F601 ' 
    desiredEmojis += ' \U0001F62C \U0001F620 \U0001F610 \U0001F611 \U0001F620 \U0001F621 \U0001F616 \U0001F624 \U0001F63E \U0001F4A9 \U0001F605 \U0001F626 \U0001F627 \U0001F631 \U0001F628 \U0001F630 \U0001F640 \U0001F614 \U0001F615  \U0001F62B \U0001F629 \U0001F622 \U0001F625 \U0001F62A \U0001F613 \U0001F62D \U0001F63F \U0001F494 \U0001F633 \U0001F62F \U0001F635 \U0001F632'
    desiredEmojis += ' \U0000263A \U00002764 \U00002665 \U00002639'

    desiredEmojis = desiredEmojis.split()
    # len = 62
    # need 162 tweets for each emoji

    for emo in desiredEmojis:
        emo = emoji.emojize(emo)
    print(desiredEmojis)
    print(len(desiredEmojis))
    return

    queries = []

    emojiUnicodes = list(unicode_codes.EMOJI_UNICODE)
    print(emojiUnicodes)
    print(emoji.emojize(':woman_technologist:'))
    return
    

    for emo in emojiUnicodes:
        emo = emoji.emojize(emo)
        print (emo)
    return

    i = 0
    while i + 10 < len(emojiUnicodes):
        currList = ' OR '.join(emojiUnicodes[i:i+10])
        queries.append(currList)
        i = i+11
    
    currList = ' OR '.join(emojiUnicodes[i:-1])
    queries.append(currList)

    # print(queries)
    return

    i = 0
    while i + 10 < len(emojis):
        currList = ' OR '.join(emojis[i:i+10])
        queries.append(currList)
        i = i+11
    currList = ' OR '.join(emojis[i:-1])
    queries.append(currList)

    print(queries)
    return

    tweetCriteria = got.manager.TweetCriteria().setQuerySearch(emojis).setLang('en').setMaxTweets(10)
    for i in range(10):
        printTweet("### Example 2 - Get tweets by query search [europe refugees]", got.manager.TweetManager.getTweets(tweetCriteria)[i])
    

if __name__ == '__main__':
    main()
