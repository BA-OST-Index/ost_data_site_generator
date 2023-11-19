import time
import htmlmin
import os
import json
import urllib.parse
from random import choices as ran_choices
from collections import OrderedDict
from jinja2 import UndefinedError
from functools import lru_cache
from main_cache import GenerationCache

TOOLTIP_ID = set()
TOOLTIP_CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"

STATIC_BASE_URL = "/static/"


class JinjaTool:
    @staticmethod
    def get_current_utc():
        return time.time()

    @staticmethod
    def generate_tooltip_id():
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
    def get_outer_json(instance_id: str, instance_type: str):
        def read_file(filepath):
            with open(os.path.join("exported_data", filepath), mode="r", encoding="UTF-8") as file:
                return json.load(file)

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
    def arg_check(arg):
        # test if is undefined
        if hasattr(arg, "_undefined_exception"):
            exc = getattr(arg, "_undefined_exception")
            if exc is UndefinedError:
                return False
        # other common cases
        if arg == "" or arg == 0 or arg == "False":
            return False

        return True

    @staticmethod
    def storypart_extract_all_data(parts, key_name):
        temp = OrderedDict()
        for segment in parts["data"]:
            for obj in segment[key_name]:
                if obj["uuid"] not in temp.keys():
                    temp[obj["uuid"]] = obj
        return [i for i in temp.values()]

    @staticmethod
    def storypart_extract_all_data_track(parts):
        return JinjaTool.storypart_extract_all_data(parts, "track")

    @staticmethod
    def storypart_extract_all_data_background(parts):
        return JinjaTool.storypart_extract_all_data(parts, "background")

    @staticmethod
    def storypart_extract_all_data_characters(parts):
        return JinjaTool.storypart_extract_all_data(parts, "character")

    @staticmethod
    @lru_cache()
    def get_static(path):
        global STATIC_BASE_URL
        return urllib.parse.urljoin(STATIC_BASE_URL, path)


class TemplateTool:
    @staticmethod
    def py_generate_story_url(lang: str, story: dict):
        ft = story["filetype"]
        if ft == 15:
            return f"/{lang}/character/student/{story['pos']['student'].lower()}/bond/{str(story['pos']['no'])}.html"
        elif ft == 14:
            return f"/{lang}/event/{str(story['pos']['event_id'])}/story/{str(story['pos']['segment'])}.html"
        else:
            if ft == 11:
                story_type = "main"
            elif ft == 12:
                story_type = "side"
            elif ft == 13:
                story_type = "short"
            else:
                story_type = "other"

            return f"/{lang}/main/story/{story_type}/{str(story['pos']['volume'])}/{str(story['pos']['chapter'])}/" \
                   f"{str(story['pos']['segment'])}.html"

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

            for (index, part) in enumerate(story["part"], 1):
                add_part, seg_index = 0, -1
                for (index2, segment) in enumerate(part["data"], 1):
                    is_exit = 0
                    for bg in segment["background"]:
                        if bg["uuid"] == background["uuid"]:
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
                    story_parts.append([part, index, seg_index, 0])
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

            for (index, part) in enumerate(story["part"], 1):
                seg_index = -1
                for (index2, segment) in enumerate(part["data"], 1):
                    is_exit = 0
                    for story_track in segment["track"]:
                        if story_track["instance_id"] == track["instance_id"]:
                            if instance_type == "story" or instance_type == "album":
                                is_exit = 1
                                break
                            elif instance_type == "character":
                                for char in segment["character"]:
                                    if char.get("filetype", "") == 52:  # NPC
                                        if char["namespace"][-1] == instance_id:
                                            is_exit = 1
                                            break
                                    else:
                                        if char["uuid"] == instance_id:
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
                    related_parts.append([part, index, seg_index, 0])

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

        # if instance_type == "story":
        #     cache_id = f"character-{char_data['uuid']}-story"
        #     if GenerationCache.check_for_cache("all", cache_id):
        #         return GenerationCache.get_from_cache("all", cache_id)

        all_story = []
        for story in outer_data["data_story"].values():
            story = story[0]
            related_parts = []
            for (index, part) in enumerate(story["part"], 1):
                seg_index = -1
                for (index2, segment) in enumerate(part["data"], 1):
                    is_exit = 0
                    for char in segment["character"]:
                        if char["uuid"] == char_data["uuid"]:
                            if instance_type == "character":
                                for char2 in segment["character"]:
                                    if char2["uuid"] == instance_id:
                                        is_exit = 1
                                        break
                                if is_exit == 1:
                                    break
                            elif instance_type == "track":
                                for track in segment["track"]:
                                    if track["instance_id"] == instance_id:
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
                    related_parts.append([part, index, seg_index, 0])

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

            # appearedAt snippet
            if instance_uuid:
                related_parts = []

                for (index, part) in enumerate(value["part"], 1):
                    seg_index = -1
                    for (index2, segment) in enumerate(part["data"], 1):
                        is_exit = 0
                        for obj in segment[instance_key]:
                            if obj["uuid"] == instance_uuid:
                                is_exit = 1

                        if is_exit:
                            seg_index = index2

                    if seg_index != -1:
                        related_parts.append([part, index, seg_index, JinjaTool.generate_tooltip_id()])

                if len(related_parts) != 0:
                    all_story_with_filetype[_curr_filetype].append([value, related_parts])

        # GenerationCache.add_to_cache("all", cache_id, [story for (i, j) in all_story_with_filetype.items() for story in j])
        return all_story_with_filetype
