from _main import *
from _main_config import *
from main_tool_2 import generate_tooltip

ALL_FOLDERS = ["character"]

delete_old_page()

env = get_jinja_env()
generate_tooltip(env)

copy_static_file(True)
for i in ALL_FOLDERS:
    generate_page_per_lang(ALL_LANGS, env, ["exported_data", i])
generate_other_per_lang(ALL_LANGS, env, LANG_OTHER_PAGE)
generate_static_page(env, OTHER_STATIC_PAGE)

start_server(9000)
