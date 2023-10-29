import json
import os
import webbrowser
import shutil
import subprocess
import time
import sys
from main_tool import JinjaTool, TemplateTool
from main_lang import ALL_FUNC_EN as TemplateEnFunc, ALL_FUNC_ZHCN as TemplateZhCnFunc
from main_changelog import ChangelogGeneration
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urljoin

ALL_LANGS = ["zh_cn"]

filename_to_filetype = {
    "album.html": [5],
    "album_all.html": [-13],
    "background.html": [71],
    "background_all.html": [-101],
    "battle.html": [21, 22, 23, 24, 25, 26, 27, 28],
    "battle_all.html": [-26, -27, -28, -29, -30],
    "character_all.html": [-51, -52],
    "event_all.html": [-41, -42],
    "event_battle_all.html": [-44],
    "event_story_all.html": [-43],
    "event_ui_all.html": [-45],
    "npc.html": [52],
    "story.html": [11, 12, 13, 14, 15, 16],
    "story_all.html": [-22, -23, -24, -25, -54],
    "student.html": [51, -53],
    "tag.html": [61],
    "tag_all.html": [-91],
    "track.html": [1, 2, 3, 4],
    "track_all.html": [-11, -12],
    "ui.html": [31, 32],
    "ui_all.html": [-61, -62],
    "video.html": [41],
    "video_all.html": [-71]
}

# Common pages for every language
page_path_and_name = {
    "page/{lang}/main_all.html": "main/index.html",
    "page/{lang}/_index.html": "index.html",
    "page/{lang}/_about.html": "about.html"
}

# Special pages
page_path_and_name2 = {
    "page/index.html": "index.html",
    "page/404.html": "404.html",
    "page/zh_cn/_zhcn_technical.html": "zh_cn/zhcn_technical.html"
}

environment = Environment(loader=FileSystemLoader(os.path.split(__file__)[0]), extensions=["jinja2.ext.loopcontrols",
                                                                                           "jinja2.ext.do"])
# Filters
environment.filters["js_string_safe"] = JinjaTool.js_string_safe
environment.filters["js_html_string_safe"] = JinjaTool.js_html_string_safe
environment.filters["page_minify_html"] = JinjaTool.page_minify_html
environment.filters["is_list"] = lambda obj: isinstance(obj, list)
# Globals - JinjaTool
environment.globals["get_current_utc"] = JinjaTool.get_current_utc
environment.globals["generate_tooltip_id"] = JinjaTool.generate_tooltip_id
environment.globals["get_outer_json"] = JinjaTool.get_outer_json
environment.globals["arg_check"] = JinjaTool.arg_check
environment.globals["extract_storypart_data"] = JinjaTool.storypart_extract_all_data
environment.globals["extract_storypart_data_track"] = JinjaTool.storypart_extract_all_data_track
environment.globals["extract_storypart_data_character"] = JinjaTool.storypart_extract_all_data_characters
environment.globals["extract_storypart_data_background"] = JinjaTool.storypart_extract_all_data_background
# Globals - TemplateTool
environment.globals["py_generate_story_url"] = TemplateTool.py_generate_story_url
environment.globals["py_tooltip_track"] = TemplateTool.py_tooltip_track
environment.globals["py_tooltip_character"] = TemplateTool.py_tooltip_character
environment.globals["py_tooltip_background"] = TemplateTool.py_tooltip_background
# Globals - Template
environment.globals["template_en"] = TemplateEnFunc
environment.globals["template_zhcn"] = TemplateZhCnFunc
# Globals - Others
environment.globals["urljoin"] = urljoin


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
    if "album" in template_name:
        return template.render(album=content)
    elif "background" in template_name:
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


