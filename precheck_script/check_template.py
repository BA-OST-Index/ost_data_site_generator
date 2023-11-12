import json
import os
import time

ALL_TEMPLATE_NAMES = ["album.html", "album_all.html",
                      "background.html", "background_all.html",
                      "battle.html", "battle_all.html",
                      "character_all.html", "npc.html", "student.html",
                      "event_all.html", "event_battle_all.html", "event_story_all.html", "event_ui_all.html",
                      "story.html", "story_all.html",
                      "tag.html", "tag_all.html",
                      "track.html", "track_all.html",
                      "ui.html", "ui_all.html",
                      "video.html", "video_all.html"]
ALL_TEST_FILES = ["album/01.json", "album/_all.json",
                  "background/BG_CS_Abydos_04.jpg.json", "background/_all.json",
                  "main/battle/main/3/NA0.json", "main/battle/main/3/_all.json",
                  "character/_all.json", "character/npc/ArisKey/ArisKey.json", "character/student/yuuka/yuuka.json",
                  "event/_all.json", "event/810/battle/_all.json", "event/818/story/_all.json",
                  "event/812/ui/_all.json",
                  "main/story/main/2/2/25.json", "main/story/main/2/2/_all.json",
                  "tag/bright.json", "tag/_all.json",
                  "track/ost/7.json", "track/ost/_all.json",
                  "ui/1.json", "ui/_all.json",
                  "video/1.json", "video/_all.json"]
TEST_FILE_BASEPATH = "exported_data/"
ALL_LANGS = ["en", "zh_cn"]


def _load_json(filepath):
    with open(os.path.join(TEST_FILE_BASEPATH, filepath), "r", encoding="utf-8") as f:
        return json.load(f)


def check_template(jinja_env, return_template):
    total = len(ALL_LANGS) * len(ALL_TEMPLATE_NAMES)
    failed_count = 0

    for lang in ALL_LANGS:
        for (template_name, json_filepath) in zip(ALL_TEMPLATE_NAMES, ALL_TEST_FILES):
            template = jinja_env.get_template(f"page/{lang}/{template_name}")

            print(f"[INFO]\tTesting {lang}/{template_name} with {json_filepath}...")
            try:
                start = time.time_ns()
                return_template(template_name, template, _load_json(json_filepath))
                end = time.time_ns()
            except Exception as e:
                print(f"[FAIL]\tFailed with exception: {str(e)}")
                failed_count += 1
            else:
                print(f"[OK]\tSuccessfully tested (runtime {(end - start) / 1e6} ms)")

    print(f"Total {total}, failed {failed_count} ({failed_count / total * 100:0.2f}%)")
    if failed_count != 0:
        raise AssertionError
