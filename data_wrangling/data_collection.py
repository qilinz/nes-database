import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

NES_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_Nintendo_Entertainment_System_games"
WIKI_ENDPOINT = "https://en.wikipedia.org"

my_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Accept-Language": "en-us"
}
response = requests.get(NES_WIKI_URL, headers=my_headers)
response.raise_for_status()
data = response.text

soup = BeautifulSoup(data, "html.parser")

# STEP 1: Get the list of games released
games = soup.select(selector='#softwarelist > tbody > tr')

game_list = []

for i in range(2, len(games)):
    game_data = games[i]

    # get wiki link for future use
    try:
        wiki_link = f"{WIKI_ENDPOINT}{game_data.select_one(selector='td i a').get('href')}"
    except AttributeError:
        wiki_link = None

    # Get texts in each row
    original_list = game_data.getText().split("\n")
    new_list = [i for i in original_list if i]

    # Create a dict
    game = {
        "title": new_list[0],
        "wiki_link": wiki_link,
        "developer": new_list[1],
        "publisher_na": new_list[2],
        "publisher_eu": new_list[3],
        "release_na": new_list[4],
        "release_eu": new_list[5]
    }
    game_list.append(game)

# STEP 2: Get the img, genre and mode

for game in game_list:
    time.sleep(1.5)
    if game["wiki_link"]:
        print(game["title"])
        response = requests.get(game['wiki_link'], headers=my_headers)

        soup = BeautifulSoup(response.text, "html.parser")

        # get the img
        try:
            game["img"] = f"https:" \
                          f"{soup.select_one(selector='#mw-content-text > div.mw-parser-output > table > tbody > tr:nth-child(2) > td > a > img').get('src')}"

        except AttributeError:
            game["img"] = None

        # get the label and data
        table_labels = soup.select(selector="#mw-content-text > div.mw-parser-output > table > tbody > tr >.infobox-label")
        table_texts = soup.select(selector="#mw-content-text > div.mw-parser-output > table > tbody > tr >.infobox-data")
        if table_labels and table_texts:
            for i in range(len(table_labels)):
                label = table_labels[i].getText()
                text = table_texts[i].getText()
                if label == "Genre(s)":
                    game["genre"] = text
                if label == "Mode(s)":
                    game["mode"] = text


df = pd.DataFrame.from_records(game_list)
df.to_csv('game_data.csv', index=False, header=True)
