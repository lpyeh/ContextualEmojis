import pandas as pd
import re

a = pd.read_csv("Data/_emoji-tweets-current.csv")
b = pd.read_csv("Data/emoji-tweets-5-to-9-2019.csv")

df = a.append(b)

df.to_csv("Data/crawled.csv", index=False)