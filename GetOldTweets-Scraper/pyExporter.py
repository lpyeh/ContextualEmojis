# -*- coding: utf-8 -*-
import sys
import getopt
import csv
import emoji
from emoji import unicode_codes
from datetime import datetime

if sys.version_info[0] < 3:
    import got
else:
    import got3 as got


def exportToCsv():
    # if len(argv) == 0:
    #     print('You must pass some parameters. Use \"-h\" to help.')
    #     return

    # if len(argv) == 1 and argv[0] == '-h':
    #     f = open('exporter_help_text.txt', 'r')
    #     print(f.read())
    #     f.close()

    #     return

    try:
        # opts, args = getopt.getopt(argv, "", (
        # "username=", "near=", "within=", "since=", "until=", "querysearch=", "toptweets", "maxtweets=", "output=", "lang="))

        # tweetCriteria = got.manager.TweetCriteria()

        outputFileName = "output_got.csv"
        outputFile = csv.writer(open(outputFileName, "w", encoding='utf-8-sig', newline=''), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        outputFile.writerow(['username','date','retweets','favorites','text','geo','mentions','hashtags','id','permalink', 'emoji'])


        print('Collecting tweets...\n')

        def receiveBuffer(tweets):
            for t in tweets:
                # print(t.text)
                add_list = []
                if (isinstance(t.emojis, list)):
                    emoji = ' '.join(t.emojis)
                else:
                    emoji = t.emojis
                for each in [t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions, t.hashtags, t.id, t.permalink, emoji]:
                    add_list.append(each)
                outputFile.writerow(add_list)
            print('%d tweets saved on file...\n' % len(tweets))



        # got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)


        # Joy:
        desiredEmojis = '\U0001F600 \U0001F602 \U0001F603 \U0001F604 \U0001F606 \U0001F607 \U0001F609 \U0001F60A \U0001F60B \U0001F60C \U0001F60D \U0001F60E \U0001F60F \U0001F31E'
        desiredEmojis +=  '  \U0001F618 \U0001F61C \U0001F61D \U0001F61B \U0001F63A \U0001F638 \U0001F639 \U0001F63B \U0001F63C  \U00002764  \U0001F496 \U0001F495 \U0001F601 \U00002665 \U0000263A' 

        # Anger:
        desiredEmojis += '  \U0001F62C \U0001F620 \U0001F610 \U0001F611 \U0001F621 \U0001F616 \U0001F624 \U0001F63E '
        desiredEmojis += ' \U0001F4A2  \U0001F47F \U0001F92C '
        
        # Disgust:
        desiredEmojis += ' \U0001F4A9 \U0001F922 \U0001F92E \U0001F637 '

        # Fear:
        desiredEmojis += ' \U0001F605 \U0001F626 \U0001F627 \U0001F631 \U0001F628 \U0001F630 \U0001F640  '

        # Sad:
        desiredEmojis += '   \U0001F614 \U0001F615 \U00002639 \U0001F62B \U0001F629 \U0001F622 \U0001F625 \U0001F62A \U0001F613 \U0001F62D \U0001F63F \U0001F494 '

        # Surprise:
        desiredEmojis += ' \U0001F633 \U0001F62F \U0001F635 \U0001F632 \U0001F92F \U0001F62E '



        desiredEmojis = desiredEmojis.split()

        for unicodeEmoji in desiredEmojis:
            currEmoji = emoji.emojize(unicodeEmoji)

            # current:
            tweetCriteria = got.manager.TweetCriteria().setQuerySearch(currEmoji).setLang('en').setMaxTweets(500)

            #date boundary:
            # tweetCriteria = got.manager.TweetCriteria().setSince("2019-05-01").setUntil("2019-09-30").setQuerySearch(currEmoji).setLang('en').setMaxTweets(162)
            # tweetCriteria = got.manager.TweetCriteria().setSince("2018-01-01").setUntil("2019-05-01").setQuerySearch(currEmoji).setLang('en').setMaxTweets(500)

            
            got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)
        

    # except arg:
    #     print('Arguments parse error, try -h' + arg)
    finally:
        print('Done. Output file generated "%s".' % outputFileName)


if __name__ == '__main__':
    exportToCsv()

