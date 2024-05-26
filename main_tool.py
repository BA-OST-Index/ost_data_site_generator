import time
import htmlmin
import os
import pickle
import urllib.parse
from random import choices as ran_choices
from collections import OrderedDict
from jinja2 import UndefinedError
from functools import lru_cache
from main_cache import GenerationCache

__all__ = ["TOOLTIP_ID", "TOOLTIP_ID_RATIONAL", "INIT_TIME",
           "JinjaTool", "TemplateTool", "get_curr_time_printable"]

TOOLTIP_ID = set()
TOOLTIP_CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
TOOLTIP_ID_RATIONAL = set()  # 有理编号的tooltip

STATIC_BASE_URL = "/static/"

INIT_TIME = int(time.time_ns())


def get_curr_time_printable() -> str:
    """精确到毫秒的后四位"""
    global INIT_TIME
    return f"{(time.time_ns() - INIT_TIME) / 1e+6:0.4f}ms ({(time.time_ns() - INIT_TIME) / 1e+9:0.4f}s)"


class JinjaTool:
    @staticmethod
    def get_current_utc():
        return time.time()

    @staticmethod
    def get_init_time():
        return INIT_TIME

    @staticmethod
    def generate_tooltip_id(*args):
        """args 以 先type后id 的方式传递"""

        def raise_exception(type: int = 2):
            if type == 1:
                raise ValueError(f"unknown data_type {args[0]}")
            elif type == 2:
                raise ValueError(args)

        if len(args) != 0:
            global TOOLTIP_ID_RATIONAL
            data_type = args[0]
            data_id = args[1]  # 全部都是 uuid (通用)，除了 npc=namespace[-1] (过于nt)

            if len(args) == 2:
                # track/background/character/album
                if data_type in ["track", "background", "character", "album"]:
                    id_1 = f"{data_type}-{data_id}-all"
                    TOOLTIP_ID_RATIONAL.add(id_1)
                    return id_1
                # story
                elif data_type in ["story"]:
                    id_1 = f"story-{data_id}-all"
                    TOOLTIP_ID_RATIONAL.add(id_1)
                    return id_1
                else:
                    raise_exception(1)
            elif len(args) == 3:
                if args[0] == "storypart":
                    id_1 = f"story-{args[1]}-part-{args[2]}"
                    TOOLTIP_ID_RATIONAL.add(id_1)
                    return id_1
                elif args[0] == "storypart_source":
                    id_1 = f"story-{args[1]}-source-{args[2]}"
                    TOOLTIP_ID_RATIONAL.add(id_1)
                    return id_1
                raise_exception(1)
            elif len(args) == 4:
                # data_type 取值如下：
                # bg, bg_direct, char, track
                first, second = (args[0], args[1]), (args[2], args[3])
                if first[0] > second[0]:
                    second_, first_ = first, second
                else:
                    second_, first_ = second, first

                if first_[0] == "background_direct":
                    id_1 = f"char-{second_[1]}-bg"
                    TOOLTIP_ID_RATIONAL.add(id_1)
                    return id_1
                # 针对 story -> track/character/background 情况
                elif first_[0] == "story":
                    return JinjaTool.generate_tooltip_id(*second_)
                elif second_[0] == "story":
                    return JinjaTool.generate_tooltip_id(*first_)
                # 针对 char -> background (direct)
                elif second_[0] == "character_bg_direct":
                    return JinjaTool.generate_tooltip_id(*first_)
                # 其它
                else:
                    id_1 = "-".join(first + second)
                    id_2 = "-".join(second + first)

                    # 检测tooltip id情况
                    if id_1 not in TOOLTIP_ID_RATIONAL:
                        # 如果第一个id不存在，检测第二个id
                        if id_2 not in TOOLTIP_ID_RATIONAL:
                            # 如果第二个id不存在，说明两个都不存在
                            # 即，是第一次创建这两数据的关系
                            # 返回第一个id
                            TOOLTIP_ID_RATIONAL.add(id_1)
                            return id_1
                        else:
                            # 否则，第二个id存在
                            # 第二个id，此时，也就是第一次创建关系时的id_1(这里是id_2)
                            return id_2
                    else:
                        # 谨防意外情况，虽然好像不该运行到这（？）
                        TOOLTIP_ID_RATIONAL.add(id_1)
                        return id_1
            else:
                raise ValueError(args)
        else:
            global TOOLTIP_ID
            while True:
                id = "".join(ran_choices(TOOLTIP_CHAR_SET, k=6))
                if id not in TOOLTIP_ID:
                    TOOLTIP_ID.add(id)
                    return id

    @staticmethod
    def js_string_safe(value):
        return (value.replace("&amp;", "&").
                replace("'", "\'").
                replace("[", "&#91;").
                replace("]", "&#93;"))

    @staticmethod
    def js_html_string_safe(value):
        return value.replace("\n", "\\n")

    @staticmethod
    def page_minify_html(value):
        return htmlmin.minify(value,
                              remove_empty_space=True,
                              remove_optional_attribute_quotes=False). \
            replace("'", "&#x27")

    @staticmethod
    @lru_cache
    def get_outer_json(instance_id: str, instance_type: str):
        def read_file(filepath):
            with open(os.path.join("exported_data", filepath), mode="rb") as file:
                return pickle.load(file)

        # track
        if instance_type == "track":
            instance_id = instance_id.split("_")
            track_type = instance_id[0]
            track_no = int(instance_id[1])

            if track_type == "OST":
                return read_file(f"track/ost/{track_no}.json")
            elif track_type == "other":
                return read_file(f"track/other/{track_no}.json")
            elif track_type == "animation":
                return read_file(f"track/animation/{track_no}.json")
            elif track_type == "short":
                return read_file(f"track/short/{track_no}.json")
        # background
        elif instance_type == "background":
            # instance_id = background filename
            return read_file(f"background/{instance_id}.json")
        elif instance_type == "character":
            # instance_id = character.uuid
            # 尝试student
            try:
                return read_file(f"character/student/{instance_id.lower()}/{instance_id.lower()}.json")
            except FileNotFoundError:
                return read_file(f"character/npc/{instance_id}/{instance_id}.json")
        elif instance_type == "album":
            return read_file(f"album/{instance_id}.json")

        raise ValueError(f"{instance_id}, {instance_type}")

    @staticmethod
    @lru_cache()
    def arg_check(arg, strict=False):
        """

        :param arg:
        :param strict: 严格模式，为True时只有未定义才会返回False
        :return:
        """
        # test if is undefined
        if hasattr(arg, "_undefined_exception"):
            exc = getattr(arg, "_undefined_exception")
            if exc is UndefinedError:
                return False

        if not strict:
            # other common cases
            if arg == "" or arg == 0 or arg == "False":
                return False

        return True

    @staticmethod
    def storypart_extract_all_data(part, key_name):
        temp = OrderedDict()
        for segment in part["data"]:
            for obj in segment[key_name]:
                if obj["uuid"] not in temp.keys():
                    temp[obj["uuid"]] = obj
        return [i for i in temp.values()]

    @staticmethod
    def storypart_extract_all_data_track(part):
        return JinjaTool.storypart_extract_all_data(part, "track")

    @staticmethod
    def storypart_extract_all_data_background(part):
        return JinjaTool.storypart_extract_all_data(part, "background")

    @staticmethod
    def storypart_extract_all_data_characters(part):
        return JinjaTool.storypart_extract_all_data(part, "character")

    @staticmethod
    def convert_story_into_single_part(story):
        ALL_KEY_NAME = ["background", "track", "character"]

        all_data_uuid = []
        all_data = {
            "character": [],
            "track": [],
            "background": []
        }

        if story["filetype_sub"] == 0:
            for part in story["part"]:
                for seg in part["data"]:
                    for key_name in ALL_KEY_NAME:
                        for entry in seg[key_name]:
                            if entry["uuid"] not in all_data_uuid:
                                all_data_uuid.append(entry["uuid"])
                                all_data[key_name].append(entry)
        elif story["filetype_sub"] == 1:
            for key_name in ALL_KEY_NAME:
                all_data[key_name] = list(story["part"]["all"][key_name].values())
        else:
            raise ValueError(story["filetype_sub"])

        return {"data": [all_data]}


    @staticmethod
    @lru_cache()
    def get_static(path):
        global STATIC_BASE_URL
        return urllib.parse.urljoin(STATIC_BASE_URL, path)


