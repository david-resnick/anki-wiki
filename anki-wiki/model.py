import genanki

TOP_LEVEL_DECK_NAME = "Thai dishes"
YAML_FILE_NAME = "List_of_Thai_dishes.yaml"
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_Thai_dishes"


class FIELDS:
    THAI_NAME = "Thai name"
    THAI_SCRIPT = "Thai script"
    ENGLISH_NAME = "English name"
    IMAGE = "Image"
    RECORDING = "Recording"
    REGION = "Region"
    DESCRIPTION = "Description"


THAI_FOOD_MODEL = genanki.Model(
    2081520238,
    "Thai Food",
    fields=[
        {"name": "Thai name", "font": "Arial"},
        {"name": "Thai script", "font": "Arial"},
        {"name": "English name", "font": "Arial"},
        {"name": "Image", "font": "Arial"},
        {"name": "Recording", "font": "Arial"},
        {"name": "Region", "font": "Arial"},
        {"name": "Description", "font": "Arial"},
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
    "List from https://en.wikipedia.org/wiki/List_of_Thai_dishes",
)
