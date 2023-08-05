import json
import os
import webbrowser
import shutil
import subprocess
import time
from jinja2 import Environment, FileSystemLoader

ALL_LANGS = ["en", "zh_cn"]

filename_to_filetype = {
    "background.html": [71],
    "background_all.html": [-101],
    "battle.html": [21, 22, 23, 24, 25, 26, 27],
    "battle_all.html": [-26, -27, -28, -29, -30],
    "character_all.html": [-51, -52],
    "event_all.html": [-41, -42],
    "event_battle_all.html": [-44],
    "event_story_all.html": [-43],
    "npc.html": [52],
    "story.html": [11, 12, 13, 14, 15, 16],
    "story_all.html": [-22, -23, -24, -25, -54],
    "student.html": [51, -53],
    "tag.html": [61],
    "tag_all.html": [-91],
    "track.html": [1, 2, 3, 4],
    "track_all.html": [-11, -12],
    "ui.html": [31, 32],
    "ui_all.html": [-45, -61, -62],
    "video.html": [41],
    "video_all.html": [-71]
}

page_path_and_name = {
    "page/{lang}/main_all.html": "main/index.html",
    "page/{lang}/_index.html": "index.html"
}

page_path_and_name2 = {
    "page/index.html": "index.html",
    # "page/404.html": "404.html"
}

environment = Environment(loader=FileSystemLoader(os.path.split(__file__)[0]), extensions=["jinja2.ext.loopcontrols"])


def change_extension_name(filename: str, extension: str = 'html'):
    splited = filename.split(".")
    splited[-1] = extension
    return ".".join(splited)


def load_file(filepath: str):
    with open(filepath, mode="r", encoding="UTF-8") as file:
        return json.load(file)


def find_template(filetype):
    filetype = str(filetype)
    for i, j in filename_to_filetype.items():
        if int(filetype) in j:
            return i
    return -1


def return_template(template_name, template, content):
    if "background" in template_name:
        return template.render(background=content)
    elif "event" in template_name:
        return template.render(event=content)
    elif "battle" in template_name:
        return template.render(battle=content)
    elif "npc" in template_name or "character" in template_name \
            or "student" in template_name:
        return template.render(char=content)
    elif "story" in template_name:
        return template.render(story=content)
    elif "tag" in template_name:
        return template.render(tag=content)
    elif "track" in template_name:
        return template.render(track=content)
    elif "ui" in template_name:
        return template.render(ui=content)
    elif "video" in template_name:
        return template.render(video=content)


def traverse_path(namespace: list, lang: str = "en"):
    current_path = "/".join(namespace)

    all_path = list(os.listdir(current_path))
    all_file = list(filter(lambda i: os.path.isfile(os.path.join(*namespace, i)), all_path))
    all_folder = list(filter(lambda i: os.path.isdir(os.path.join(*namespace, i)), all_path))

    for i in all_file:
        try:
            target_path = "/".join(["exported_data", *namespace[1:], change_extension_name(i, "json")])

            content = load_file(target_path)
            template_name = find_template(content["filetype"])

            if template_name == -1 and __debug__:
                print("Not worked", i)
                continue

            template = environment.get_template(f"page/{lang}/{template_name}")

            if content["filetype"] in filename_to_filetype["ui.html"]:
                target_path = "/".join(["data_html", lang, *namespace[1:], change_extension_name(i, "html")])
            elif content["filetype"] == -53:
                # for single student
                target_path = "/".join(["data_html", lang, *namespace[1:], "index.html"])
            elif content["filetype"] == 52:
                # for npc
                target_path = "/".join(["data_html", lang, *namespace[1:], "index.html"])
            else:
                target_path = "/".join(["data_html", lang, *namespace[1:], change_extension_name(i, "html")])

            if "_all" in i:
                target_path = "/".join(["data_html", lang, *namespace[1:], "index.html"])

            template_content = return_template(template_name, template, content)

            os.makedirs("/".join(["data_html", lang, *namespace[1:]]), exist_ok=True)
            with open(target_path, mode="w", encoding="UTF-8") as file:
                file.write(template_content)
        except Exception:
            print(target_path)
            raise

    for i in all_folder:
        traverse_path([*namespace, i], lang)


for lang in ALL_LANGS:
    traverse_path(["exported_data"], lang)
    for path, name in page_path_and_name.items():
        template = environment.get_template(path.format(lang=lang))
        result = template.render()
        with open(os.path.join("data_html/" + lang + "/", name), mode="w", encoding="UTF-8") as file:
            file.write(result)
for path, name in page_path_and_name2.items():
    template = environment.get_template(path)
    result = template.render()
    with open(os.path.join("data_html/", name), mode="w", encoding="UTF-8") as file:
        file.write(result)
print("Generation completed")

shutil.copytree("static", "data_html/static", dirs_exist_ok=True, copy_function=shutil.copy)
print("Copying completed")

process = subprocess.Popen("py -m http.server 9000 --directory data_html", shell=True)
time.sleep(2)
webbrowser.open("http://localhost:9000/en/index.html")
process.wait()