class TemplateTool:
    @staticmethod
    def get_character_instance_id(data: dict) -> str:
        if data.get("filetype", "") == 52 or data.get("student", "None") != "None":  # NPC
            return data["namespace"][-1]
        return data["uuid"]

    @staticmethod
    def get_character_data(data: dict):
        """tooltip_character 前半部分的 python 实现版"""
        if data.get("filetype", -1) == 52:
            # npc
            char_data = JinjaTool.get_outer_json(data["namespace"][-1], "character")
        else:
            try:
                char_data = JinjaTool.get_outer_json(data["uuid"], "character")
            except Exception:
                # for unknown case
                char_data = JinjaTool.get_outer_json(data["student"]["uuid"], "character")

        if char_data.get("filetype", -1) == 52:
            # npc
            char_info = char_data
            char_type = "npc"
            char_name = char_info["name"]
        else:
            # student
            char_info = char_data["student"]
            char_type = "stu"
            char_name = char_info["name"]["name"]

        outer_data = char_info["used_by"]

        return {"char_data": char_data, "char_info": char_info,
                "char_type": char_type, "char_name": char_name,
                "outer_data": outer_data}

    @staticmethod
    def py_generate_story_url(lang: str, story: dict):
        ft = story["filetype"]
        if ft in [14, 15]:
            return f"/{lang}/{'/'.join(story['namespace'])}.html"
        else:
            if ft == 11:
                story_type = "main"
            elif ft == 12:
                story_type = "side"
            elif ft == 13:
                story_type = "short"
            else:
                story_type = "other"

            return f"/{lang}/main/story/{'/'.join(story['namespace'][2:])}.html"

    @staticmethod
    def py_tooltip_background(background, instance_id, instance_type, extra_data):
        """返回一个 [[Story, [[Part, loop_index, seg_index, tooltip_id], ...]], ...]"""
        all_story = []

        # if instance_type == "story":
        #     cache_id = f"background-{background['uuid']}-story"
        #     if GenerationCache.check_for_cache("all", cache_id):
        #         return GenerationCache.get_from_cache("all", cache_id)

        for story in extra_data.values():
            story = story[0]
            story_parts = []

            if story["filetype_sub"] == 1:
                # auto generated story
                if instance_type == "story":
                    if background["filename"] in story["part"]["all"]["background"].keys():
                        all_story.append([story, []])
                elif instance_type == "character":
                    if background["filename"] in story["part"]["bg_to_char"].keys():
                        if instance_id in story["part"]["bg_to_char"][background["filename"]]:
                            all_story.append([story, []])
                elif instance_type == "track":
                    if background["filename"] in story["part"]["bg_to_track"].keys():
                        if instance_id in story["part"]["bg_to_track"][background["filename"]]:
                            all_story.append([story, []])
                continue

            for (index, part) in enumerate(story["part"], 1):
                add_part, seg_index = 0, -1
                is_by_comm, is_narrative = False, False

                for (index2, segment) in enumerate(part["data"], 1):
                    is_exit = 0
                    for bg in segment["background"]:
                        if bg["uuid"] == background["uuid"]:
                            # bg-char
                            for char in segment["character"]:
                                if TemplateTool.get_character_instance_id(char) == instance_id:
                                    if char["is_comm"]:
                                        is_by_comm = True
                                    if char["is_narrative"]:
                                        is_narrative = True

                            # 其它代码
                            if instance_type == "story" or instance_type == "character":
                                is_exit = 1
                                break
                            elif instance_type == "track":
                                for track in segment["track"]:
                                    if track["instance_id"] == instance_id:
                                        is_exit = 1
                                        break
                            if is_exit:
                                break
                    if is_exit:
                        seg_index = index2
                        break

                if seg_index != -1:
                    story_parts.append([part, index, seg_index, 0, is_by_comm, is_narrative])
            if len(story_parts) != 0:
                all_story.append([story, story_parts])

        # if instance_type == "story":
        #     GenerationCache.add_to_cache("all", cache_id, all_story)
        return all_story

    @staticmethod
    def py_tooltip_track(track, instance_id, instance_type, extra_data):
        all_story = []

        # if instance_type == "story":
        #     cache_id = f"track-{track['uuid']}-story"
        #     if GenerationCache.check_for_cache("all", cache_id):
        #         return GenerationCache.get_from_cache("all", cache_id)

        for story in extra_data["data_story"].values():
            story = story[0]
            related_parts = []

            if story["filetype_sub"] == 1:
                # auto generated story
                if instance_type == "story":
                    if track["instance_id"] in story["part"]["all"]["track"].keys():
                        all_story.append([story, []])
                elif instance_type == "character":
                    if track["instance_id"] in story["part"]["track_to_char"].keys():
                        if instance_id in story["part"]["track_to_char"][track["instance_id"]]:
                            all_story.append([story, []])
                elif instance_type == "background":
                    if track["instance_id"] in story["part"]["track_to_bg"].keys():
                        if instance_id in story["part"]["track_to_bg"][track["instance_id"]]:
                            all_story.append([story, []])
                continue

            for (index, part) in enumerate(story["part"], 1):
                seg_index = -1
                is_by_comm, is_narrative = False, False

                for (index2, segment) in enumerate(part["data"], 1):
                    is_exit = 0
                    for story_track in segment["track"]:
                        # print(story_track)
                        if story_track["instance_id"] == track["instance_id"]:
                            if instance_type == "story" or instance_type == "album":
                                is_exit = 1
                                break
                            elif instance_type == "character":
                                for char in segment["character"]:
                                    # bg-char
                                    if char["is_comm"]:
                                        is_by_comm = True
                                    if char["is_narrative"]:
                                        is_narrative = True

                                    if TemplateTool.get_character_instance_id(char) == instance_id:
                                        is_exit = 1
                                        break
                            elif instance_type == "background":
                                for bg in segment["background"]:
                                    if bg["uuid"] == instance_id:
                                        is_exit = 1
                                        break

                        if is_exit:
                            break
                    if is_exit:
                        seg_index = index2
                        break

                if seg_index != -1:
                    related_parts.append([part, index, seg_index, 0, is_by_comm, is_narrative])

            if len(related_parts) != 0:
                all_story.append([story, related_parts])

        # if instance_type == "story":
        #     GenerationCache.add_to_cache("all", cache_id, all_story)

        return all_story

    @staticmethod
    def py_tooltip_character(character, instance_id, instance_type, extra_data):
        """注意，此处的 extra_data 是 loop_data.data"""
        if extra_data["filetype"] == 52:
            char_data = extra_data
            char_type = "npc"
        else:
            char_data = extra_data["student"]
            char_type = "stu"
        outer_data = char_data["used_by"]
        character_id = TemplateTool.get_character_instance_id(character)

        # if instance_type == "story":
        #     cache_id = f"character-{char_data['uuid']}-story"
        #     if GenerationCache.check_for_cache("all", cache_id):
        #         return GenerationCache.get_from_cache("all", cache_id)

        all_story = []
        for story in outer_data["data_story"].values():
            story = story[0]
            related_parts = []

            if story["filetype_sub"] == 1:
                # auto generated story
                if instance_type == "story":
                    if character_id in story["part"]["all"]["character"].keys():
                        all_story.append([story, []])
                elif instance_type == "character":
                    if character_id in story["part"]["char_to_char"].keys():
                        if instance_id in story["part"]["char_to_char"][character_id]:
                            all_story.append([story, []])
                elif instance_type == "track":
                    if character_id in story["part"]["char_to_track"].keys():
                        if instance_id in story["part"]["char_to_track"][character_id]:
                            all_story.append([story, []])
                elif instance_type == "background":
                    if character_id in story["part"]["char_to_bg"].keys():
                        if instance_id in story["part"]["char_to_bg"][character_id]:
                            all_story.append([story, []])
                continue

            for (index, part) in enumerate(story["part"], 1):
                seg_index = -1
                is_by_comm, is_narrative = False, False

                # 针对 char-char (in-story) 设计，这部分只精确到part
                if instance_type == "character":
                    is_exit = 0
                    for char2 in JinjaTool.storypart_extract_all_data_characters(part):
                        # 探测对方（传入的 character 变量）在不在里面
                        if TemplateTool.get_character_instance_id(char2) == character_id:
                            # 探测 character 自己在不在起头
                            for char3 in JinjaTool.storypart_extract_all_data_characters(part):
                                if TemplateTool.get_character_instance_id(char3) == instance_id:
                                    if char2["is_comm"]:
                                        is_by_comm = True
                                    if char2["is_narrative"]:
                                        is_narrative = True

                                    is_exit = 1
                                    break

                                if is_exit == 1:
                                    break

                            if is_exit == 1:
                                break
                    if is_exit == 1:
                        related_parts.append([part, index, seg_index, 0, is_by_comm, is_narrative])

                    # 直接跳过剩下循环
                    continue

                # 其它数据
                for (index2, segment) in enumerate(part["data"], 1):
                    is_exit = 0
                    for char in segment["character"]:
                        if char["uuid"] == char_data["uuid"]:
                            if char["is_comm"]:
                                is_by_comm = True
                            if char["is_narrative"]:
                                is_narrative = True

                            if instance_type == "track":
                                for track in segment["track"]:
                                    if track["instance_id"] == instance_id:
                                        is_exit = 1
                                        break
                                if is_exit == 1:
                                    break
                            elif instance_type == "background":
                                for bg in segment["background"]:
                                    if bg["uuid"] == instance_id:
                                        is_exit = 1
                                        break
                                if is_exit == 1:
                                    break
                            else:
                                is_exit = 1
                                break


                    if is_exit:
                        seg_index = index2

                if seg_index != -1:
                    related_parts.append([part, index, seg_index, 0, is_by_comm, is_narrative])

            if len(related_parts) != 0:
                all_story.append([story, related_parts])

        # if instance_type == "story":
        #     GenerationCache.add_to_cache("all", cache_id, all_story)
        return all_story

    @staticmethod
    def py_output_usedby_story(data_story: dict, instance_uuid, instance_key):
        # cache_id = f"{instance_key}-{instance_uuid}-story"

        all_story_with_filetype = OrderedDict()
        _curr_filetype = 0

        for key, value in data_story.items():
            # 区分不同 filetype 故事
            if _curr_filetype == 0:
                _curr_filetype = value[0]["filetype"]
                all_story_with_filetype[_curr_filetype] = []
            else:
                if _curr_filetype != value[0]["filetype"]:
                    _curr_filetype = value[0]["filetype"]
                    all_story_with_filetype[_curr_filetype] = []

            value = value[0]

            if value["filetype_sub"] == 1:
                all_story_with_filetype[_curr_filetype].append([value, []])
                continue

            # appearedAt snippet
            if instance_uuid:
                related_parts = []

                for (index, part) in enumerate(value["part"], 1):
                    seg_index = -1
                    is_by_comm, is_narrative = False, False  # bg-char

                    for (index2, segment) in enumerate(part["data"], 1):
                        is_exit = 0
                        for obj in segment[instance_key]:
                            if obj["uuid"] == instance_uuid:
                                # bg-char
                                if instance_key == "character":
                                    if obj["is_comm"]:
                                        is_by_comm = True
                                    if obj["is_narrative"]:
                                        is_narrative = True

                                is_exit = 1

                        if is_exit:
                            seg_index = index2

                    if seg_index != -1:
                        related_parts.append(
                            [part, index, seg_index,
                             JinjaTool.generate_tooltip_id("storypart", value["instance_id"], index),
                             is_by_comm, is_narrative])

                if len(related_parts) != 0:
                    all_story_with_filetype[_curr_filetype].append([value, related_parts])

        # GenerationCache.add_to_cache("all", cache_id, [story for (i, j) in all_story_with_filetype.items() for story in j])
        return all_story_with_filetype
