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
from gtts import gTTS
from model import (
    FIELDS,
    THAI_FOOD_MODEL,
    THAI_DISHES_DECK,
    TOP_LEVEL_DECK_NAME,
    WIKIPEDIA_URL,
    YAML_FILE_NAME,
    ThaiDishNote,
    TIMESTAMP,
)


def get_mp3(thai_script, working_dir):
    mp3_path = f"{working_dir}/{thai_script.replace('/',' ')}.mp3"
    if not os.path.exists(mp3_path):
        tts = gTTS(thai_script, lang="th")
        print(f"Saving {mp3_path}")
        tts.save(mp3_path)
    return mp3_path


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
    rows = table.find("tbody").find_all("tr")[1:]
    assert len(df) == len(rows)
    df.attrs["deck_name"] = build_deck_name(table)
    working_dir = "media_files"
    for index, row in enumerate(rows):
        image_path = get_image(row, f"{working_dir}/images")
        df.at[index, FIELDS.IMAGE] = image_path
    for index, row in df.iterrows():
        mp3_path = get_mp3(row[FIELDS.THAI_SCRIPT], f"{working_dir}/sounds")
        df.at[index, FIELDS.RECORDING] = mp3_path
    return df


def panda_to_anki_deck(df):
    name = df.attrs["deck_name"]
    deck = genanki.Deck(
        get_deck_id(name),
        name,
        description=f"All {len(df)} Thai dishes filed under \"{'→'.join(name.split('::')[1:])}\""
        f" on <a href='{WIKIPEDIA_URL}'>Wikipedia List of Thai dishes</a>."
        f"<br/>Deck generated {TIMESTAMP}.",
    )
    media_files = []
    for index, row in df.iterrows():
        image = (
            f"<img src='{os.path.basename(row[FIELDS.IMAGE])}'>"
            if len(row[FIELDS.IMAGE])
            else ""
        )
        recording = (
            f"[sound:{os.path.basename(row[FIELDS.RECORDING])}]"
            if len(row[FIELDS.RECORDING])
            else ""
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


def main_deck_description(dataframes, total_duplicates):
    num_cards = 0
    categories = []
    for df in dataframes:
        num_cards += len(df)
        category_name = "→".join(df.attrs["deck_name"].split("::")[1:])
        categories.append(f"<li>{category_name} ({len(df)})</li>")
    return (
        f"List of all {num_cards} Thai dishes from "
        f"<a href='{WIKIPEDIA_URL}'>Wikipedia List of Thai dishes</a>"
        "<br/><br/>Subdecks:"
        f"<ul>{''.join(categories)}</ul>"
        f"<br/>{total_duplicates} duplicates removed."
        f"<br/>Deck generated {TIMESTAMP}"
    )


def main():
    response = requests.get(WIKIPEDIA_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    decks = []
    media_files = []
    dataframes = []
    thai_script_set = set()
    total_duplicates = 0
    for table in soup.find_all("table", {"class": "wikitable"}):
        df = soup_to_panda(table)
        print(df.attrs["deck_name"])
        script_entries = df[FIELDS.THAI_SCRIPT].tolist()
        duplicates = []
        for index, entry in enumerate(script_entries):
            before = len(thai_script_set)
            thai_script_set.add(entry)
            if before == len(thai_script_set):
                print(f"Dropping duplicate entry for {entry} ({index}).")
                duplicates.append(index)
        if len(duplicates) > 0:
            df = df.drop(duplicates)
            total_duplicates += len(duplicates)
        deck, deck_media_files = panda_to_anki_deck(df)
        media_files.extend(deck_media_files)
        decks.append(deck)
        dataframes.append(df)
    THAI_DISHES_DECK.description = main_deck_description(dataframes, total_duplicates)
    decks.append(THAI_DISHES_DECK)
    package = genanki.Package(decks, media_files)
    package.write_to_file(f"{TOP_LEVEL_DECK_NAME}.apkg")


if __name__ == "__main__":
    main()
