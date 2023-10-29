import json
import os
from jinja2 import Environment

TEMPLATE_NAME = "changelog.html"
TEMPLATE_LANG = ["en", "zh_cn"]
CHANGELOG_FILENAME = ["changelog_data", "changelog_parser", "changelog_site"]


class ChangelogGeneration:
    def __init__(self, env: Environment, template_name: str = TEMPLATE_NAME, template_lang: list = TEMPLATE_LANG,
                 changelog_name: list = CHANGELOG_FILENAME):
        self.env = env
        self.template_name = template_name
        self.template_lang = template_lang
        self.changelog_filename = changelog_name

    def generate(self):
        for i in self.template_lang:
            template = self.env.get_template(f"page/{i}/{self.template_name}")

            for j in self.changelog_filename:
                filepath = f"dev_changelogs/{j}_{i}.json"
                with open(filepath, "r", encoding="UTF-8") as file:
                    content = json.load(file)
                html = template.render(changelog=content)

                os.makedirs(f"data_html/{i}", exist_ok=True)
                with open(f"data_html/{i}/{j}.html", "w", encoding="UTF-8") as file:
                    file.write(html)
