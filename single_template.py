import json
import os
import time
import webbrowser
from _main import *

environment = get_jinja_env()


path = "page/en/album.html"
name = "en/album/01.html"
data_path = "exported_data/album/01.json"

path = "page/en/track.html"
name = "en/track/ost/16.html"
data_path = "exported_data/track/ost/16.json"

'''
path = "page/en/npc.html"
name = "en/character/npc/ariskey/index.html"
data_path = "exported_data/character/npc/ArisKey/ArisKey.json"
'''
'''
path = "page/en/background.html"
name = "en/background/BG_AronaRoom_In.jpg.html"
data_path = "exported_data/background/BG_AronaRoom_In.jpg.json"
'''

with open(data_path, mode="r", encoding="UTF-8") as file:
    data = json.load(file)

template = environment.get_template(path)
st = time.time_ns()
result = template.render(is_static="", track=data)
print((time.time_ns() - st) / 1e+6)

os.makedirs(os.path.split(os.path.join("data_html/", name))[0], exist_ok=True)
with open(os.path.join("data_html/", name), mode="w", encoding="UTF-8") as file:
    file.write(result)

webbrowser.open("http://localhost:9000/" + name)
