import pandas as pd
import numpy as np

df = pd.read_csv("game_data_added.csv")

# change nan to None
df = df.replace({np.nan: None})

# remove all the footnotes, e.g. [1]
df = df.replace("\[\d\]", "", regex=True)

# leave the genre simple: remove contents in ()
df["genre"] = df["genre"].replace("\([\w\s,]+\)", "", regex=True)

# change the mode to multi-support
df["multi-support"] = False
df.loc[(df['mode'].notna()) & (df['mode'] != 'Single player') & (df['mode'] != 'Single-player'), 'multi-support'] = True
df.drop(columns=["mode"], inplace=True)


game_list = df.to_dict("records")

for game in game_list:
    # 1. release date to year
    if game["release_na"] != "Unreleased":
        game["release_na"] = game["release_na"][-4:]
    if game["release_eu"] != "Unreleased":
        game["release_eu"] = game["release_eu"][-4:]


df2 = pd.DataFrame.from_records(game_list)
df2.to_csv('../game_data_processed.csv', index=False, header=True)
