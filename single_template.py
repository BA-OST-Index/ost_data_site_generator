import pickle
import os
import time
import webbrowser
from _main import *

environment = get_jinja_env()

"""
path = "page/en/album.html"
name = "en/album/01.html"
data_path = "exported_data/album/01.json"

path = "page/en/track.html"
name = "en/track/ost/16.html"
data_path = "exported_data/track/ost/16.json"
"""
'''
path = "page/zh_cn/character_all.html"
name = "zh_cn/character/student/hoshino/index.html"
data_path = "exported_data/character/_all.json"
'''
'''
path = "page/en/background.html"
name = "en/background/BG_CS_Abydos_01.jpg.html"
data_path = "exported_data/background/BG_CS_Abydos_01.jpg.json"
'''
'''
path = "page/zh_cn/tag.html"
name = "zh_cn/tag/sad.html"
data_path = "exported_data/tag/sad.json"
'''
'''
path = "page/zh_cn/track_all.html"
name = "zh_cn/track/ost/index.html"
data_path = "exported_data/track/ost/_all.json"
'''
'''
path = "page/zh_cn/story.html"
name = "en/main/story/main/2/2/25.html"
data_path = "exported_data/character/student/mika/bond/01.json"
'''
'''
path = "page/zh_cn/student.html"
name = "zh_cn/character/student/hoshino/index.html"
data_path = "exported_data/character/student/ui/ui.json"
'''
'''
path = "page/zh_cn/npc.html"
name = "zh_cn/character/student/hoshino/index.html"
data_path = "exported_data/character/npc/Sora/Sora.json"
'''
'''
path = "page/en/composer.html"
name = "en/composer/1.html"
data_path = "exported_data/composer/1.json"
'''
'''
path = "page/zh_cn/event_story_all.html"
name = "en/main/story/main/2/2/25.html"
data_path = "exported_data/event/810/story/_all.json"
'''
'''
path = "page/en/ui.html"
name = "en/ui/1.html"
# data_path = "exported_data/ui/1.json"
data_path = "exported_data/event/812/ui/1.json"
'''

with open(data_path, mode="rb") as file:
    data = pickle.load(file)

template = environment.get_template(path)
st = time.time_ns()
result = template.render(is_static="", ui=data)
print((time.time_ns() - st) / 1e+6)

os.makedirs(os.path.split(os.path.join("data_html/", name))[0], exist_ok=True)
with open(os.path.join("data_html/", name), mode="w", encoding="UTF-8") as file:
    file.write(result)

webbrowser.open("http://localhost:9000/" + name)
