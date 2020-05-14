# Get Old Tweets for Affective Computing Project
Based on: [GetOldTweets-python](https://github.com/fajarmf10/GetOldTweets-python)
Also uses: [Emoji](https://github.com/carpedm20/emoji)

Check out pyExporter.py. 

A project written in Python to get tweets with date boundaries. It bypass some limitations of Twitter Official API. This specifically searches for Tweets with specified emojis.

## Prerequisites

```
pip install -r requirements.txt
```

## other notes

10,000 tweets even distributed.

one csv has current tweets, one has tweets from may to september of 2019.

Tweets include at least one of the following unicode emojis:


U0001F600 U0001F602 U0001F603 U0001F604 U0001F606 U0001F607 U0001F609 U0001F60A U0001F60B U0001F60C U0001F60D U0001F60E U0001F60F U0001F31E U000263A U0001F618 U0001F61C U0001F61D U0001F61B U0001F63A U0001F638 U0001F639 U0001F63B U0001F63C U0002764 U0001F496 U0001F495 U0001F601 U0002665 U0001F62C U0001F620 U0001F610 U0001F611 U0001F620 U0001F621 U0001F616 U0001F624 U0001F63E U0001F4A9 U0001F605 U0001F626 U0001F627 U0001F631 U0001F628 U0001F630 U0001F640 U0001F614 U0001F615 U0002639 U0001F62B U0001F629 U0001F622 U0001F625 U0001F62A U0001F613 U0001F62D U0001F63F U0001F494 U0001F633 U0001F62F U0001F635 U0001F632

(some of above unicodes are missing a zero, my b)

Each row includes: ['username','date','retweets','favorites','text','geo','mentions','hashtags','id','permalink', 'emoji']

For some reason the text includes some emojis (not all emojis) in the tweet. Rely on the emoji column to see which emojis were used (frequency and order is recorded). 
Also a few tweets do not have emojis (this may be because the username of the person includes an emoji). If this is so, the emoji column will be empty.

Code is based on and uses “getoldtweets”:
https://github.com/fajarmf10/GetOldTweets-python

and Python emoji:
https://github.com/carpedm20/emoji