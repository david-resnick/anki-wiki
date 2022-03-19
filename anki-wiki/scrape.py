import argparse
import genanki
import os
import pandas as pd  # library for data analysis
import requests  # library to handle requests
import random
import shutil
import tempfile
import yaml
from bs4 import BeautifulSoup  # library to parse HTML documents
from urllib.parse import urlparse
from model import THAI_FOOD_MODEL, TOP_LEVEL_DECK_NAME, YAML_FILE_NAME, WIKIPEDIA_URL


def get_image(row, working_dir):
    image_src = row.find("img")["src"]
    image_url = f"https:{image_src}"
    filename = os.path.basename(urlparse(image_url).path)
    image_path = f"{working_dir}/{filename}"
    if not os.path.exists(image_path):
        response = requests.get(
            image_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
            },
            stream=True,
        )
        with open(image_path, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    return image_path


def soup_to_panda(table):
    df = pd.DataFrame(pd.read_html(str(table))[0])
    rows = table.find("tbody").findAll("tr")[1:]
    assert len(df) == len(rows)
    working_dir = "media_files/images"
    for index, row in enumerate(rows):
        image_path = get_image(row, working_dir)
        df.at[index, "Image"] = image_path
    return df


def panda_to_anki_deck(df, name):

    pass


def extract_headline(heading):
    return heading.find("span", {"class": "mw-headline"}).text


def build_deck_name(table, soup):
    element = table.previous_sibling
    title = TOP_LEVEL_DECK_NAME
    subtitle = None
    while element.name != "h2":
        if subtitle is None and element.name == "h3":
            subtitle = extract_headline(element)
        element = element.previous_sibling
    title = f"{ TOP_LEVEL_DECK_NAME }::{ extract_headline(element) }"
    if subtitle:
        title = f"{ title }::{ subtitle }"
    return title


def get_deck_id(deck_name):
    with open(YAML_FILE_NAME, "r") as file:
        config = yaml.safe_load(file)
    if "decks" not in config:
        config["decks"] = {}
    if deck_name not in config["decks"]:
        config["decks"][deck_name] = random.randrange(1 << 30, 1 << 31)
        with open(YAML_FILE_NAME, "w") as file:
            file.write(yaml.dump(config))
    return config["decks"][deck_name]


def main():
    response = requests.get(WIKIPEDIA_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    for table in soup.find_all("table", {"class": "wikitable"}):
        # df = soup_to_panda(table)
        deck_name = build_deck_name(table, soup)
        print(deck_name)
        deck_id = get_deck_id(deck_name)
        # panda_to_anki_deck(df, deck_name)
        # break


if __name__ == "__main__":
    main()
