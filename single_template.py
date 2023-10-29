import json
import os
import urllib.parse
import webbrowser
from jinja2 import Environment, FileSystemLoader
from main_tool import JinjaTool

environment = Environment(loader=FileSystemLoader(os.path.split(__file__)[0]), extensions=["jinja2.ext.loopcontrols",
                                                                                           "jinja2.ext.do"])
environment.filters["js_string_safe"] = JinjaTool.js_string_safe
environment.filters["js_html_string_safe"] = JinjaTool.js_html_string_safe
environment.filters["is_list"] = lambda obj: isinstance(obj, list)
environment.filters["page_minify_html"] = JinjaTool.page_minify_html
environment.globals["get_current_utc"] = JinjaTool.get_current_utc
environment.globals["generate_tooltip_id"] = JinjaTool.generate_tooltip_id
environment.globals["get_outer_json"] = JinjaTool.get_outer_json
environment.globals["arg_check"] = JinjaTool.arg_check
environment.globals["urljoin"] = urllib.parse.urljoin

path = "test.txt"
name = "test.html"
data_path = "exported_data/main/story/main/1/1/02.json"

with open(data_path, mode="r", encoding="UTF-8") as file:
    data = json.load(file)

template = environment.get_template(path)
result = template.render(is_static="", story=data)
os.makedirs(os.path.split(os.path.join("data_html/", name))[0], exist_ok=True)
with open(os.path.join("data_html/", name), mode="w", encoding="UTF-8") as file:
    file.write(result)

webbrowser.open("http://localhost:9000/" + name)
