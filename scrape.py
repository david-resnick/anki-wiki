import argparse
import pandas as pd  # library for data analysis
import requests  # library to handle requests
import shutil
from bs4 import BeautifulSoup  # library to parse HTML documents
import yaml
import os
import tempfile
from urllib.parse import urlparse


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


def convert_to_deck(table):
    df = pd.DataFrame(pd.read_html(str(table))[0])
    rows = table.find("tbody").findAll("tr")[1:]
    assert len(df) == len(rows)
    working_dir = "images"
    for index, row in enumerate(rows):
        image_path = get_image(row, working_dir)
        df.at[index, "Image"] = image_path


def main():
    parser = argparse.ArgumentParser(
        description="Create Anki decks from wikipedia tables."
    )
    parser.add_argument(
        "yaml_config", type=argparse.FileType("r"), help="yaml configuration file"
    )
    args = parser.parse_args()
    config = yaml.safe_load(args.yaml_config)

    response = requests.get(config["url"])
    soup = BeautifulSoup(response.text, "html.parser")
    for table in soup.find_all("table", {"class": "wikitable"}):
        convert_to_deck(table)
        break


if __name__ == "__main__":
    main()
