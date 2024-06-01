import pickle
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
ALL_TEST_FILES = [["album/01.json"],  # album.html
                  ["album/_all.json"],  # album_all.html

                  ["background/BG_CS_Abydos_04.jpg.json"],  # background.html
                  ["background/_all.json"],  # background_all.html

                  ["main/battle/main/3/NA0.json", "main/battle/main/3/H10.json", "main/battle/main/3/N10.json"],  # battle.html
                  ["main/battle/main/3/_all.json"],  # battle_all.html

                  ["character/_all.json", "character/npc/_all.json"],  # character_all.html
                  ["character/npc/ArisKey/ArisKey.json"],  # npc.html
                  ["character/student/yuuka/yuuka.json"],  # student.html

                  ["event/_all.json"],  # event_all.html
                  ["event/810/battle/_all.json"],  # event_battle_all.html
                  ["event/818/story/_all.json"],  # event_story_all.html
                  ["event/812/ui/_all.json"],  # event_ui_all.html

                  ["main/story/main/2/2/23.json", "event/818/story/01.json"],  # story.html
                  ["main/story/main/2/2/_all.json", "event/818/story/_all.json"],  # story_all.html

                  ["tag/bright.json"],  # tag.html
                  ["tag/_all.json"],  # tag_all.html

                  ["track/ost/7.json", "track/ost/1.json"],  # track.html
                  ["track/ost/_all.json"],  # track_all.html

                  ["ui/1.json", "event/812/ui/1.json"],  # ui.html
                  ["ui/_all.json"],  # ui_all.html

                  ["video/1.json"],  # video.html
                  ["video/_all.json"]  # video_all.html
]
TEST_FILE_BASEPATH = "exported_data/"
ALL_LANGS = ["en", "zh_cn"]


def _load_json(filepath):
    with open(os.path.join(TEST_FILE_BASEPATH, filepath), "rb") as f:
        return pickle.load(f)


def check_template(jinja_env, return_template):
    total = len(ALL_LANGS) * sum([len(i) for i in ALL_TEST_FILES])
    failed_count = 0

    for lang in ALL_LANGS:
        for (template_name, json_filepaths) in zip(ALL_TEMPLATE_NAMES, ALL_TEST_FILES):
            for json_filepath in json_filepaths:
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
