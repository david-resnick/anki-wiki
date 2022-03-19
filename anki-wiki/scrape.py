import argparse
import genanki
import os
import pandas as pd  # library for data analysis
import requests  # library to handle requests
import random
import shutil
import tempfile
import yaml
from pprint import pprint
from bs4 import BeautifulSoup  # library to parse HTML documents
from urllib.parse import urlparse
from model import (
    FIELDS,
    THAI_FOOD_MODEL,
    THAI_DISHES_DECK,
    TOP_LEVEL_DECK_NAME,
    WIKIPEDIA_URL,
    YAML_FILE_NAME,
    ThaiDishNote,
)


def get_image(row, working_dir):
    image = row.find("img")
    if image == None:
        return ""
    image_src = image["src"]
    image_url = f"https:{image_src}"
    original_filename = os.path.basename(urlparse(image_url).path)
    filename = (
        original_filename
        if len(original_filename) < 256
        else f"{original_filename[:251]}.jpg"
    )
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
    df = pd.DataFrame(pd.read_html(str(table))[0]).fillna("")
    rows = table.find("tbody").findAll("tr")[1:]
    assert len(df) == len(rows)
    working_dir = "media_files/images"
    for index, row in enumerate(rows):
        image_path = get_image(row, working_dir)
        df.at[index, FIELDS.IMAGE] = image_path
        df.at[index, FIELDS.RECORDING] = ""
    return df


def panda_to_anki_deck(df, name):
    deck = genanki.Deck(get_deck_id(name), name)
    media_files = []
    for index, row in df.iterrows():
        image = (
            f"<img src='{os.path.basename(row[FIELDS.IMAGE])}'>"
            if len(row[FIELDS.IMAGE])
            else ""
        )
        recording = (
            f"[sound:{row[FIELDS.RECORDING]}]" if len(row[FIELDS.RECORDING]) else ""
        )
        fields = [
            row[FIELDS.THAI_NAME],
            row[FIELDS.THAI_SCRIPT],
            row[FIELDS.ENGLISH_NAME],
            image,
            recording,
            row[FIELDS.REGION],
            row[FIELDS.DESCRIPTION],
        ]
        tags = [row[FIELDS.REGION]] if len(row[FIELDS.REGION]) else None
        deck.add_note(
            ThaiDishNote(
                model=THAI_FOOD_MODEL,
                fields=fields,
                sort_field=FIELDS.THAI_SCRIPT,
                tags=tags,
            )
        )
        if len(row[FIELDS.IMAGE]):
            media_files.append(row[FIELDS.IMAGE])
        if len(row[FIELDS.RECORDING]):
            media_files.append(row[FIELDS.RECORDING])
    return deck, media_files


def extract_headline(heading):
    return heading.find("span", {"class": "mw-headline"}).text


def build_deck_name(table):
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
    decks = [THAI_DISHES_DECK]
    media_files = []
    for table in soup.find_all("table", {"class": "wikitable"}):
        deck, deck_media_files = panda_to_anki_deck(
            soup_to_panda(table), build_deck_name(table)
        )
        media_files.extend(deck_media_files)
        decks.append(deck)
    package = genanki.Package(decks, media_files)
    package.write_to_file(f"{TOP_LEVEL_DECK_NAME}.apkg")


if __name__ == "__main__":
    main()
