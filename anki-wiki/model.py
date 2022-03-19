import genanki
from datetime import datetime


TOP_LEVEL_DECK_NAME = "Thai dishes"
YAML_FILE_NAME = "List_of_Thai_dishes.yaml"
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_Thai_dishes"
TIMESTAMP = datetime.fromtimestamp(datetime.timestamp(datetime.now())).strftime(
    "%d %B, %Y, %H:%M:%S"
)


class FIELDS:
    THAI_NAME = "Thai name"
    THAI_SCRIPT = "Thai script"
    ENGLISH_NAME = "English name"
    IMAGE = "Image"
    RECORDING = "Recording"
    REGION = "Region"
    DESCRIPTION = "Description"


class ThaiDishNote(genanki.Note):
    @property
    def guid(self):
        for field in THAI_FOOD_MODEL.fields:
            if field["name"] == FIELDS.THAI_SCRIPT:
                return genanki.guid_for(field)
        assert False, "bug in method"


THAI_FOOD_MODEL = genanki.Model(
    2081520238,
    "Thai Food",
    fields=[
        {"name": FIELDS.THAI_NAME, "font": "Arial"},
        {"name": FIELDS.THAI_SCRIPT, "font": "Arial"},
        {"name": FIELDS.ENGLISH_NAME, "font": "Arial"},
        {"name": FIELDS.IMAGE, "font": "Arial"},
        {"name": FIELDS.RECORDING, "font": "Arial"},
        {"name": FIELDS.REGION, "font": "Arial"},
        {"name": FIELDS.DESCRIPTION, "font": "Arial"},
    ],
    templates=[
        {
            "name": "Food name",
            "qfmt": "{{Thai script}}",
            "afmt": "{{FrontSide}}"
            "<hr id='answer'>"
            "{{English name}}"
            "<br/>{{Image}}"
            "<br/>{{Thai name}} {{Recording}}"
            "<br/>{{Description}}"
            "<br/>{{Region}}",
        },
    ],
    css=".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n\n"
    ".cloze {\n font-weight: bold;\n color: blue;\n}\n.nightMode .cloze {\n color: lightblue;\n}",
)

THAI_DISHES_DECK = genanki.Deck(
    1955603963,
    "Thai Dishes",
)
