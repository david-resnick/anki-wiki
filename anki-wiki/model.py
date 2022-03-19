import genanki

THAI_FOOD_MODEL = genanki.Model(
    2081520238,
    "Thai Food",
    fields=[
        {"name": "Thai name"},
        {"name": "Thai script"},
        {"name": "English name"},
        {"name": "Image"},
        {"name": "Recording"},
        {"name": "Region"},
        {"name": "Description"},
    ],
    templates=[
        {
            "name": "Food name",
            "qfmt": "{{Thai script}}",
            "afmt": "".join[
                "{{FrontSide}}",
                "<hr id='answer'>",
                "{{English name}}",
                "<br/><img src='{{Image}}'>}",
                "<br/>{{Thai name}}",
                "[sound:{{Recording}}]",
                "<br/>{{Description}}",
                "<br/>{{Region}}",
            ],
        },
    ],
)