def traverse_path(namespace: list, lang: str):
    current_path = "/".join(namespace)

    all_path = list(os.listdir(current_path))
    all_file = list(filter(lambda i: os.path.isfile(os.path.join(*namespace, i)), all_path))
    all_folder = list(filter(lambda i: os.path.isdir(os.path.join(*namespace, i)), all_path))
    try:
        all_folder.remove(".git")
    except ValueError:
        pass
    # i freaking knew it!
    try:
        all_folder.remove(".github")
    except ValueError:
        pass

    for i in all_file:
        if i.startswith("."):
            # avoid weird bug occurred in GitHub Action
            continue

        try:
            target_path = "/".join(["exported_data", *namespace[1:], change_extension_name(i, "json")])

            content = load_file(target_path)

            if content["filetype"] != 81:
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
                    target_path = "/".join(["data_html", lang, *namespace[1:-1], namespace[-1].lower(), "index.html"])
                else:
                    target_path = "/".join(["data_html", lang, *namespace[1:], change_extension_name(i, "html")])
                if "_all" in i:
                    target_path = "/".join(["data_html", lang, *namespace[1:], "index.html"])

                # 对 target_path 作处理，若html文件名为数据，放弃前导0
                # 因为直接读的 segment 是 int 并不会带前导0
                # 前导0是后端给故事排序时所需要的
                temp = os.path.split(target_path)
                if "story" in temp[0]:
                    # 只针对故事进行处理，其他不进行
                    try:
                        temp2 = int(temp[1][:-5])
                    except Exception:
                        # not a number
                        pass
                    else:
                        if temp2 < 10 and temp2 != 0 and temp[1].startswith("0"):
                            target_path = os.path.join(temp[0], temp[1][1:])

                template_content = return_template(template_name, template, content)
            else:
                # for virtual data

                # load specific template file
                template_path = content["template_path"]
                template = environment.get_template(os.path.join(f"page/{lang}", template_path))

                template_content = template.render(obj=content)

                # export to current location
                page_path = content["page_path"]
                target_path = os.path.join(f"data_html/{lang}", page_path)

            # Normalize the path
            target_path = target_path.replace("\\", "/")
            # For my and for Windows' fuck sake, I didn't realize that Windows is non-case-sensitive
            # when it comes to the directory/folder naming, which it would cause some confusing bugs
            # like the NPC path is never accessible due to I didn't put NPC names in all lower cases.
            relative_path = target_path.split("/")[1:]
            if relative_path[-1].endswith(".html"):
                relative_path = "/".join(relative_path[1:-1])
            else:
                relative_path = "/".join(relative_path)
            # ok now you're gonna do it in my expected way you little
            os.makedirs("/".join(["data_html", lang, relative_path]), exist_ok=True)
            with open(target_path, mode="w", encoding="UTF-8") as file:
                file.write(template_content)
        except Exception:
            print(target_path)
            raise

    for i in all_folder:
        traverse_path([*namespace, i], lang)


# Deleting old files
start_time = time.time()
folders_to_remove = ["en", "zh_cn"]
for i in folders_to_remove:
    try:
        shutil.rmtree(f"data_html/{i}")
    except FileNotFoundError:
        pass
files_to_remove = ["404.html", "index.html"]
for i in files_to_remove:
    try:
        os.remove(f"data_html/{i}")
    except FileNotFoundError:
        pass
print(f"Deletion completed: {time.time() - start_time:0.2f}")

# Generating new files
start_time = time.time()
for lang in ALL_LANGS:
    traverse_path(["exported_data"], lang)
    for path, name in page_path_and_name.items():
        template = environment.get_template(path.format(lang=lang))
        result = template.render(is_static="static")
        os.makedirs("data_html/" + lang + "/", exist_ok=True)
        with open(os.path.join("data_html/" + lang + "/", name), mode="w", encoding="UTF-8") as file:
            file.write(result)
for path, name in page_path_and_name2.items():
    template = environment.get_template(path)
    result = template.render(is_static="static")
    with open(os.path.join("data_html/", name), mode="w", encoding="UTF-8") as file:
        file.write(result)
changelog = ChangelogGeneration(environment)
changelog.generate()
print(f"Generation completed: {time.time() - start_time:0.2f}")

# Copying static
start_time = time.time()
shutil.copytree("static/static", "data_html/static", dirs_exist_ok=True, copy_function=shutil.copy)
print(f"Copying completed: {time.time() - start_time:0.2f}")

if len(sys.argv) == 1:
    # running locally, because GitHub Action will have two args.
    process = subprocess.Popen("py -m http.server 9000 --directory data_html", shell=True)
    time.sleep(2)
    webbrowser.open("http://localhost:9000/en/index.html")
    process.wait()
