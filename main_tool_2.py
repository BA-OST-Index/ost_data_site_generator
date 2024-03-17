import os
import json
import shutil
from main_tool import *

BASE_OUTPUT_PATH = "./static/static/js/auto/tooltip/"


def js_writer(filename: str, data: dict, data_type: str, basepath=BASE_OUTPUT_PATH):
    os.makedirs(basepath, exist_ok=True)
    filepath = os.path.join(basepath, filename)
    with open(filepath, mode="w", encoding="UTF-8") as f:
        f.write(f"const tooltip_data_{data_type} = ")
        f.write(json.dumps(data, ensure_ascii=False))


def rename_js(timestamp: int or str, basepath: str = BASE_OUTPUT_PATH):
    for i in os.listdir(basepath):
        old_path = os.path.join(basepath, i)
        new_path = old_path.split("_")
        new_path = "_".join(new_path[:-1] + [f"{timestamp}.js"])

        os.rename(old_path, new_path)


class TooltipHtmlGenerator:
    BASE_INPUT_PATH = "./exported_data/"
    BASE_OUTPUT_PATH = BASE_OUTPUT_PATH
    LANGCODE_LIST = ["en", "zh_cn"]
    JINJA_TEMPLATE = {
        "storyinfo": "{% from 'template/[LANG]/_macro_tooltip.html' import tooltip_storyinfo %}"
                     "{{ tooltip_storyinfo(story) }}",
        "storypart": "{% from 'template/[LANG]/_macro_tooltip.html' import tooltip_storypart %}"
                     "{{ tooltip_storypart(story, story_part) }}",
        "storypart_source": "{% from 'template/[LANG]/_macro_tooltip.html' import tooltip_storypart_source %}"
                            "{{ tooltip_storypart_source(part) }}",
        "album": "{% from 'template/[LANG]/_macro_tooltip.html' import tooltip_album %}"
                 "{{ tooltip_album(album) }}",
        "character": "{% from 'template/[LANG]/_macro_tooltip.html' import tooltip_character %}"
                     "{{ tooltip_character(char, instance_id, instance_type) }}",
        "track": "{% from 'template/[LANG]/_macro_tooltip.html' import tooltip_track %}"
                 "{{ tooltip_track(track, instance_id, instance_type) }}",
        "background": "{% from 'template/[LANG]/_macro_tooltip.html' import tooltip_background %}"
                      "{{ tooltip_background(background, instance_id, instance_type) }}",
        "background_to_char": "{% from 'template/[LANG]/_macro_tooltip2.html' import background_to_character_in_story %}"
                              "{{ background_to_character_in_story(character, instance_id, instance_id2) }}",
        "background_to_track": "{% from 'template/[LANG]/_macro_tooltip2.html' import background_to_track %}"
                               "{{ background_to_track(track, instance_id, instance_id2) }}",
        "character_to_track": "{% from 'template/[LANG]/_macro_tooltip2.html' import character_to_track %}"
                              "{{ character_to_track(track, instance_id) }}"
    }

    @staticmethod
    def get_tooltip(*args):
        return JinjaTool.generate_tooltip_id(*args)

    def __init__(self, jinja_env):
        self.init_time = INIT_TIME
        self.jinja_env = jinja_env

        # 数据类型
        self.data_types = ["story", "album", "background", "character", "track"]
        self.data = {
            lang: {
                type: {}
                for type in self.data_types
            }
            for lang in self.LANGCODE_LIST}

        # Jinja模板编译
        self.jinja_template = {
            lang: {
                name: self.jinja_env.from_string(content.replace("[LANG]", lang))
                for (name, content) in self.JINJA_TEMPLATE.items()
            }
            for lang in self.LANGCODE_LIST
        }
        self.jinja_template["_background_direct"] = lambda data: [[i[0]["image"]["value"], i[0]["filename"]]
                                                                  for i in data.values()]
        self.jinja_template["background_direct"] = lambda data: {"type": "bg_direct",
                                                                 "data": self.jinja_template["_background_direct"](
                                                                     data)}

        # 其它初始化
        self.is_generated = False

    @staticmethod
    def walk_dir(*path, base_path=None):
        for root, dirs, files in os.walk(TooltipHtmlGenerator.join_dir(*path, base_path=base_path)):
            for file in files:
                if file == "_all.json":
                    continue

                file_path = os.path.join(root, file)
                yield file_path

    @staticmethod
    def list_dir(*path, base_path=None):
        return os.listdir(TooltipHtmlGenerator.join_dir(*path, base_path=base_path))

    @staticmethod
    def join_dir(*path, base_path=None):
        if base_path is None:
            base_path = TooltipHtmlGenerator.BASE_INPUT_PATH
        return os.path.join(base_path, *path)

    @staticmethod
    def get_json(filepath):
        with open(filepath, mode="r", encoding="utf-8") as f:
            return json.load(f)

    def get_render_result(self, template, **data):
        return JinjaTool.page_minify_html(template.render(**data))

    def add_render_result_by_lang(self, template_keyname: str, tooltip_id: str, data_type: str, lang_list=None, **data):
        if lang_list is None:
            lang_list = self.LANGCODE_LIST

        for lang in lang_list:
            if tooltip_id in self.data[lang][data_type].keys():
                print("skipping tooltip id", tooltip_id)
                continue
            self.data[lang][data_type][tooltip_id] = self.get_render_result(self.jinja_template[lang][template_keyname],
                                                                            **data)

    def _generate_story(self):
        # story
        print("tooltip generation: story")
        all_walker = []
        all_walker.append(self.walk_dir("main", "story"))
        for event_id in self.list_dir("event"):
            try:
                int(event_id)  # a valid event_id should be int
                if os.path.isdir(self.join_dir("event", event_id, "story")):
                    all_walker.append(self.walk_dir("event", event_id, "story"))
            except ValueError:
                continue
        for stu_id in self.list_dir("character", "student"):
            if stu_id == "_all.json":
                continue
            if os.path.isdir(self.join_dir("character", "student", stu_id, "bond")):
                all_walker.append(self.walk_dir("character", "student", stu_id, "bond"))

        for generator in all_walker:
            for filepath in generator:
                print(f"filename: {filepath}", get_curr_time_printable())
                content = self.get_json(filepath)

                # storyinfo
                tooltip_id = self.get_tooltip("story", content["instance_id"])
                self.add_render_result_by_lang("storyinfo", tooltip_id, "story", story=content)

                # storypart (part/source)
                if content["filetype_sub"] == 0:
                    for (no, data) in enumerate(content["part"], 1):
                        tooltip_id = self.get_tooltip("storypart", content["instance_id"], no)
                        self.add_render_result_by_lang("storypart", tooltip_id, "story",
                                                       story=content, story_part=data)

                        tooltip_id = self.get_tooltip("storypart_source", content["instance_id"], no)
                        self.add_render_result_by_lang("storypart_source", tooltip_id, "story",
                                                       part=data)

    def _generate_album(self):
        # album (album)
        print("tooltip generation: album")
        all_walker = []
        all_walker.append(self.walk_dir("album"))
        for generator in all_walker:
            for filepath in generator:
                print(f"filename: {filepath}", get_curr_time_printable())
                content = self.get_json(filepath)

                tooltip_id = self.get_tooltip("album", content["uuid"])
                self.add_render_result_by_lang("album", tooltip_id, "album",
                                               album=content)

    def _generate_background(self):
        # background (bg)
        print("tooltip generation: background")
        all_walker = []
        all_walker.append(self.walk_dir("background"))
        for generator in all_walker:
            for filepath in generator:
                print(f"filename: {filepath}", get_curr_time_printable())
                content = self.get_json(filepath)

                # background itself
                tooltip_id = self.get_tooltip("background", content["uuid"])
                self.add_render_result_by_lang("background", tooltip_id, "background",
                                               background=content, instance_id=content["uuid"], instance_type="story")

                # background to character (in story)
                # output_usedby_character_dict
                for data in content["used_by"]["data_character"].values():
                    data = data[0]

                    tooltip_id = self.get_tooltip("character", TemplateTool.get_character_instance_id(data),
                                                  "background", content["uuid"])
                    self.add_render_result_by_lang("background_to_char", tooltip_id, "background",
                                                   character=data, instance_id=content["uuid"],
                                                   instance_id2=content["filename"])

                # background to character (direct)
                # output_usedby_character
                for data in content["character"]:
                    tooltip_id = self.get_tooltip("character", TemplateTool.get_character_instance_id(data),
                                                  # 背景UUID特殊处理，加上 -direct 以适配现有代码
                                                  "background", content["uuid"] + "-direct")

                    # 获取外部数据
                    char_outer = JinjaTool.get_outer_json(TemplateTool.get_character_instance_id(data), "character")
                    # student 数据特殊处理
                    try:
                        char_outer = char_outer["student"]
                    except KeyError:
                        pass

                    # 特殊处理：返回一个list，到时候直接JS动态生成
                    for lang in self.LANGCODE_LIST:
                        self.data[lang]["background"][tooltip_id] = (self.jinja_template["background_direct"]
                                                                     (char_outer["used_by"]["data_background_direct"]))

                # background to track
                # output_usedby_track
                for data in content["used_by"]["data_track"].values():
                    data = data[0]

                    tooltip_id = self.get_tooltip("track", data["instance_id"],
                                                  "background", content["uuid"])
                    self.add_render_result_by_lang("background_to_track", tooltip_id, "background",
                                                   track=data, instance_id=content["uuid"], instance_id2=content["filename"])

    def _generate_character(self):
        # character (char)
        print("tooltip generation: character")
        all_walker = []
        all_walker.append(self.walk_dir("character", "npc"))
        temp = []
        for stu_id in self.list_dir("character", "student"):
            # 意思就是，每个学生id都有一个学生自己的文件
            # 例如 yuuka -> yuuka/yuuka.json
            if stu_id == "_all.json":
                continue
            temp.append(self.join_dir("character", "student", stu_id, stu_id + ".json"))
        all_walker.append(temp)

        for generator in all_walker:
            for filepath in generator:
                print(f"filename: {filepath}", get_curr_time_printable())
                content = self.get_json(filepath)
                if content["filetype"] == -53:
                    content = content["student"]
                elif content["filetype"] == 52:
                    # 覆写uuid，因为这里用不到
                    # （指代码太屎山了）
                    content["uuid"] = TemplateTool.get_character_instance_id(content)

                # character itself
                tooltip_id = self.get_tooltip("character", content["uuid"])
                self.add_render_result_by_lang("character", tooltip_id, "character",
                                               char=content, instance_id=content["uuid"],
                                               instance_type="story")

                # character to track
                # output_usedby_track
                for data in content["used_by"]["data_track"].values():
                    data = data[0]

                    tooltip_id = self.get_tooltip("track", data["instance_id"],
                                                  "character", content["uuid"])
                    self.add_render_result_by_lang("character_to_track", tooltip_id, "character",
                                                   track=data, instance_id=content["uuid"])

                # character to background (direct)
                # output_usedby_background
                for data in content["used_by"]["data_background_direct"].values():
                    data = data[0]

                    # character 到 direct background 就是 background itself
                    tooltip_id = self.get_tooltip("background", data["uuid"])
                    self.add_render_result_by_lang("background", tooltip_id, "character",
                                                   background=data, instance_id=content["uuid"],
                                                   instance_type="story")

                # character to background (indirect/story)
                # output_usedby_background
                joined_bgs = {**content["used_by"]["data_background"],
                              **content["used_by"]["data_background_by_comm"]}
                for data in joined_bgs.values():
                    data = data[0]

                    tooltip_id = self.get_tooltip("background", data["uuid"],
                                                  "character", content["uuid"])
                    self.add_render_result_by_lang("background", tooltip_id, "character",
                                                   background=data, instance_id=content["uuid"],
                                                   instance_type="character")

                # character to character (story)
                # output_usedby_character_dict
                for data in content["used_by"]["data_character"].values():
                    data = data[0]

                    tooltip_id = self.get_tooltip("character", TemplateTool.get_character_instance_id(data),
                                                  "character", content["uuid"])
                    self.add_render_result_by_lang("character", tooltip_id, "character",
                                                   char=data, instance_id=content["uuid"], instance_type="character")

    def _generate_track(self):
        # track (track)
        print("tooltip generation: track")
        all_walker = []
        all_walker.append(self.walk_dir("track"))
        for generator in all_walker:
            for filename in generator:
                print(f"filename: {filename}", get_curr_time_printable())
                content = self.get_json(filename)

                # background itself
                tooltip_id = self.get_tooltip("track", content["instance_id"])
                self.add_render_result_by_lang("track", tooltip_id, "track",
                                               track=content, instance_id=content["instance_id"],
                                               instance_type="story")

                # track to background
                # output_usedby_background
                for data in content["used_by"]["data_background"].values():
                    data = data[0]

                    tooltip_id = self.get_tooltip("background", data["uuid"],
                                                  "track", content["instance_id"])
                    self.add_render_result_by_lang("background", tooltip_id, "track",
                                                   background=data, instance_id=content["instance_id"],
                                                   instance_type="track")

                # track to character
                # output_usedby_character_dict
                for data in content["used_by"]["data_character"].values():
                    data = data[0]

                    tooltip_id = self.get_tooltip("character", TemplateTool.get_character_instance_id(data),
                                                  "track", content["instance_id"])
                    self.add_render_result_by_lang("character", tooltip_id, "track",
                                                   char=data, instance_id=content["instance_id"], instance_type="track")

    def generate(self):
        self._generate_story()
        self._generate_album()
        self._generate_background()
        self._generate_character()
        self._generate_track()

        self.is_generated = True
        print("tooltip generation completed")

    def write(self):
        if not self.is_generated:
            raise RuntimeError

        print("start writing tooltip")
        shutil.rmtree(self.BASE_OUTPUT_PATH, ignore_errors=True)

        for type in self.data_types:
            print("writing tooltip", type)
            js_writer(f"data_zh_cn_{type}_{INIT_TIME}.js", self.data["zh_cn"][type], type)
            js_writer(f"data_en_{type}_{INIT_TIME}.js", self.data["en"][type], type)


def generate_tooltip(jinja_env):
    t = TooltipHtmlGenerator(jinja_env)
    t.generate()
    t.write()
