import argparse
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data")
    parser.add_argument("--column")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    col = args.column

    emojis = {
    "joy": [b'\\U0001f600', b'\\U0001f602', b'\\U0001f603', b'\\U0001f604',
            b'\\U0001f606', b'\\U0001f607', b'\\U0001f609', b'\\U0001f60A',
            b'\\U0001f60B', b'\\U0001f60C', b'\\U0001f60D', b'\\U0001f60E',
            b'\\U0001f60f', b'\\U0001f31E', b'\\U000263A', b'\\U0001f618',
            b'\\U0001f61C', b'\\U0001f61D', b'\\U0001f61B', b'\\U0001f63A',
            b'\\U0001f638', b'\\U0001f639', b'\\U0001f63B', b'\\U0001f63C',
            b'\\U0002764', b'\\U0001f496', b'\\U0001f495', b'\\U0001f601',
            b'\\U0002665'],
    "anger": [b'\\U0001f62C', b'\\U0001f620', b'\\U0001f610', b'\\U0001f611',
              b'\\U0001f620', b'\\U0001f621', b'\\U0001f616', b'\\U0001f624',
              b'\\U0001f63E'],
    "disgust": [b'\\U0001f4A9'],
    "fear": [b'\\U0001f605', b'\\U0001f626', b'\\U0001f627', b'\\U0001f631',
             b'\\U0001f628', b'\\U0001f630', b'\\U0001f640'],
    "sad": [b'\\U0001f614', b'\\U0001f615', b'\\U0002639', b'\\U0001f62B',
            b'\\U0001f629', b'\\U0001f622', b'\\U0001f625', b'\\U0001f62A',
            b'\\U0001f613', b'\\U0001f62D', b'\\U0001f63f', b'\\U0001f494'],
    "surprise": [b'\\U0001f633', b'\\U0001f62f', b'\\U0001f635', b'\\U0001f632']
    }
    emoji_rev = {v: key for key,val in emojis.items() for v in val}

    emotion_cols = {key: list() for key in emojis}

    for i, row in df.iterrows():
        if not isinstance(row[col], str):
            emotions = []
        else:
            emotions = [emoji_rev.get(emoji.encode("unicode-escape"), "")
                        for emoji in row[col].split()]
        for emotion in emotion_cols:
            if emotion in emotions:
                emotion_cols[emotion].append(1)
            else:
                emotion_cols[emotion].append(0)

    for emotion in emotion_cols:
        df[emotion] = pd.Series(emotion_cols[emotion])
    df.to_csv(args.data[:-4] + "_emo.csv", index=False)